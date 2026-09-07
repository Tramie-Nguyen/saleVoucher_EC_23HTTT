import os
import csv
import time
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from hsdn import BASE_DIR


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
BASE_URL = "https://www.lifelink.vn"
PATH_DANH_MUC = os.path.join(BASE_DIR, "export_files", "danh_muc_rows.csv")

# Tạo 1 session dùng chung cho toàn bộ script, có retry tự động
session = requests.Session()
session.headers.update(HEADERS)

retry_strategy = Retry(
    total=5,                    # thử lại tối đa 5 lần
    backoff_factor=2,           # 2s, 4s, 8s, 16s, 32s giữa các lần thử
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)


def get_soup(url, max_manual_retries=3):
    """Tải và parse HTML từ URL, có retry thủ công cho lỗi timeout/connection."""
    for attempt in range(1, max_manual_retries + 1):
        try:
            resp = session.get(url, timeout=30)  # tăng timeout 15 -> 30
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            print(f"  ⚠️ Lỗi khi tải trang {url} (lần {attempt}/{max_manual_retries}): {e}")
            if attempt < max_manual_retries:
                time.sleep(5 * attempt)  # nghỉ tăng dần: 5s, 10s
            else:
                print(f"  ❌ Bỏ qua URL sau {max_manual_retries} lần thử: {url}")
                return None
    return None

def clean_price(price_str):
    """Chuyển chuỗi '100.000 đ' thành số nguyên 100000."""
    if not price_str:
        return 0
    digits = re.sub(r"\D", "", price_str)
    return int(digits) if digits else 0

def normalize_text(s):
    """
    Chuẩn hoá chuỗi để so sánh/khử trùng: lowercase, gộp khoảng trắng,
    bỏ dấu câu hay gây lệch so khớp. Giữ nguyên dấu tiếng Việt vì địa chỉ
    khác dấu (vd 'Đa Kao' vs 'Đà Kao') nên được coi là khác nhau.
    """
    if not s:
        return ""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)          # gộp khoảng trắng thừa
    s = re.sub(r"[.,;:\-–—]", "", s)    # bỏ dấu câu hay gây lệch so khớp
    return s.strip()


def voucher_identity(voucher_row):
    """Tạo khóa duy nhất để phát hiện voucher trùng theo tên voucher + tên DN."""
    ten_voucher = normalize_text(voucher_row.get("ten_voucher"))
    ten_dn = normalize_text(voucher_row.get("ten_dn"))
    return (ten_voucher, ten_dn)


def voucher_location_identity(map_row):
    """Tạo khóa duy nhất cho mapping voucher-chi nhánh theo tên voucher + tên DN + địa chỉ."""
    ten_voucher = normalize_text(map_row.get("ten_voucher"))
    ten_dn = normalize_text(map_row.get("ten_dn"))
    dia_chi = normalize_text(map_row.get("dia_chi_chi_nhanh"))
    return (ten_voucher, ten_dn, dia_chi)

# ==========================================
# 2. CRAWLER FUNCTIONS (Cào dữ liệu) — giữ nguyên logic gốc
# ==========================================

def extract_enterprises_from_category(category_endpoint, max_pages=1):
    """Trích xuất danh sách Doanh nghiệp duy nhất (trong phạm vi 1 danh mục) + link trang brand."""
    category_url = urljoin(BASE_URL, f"/e-voucher/{category_endpoint}")
    enterprises = {}

    for page in range(1, max_pages + 1):
        url = f"{category_url}?cp={page}"
        print(f"Đang quét Doanh nghiệp tại: {url}")
        soup = get_soup(url)
        if not soup:
            break

        items = soup.select("div.product-box")
        if not items:
            print("Không tìm thấy item nào nữa. Dừng phân trang.")
            break

        for item in items:
            brand_tag = item.select_one(".name-seller-item")
            logo_tag = item.select_one("img")

            a_tags = item.select("a")
            a_tag = a_tags[1]
            a_href = a_tag["href"] if a_tag else None
            brand_link = urljoin(BASE_URL, a_href) if a_href else None

            logo_url = logo_tag.get("src") if logo_tag else None

            if brand_tag:
                ten_dn = brand_tag.get_text(strip=True)
            else:
                continue  # không có tên DN thì bỏ qua item này, tránh lỗi biến chưa gán

            enterprises[ten_dn] = {
                "ten_dn": ten_dn,
                "logo": logo_url,
                "ngay_tao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "trang_thai": "Dang hoat dong",
                "brand_link": brand_link,  # dùng nội bộ để cào chi nhánh + dedupe, không đưa vào CSV hosodn
            }

        time.sleep(1)

    return list(enterprises.values())

def extract_branches_from_detail(brand_url, ten_dn=""):
    """
    Vào trang chi tiết thương hiệu để lấy TOÀN BỘ danh sách Chi nhánh.

    Ưu tiên lấy dữ liệu trong popup "Xem tất cả địa chỉ" (#PopupAcceptance), vì phần
    .group-loc hiển thị mặc định trên trang có thể bị giới hạn, chỉ đầy đủ khi bấm
    "Xem tất cả". Popup này đã có sẵn trong HTML trả về (chỉ bị ẩn bằng CSS), nên
    requests + BeautifulSoup vẫn đọc được, không cần click/chạy JS.
    """
    if not brand_url:
        return [], ten_dn

    soup = get_soup(brand_url)
    if not soup:
        return [], ten_dn

    seller_name_tag = soup.select_one(".seller-name")
    ten_dn_full = seller_name_tag.get_text(strip=True) if seller_name_tag else ten_dn

    branches = []

    group_loc = soup.select_one("#PopupAcceptance .group-loc") or soup.select_one(".group-loc")

    if not group_loc:
        return branches, ten_dn_full

    # Duyệt theo từng .loc-name rồi lấy .lst-address là sibling NGAY SAU nó.
    # Không cần quan tâm .loc-name/.lst-address có bị bọc thêm 1 lớp trung gian
    # (vd .lst-acc-map trong popup) hay không, vì find_next_sibling tự bỏ qua chuyện đó
    # miễn 2 thẻ cùng nằm chung 1 cha.
    idx = 0
    for loc_tag in group_loc.find_all("div", class_="loc-name"):
        current_khu_vuc = loc_tag.get_text(strip=True)
        addr_container = loc_tag.find_next_sibling("div", class_="lst-address")
        if not addr_container:
            continue

        address_tags = addr_container.select(".address-point")
        for dia_chi_tag in address_tags:
            ten_cn_tag = dia_chi_tag.find_previous_sibling(class_="point-name")
            dia_chi = dia_chi_tag.get_text(strip=True) if dia_chi_tag else None

            idx += 1
            default_cn_name = f"Chi nhánh {idx}" 
            ten_cn = ten_cn_tag.get_text(strip=True) if ten_cn_tag else default_cn_name

            if dia_chi or ten_cn:
                branches.append({
                    "ten_dn": ten_dn_full,
                    "ten_chi_nhanh": ten_cn,
                    "dia_chi": dia_chi,
                    "trang_thai": "Dang hoat dong",
                    "khu_vuc": current_khu_vuc,
                })

    return branches, ten_dn_full

def crawl_all_branches(data_dn, delay=1.0):
    """
    Lặp qua danh sách doanh nghiệp (có brand_link) để lấy toàn bộ chi nhánh.
    Đồng thời CẬP NHẬT LẠI (in-place) ten_dn trong từng phần tử data_dn bằng tên đầy đủ
    (.seller-name) lấy được từ trang chi tiết thương hiệu.
    """
    all_branches = []
    total = len(data_dn)

    for i, dn in enumerate(data_dn, 1):
        ten_dn = dn.get("ten_dn")
        brand_link = dn.get("brand_link")
        print(f"[{i}/{total}] Đang cào chi nhánh của: {ten_dn}")

        if not brand_link:
            print(f"  ⚠️ Không có brand_link cho '{ten_dn}', bỏ qua.")
            continue

        branches, ten_dn_full = extract_branches_from_detail(brand_link, ten_dn=ten_dn)

        if ten_dn_full:
            dn["ten_dn"] = ten_dn_full

        if not branches:
            print(f"  ⚠️ Không tìm thấy chi nhánh nào cho '{ten_dn}'.")
        all_branches.extend(branches)

        time.sleep(delay)

    return all_branches

def extract_voucher_prices_from_category(category_endpoint, max_pages=1):
    """
    Cào GIÁ + ẢNH + URL chi tiết của voucher trong danh mục.
    Tên DN/tên voucher đầy đủ được lấy ở trang chi tiết, xem extract_voucher_detail().
    """
    category_url = urljoin(BASE_URL, f"/e-voucher/{category_endpoint}")
    results = []
    url_chi_tiet = []

    for page in range(1, max_pages + 1):
        url = f"{category_url}?cp={page}"
        print(url)
        print(f"Đang cào trang danh mục voucher: {url}")
        soup = get_soup(url)
        if not soup:
            break

        items = soup.select("div.product-box")
        if not items:
            print("Không tìm thấy thẻ item nào nữa. Dừng phân trang.")
            break

        for item in items:
            price_tag = item.select_one(".sale-price")
            old_price_tag = item.select_one(".original-price")
            img_tag = item.select_one("img")
            image = img_tag.get("src") if img_tag else None

            link_tag = item.select_one("a")
            rel_url = link_tag["href"] if (link_tag and "href" in link_tag.attrs) else None

            if rel_url:
                raw_old = old_price_tag.get_text(strip=True) if old_price_tag else None
                raw_sale = price_tag.get_text(strip=True) if price_tag else None

                gia_goc = clean_price(raw_old)
                gia_ban = clean_price(raw_sale)
                if gia_goc == 0:
                    gia_goc = gia_ban

                results.append({
                    "gia_goc": gia_goc,
                    "gia_tri_giam": gia_ban,
                    "hinh_anh_url": image,
                })
                url_chi_tiet.append(urljoin(BASE_URL, rel_url))

        time.sleep(1)
    return [results, url_chi_tiet]

def extract_voucher_detail(product_url):
    """Vào trang chi tiết voucher để lấy: tên DN, tên voucher, điều kiện, mô tả, các địa điểm áp dụng."""
    soup = get_soup(product_url)

    if not soup:
        return {
            "detail": {"ten_dn": None, "ten_voucher": None, "dieu_kien_ap_dung": None, "mo_ta": None},
            "map_rows": []
        }
    partner_tag = soup.select_one(".b-name")
    voucher_tag = soup.select_one("h1.deal-title")
    condition = soup.select_one("#showFullTerms") or soup.select_one(".raw-content-rg #showFullTerms")
    description = soup.select_one("#showFullGenInfo") or soup.select_one(".raw-content-rg #showFullGenInfo")
    detail_data = {
        "ten_dn": partner_tag.get_text(strip=True) if partner_tag else None,
        "ten_voucher": voucher_tag.get_text(strip=True) if voucher_tag else None,
        "dieu_kien_ap_dung": condition.get_text(separator="\n", strip=True) if condition else None,
        "mo_ta": description.get_text(separator="\n", strip=True) if description else None
    }

    map_rows = []
    address_tags = soup.select("span.span-icon-loc")

    for tag in address_tags:
        address_text = tag.get_text(strip=True) if tag else None
        voucher_text = voucher_tag.get_text(strip=True) if voucher_tag else None
        partner_text = partner_tag.get_text(strip=True) if partner_tag else None
        if address_text:
            map_rows.append({
                "ten_voucher": voucher_text,
                "ten_dn": partner_text,
                "dia_chi_chi_nhanh": address_text
            })

    return {
        "detail": detail_data,
        "map_rows": map_rows
    }

def merge_branches_with_voucher_locations(all_chinhanh, all_voucher_cn):
    merged = list(all_chinhanh)

    # Tập khóa đã tồn tại từ trang DN (chuẩn hóa tên DN + địa chỉ)
    seen_keys = {
        (normalize_text(cn.get("ten_dn")), normalize_text(cn.get("dia_chi")))
        for cn in all_chinhanh
    }

    # Dict theo dõi idx riêng cho từng Doanh nghiệp
    # key: ten_dn_normalized, value: số lượng chi nhánh đã thêm từ voucher
    dn_idx_tracker = {}
    total_added = 0

    for row in all_voucher_cn:
        ten_dn = row.get("ten_dn")
        dia_chi = row.get("dia_chi_chi_nhanh")
        if not dia_chi or not ten_dn:
            continue

        dn_key = normalize_text(ten_dn)
        full_key = (dn_key, normalize_text(dia_chi))

        # Nếu cặp (DN, Địa chỉ) này đã có trong danh sách thì bỏ qua
        if full_key in seen_keys:
            continue

        # Đánh dấu đã xử lý
        seen_keys.add(full_key)

        # Khởi tạo hoặc tăng idx riêng cho doanh nghiệp này
        dn_idx_tracker[dn_key] = dn_idx_tracker.get(dn_key, 0) + 1
        current_idx = dn_idx_tracker[dn_key]

        # Định dạng tên chi nhánh: Tên doanh nghiệp - Chi nhánh {idx}
        ten_cn = f"{ten_dn} - Chi nhánh {current_idx}"

        merged.append({
            "ten_dn": ten_dn,
            "ten_chi_nhanh": ten_cn,
            "dia_chi": dia_chi,
            "trang_thai": "Dang hoat dong",
            "khu_vuc": "",
        })
        total_added += 1

    print(f"ℹ️ Gộp chi nhánh: {len(all_chinhanh)} từ trang DN + {total_added} bổ sung từ voucher "
          f"(đã khử trùng) = {len(merged)} tổng.")
    return merged
# ==========================================
# 3. CATEGORY MAPPING FUNCTIONS (từ file map_voucher_category)
# ==========================================

def load_category_mapping():
    """Đọc file danh_muc_rows.csv từ Supabase để tạo bảng tra cứu ma_danh_muc."""
    if not os.path.exists(PATH_DANH_MUC):
        raise FileNotFoundError(f"File not found: {PATH_DANH_MUC}")

    category_map = {}
    with open(PATH_DANH_MUC, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name_clean = row["ten_danh_muc"].strip().lower()
            category_map[name_clean] = row["ma_danh_muc"]
    return category_map

def build_ready_voucher_record(voucher_row, ma_danh_muc_found):
    # Thời gian bắt đầu bán cố định từ 23/8/2026
    start_dt = datetime(2026, 8, 23, 0, 0, 0)
    now_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    future_str = (start_dt + timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "ten_voucher": voucher_row.get("ten_voucher"),
        "mo_ta": voucher_row.get("mo_ta"),
        "gia_goc": voucher_row.get("gia_goc", 0),
        "gia_tri_giam": voucher_row.get("gia_tri_giam", 0),
        "dieu_kien_ap_dung": voucher_row.get("dieu_kien_ap_dung"),
        "so_luong_phat_hanh": 100,
        "tg_bat_dau_ban": now_str,
        "tg_ket_thuc_ban": future_str,
        "trang_thai": "Dang ban",
        "chinh_sach_hoan_huy": "Không quy đổi thành tiền mặt. Hỗ trợ hoàn tiền nếu hủy trước 24h.",
        "hinh_anh_url": voucher_row.get("hinh_anh_url"),
        "so_luong_da_ban": 0,
        "ma_danh_muc": ma_danh_muc_found,
    }

# ==========================================
# 4. MAIN EXECUTION — chạy 1 lần cho tất cả danh mục
# ==========================================

if __name__ == "__main__":
    # endpoints 
    inputs = {  
        "an-uong-c157": ("Ăn uống", 4), 
        "vui-choi-giai-tri-c158": ("Vui chơi giải trí", 5),
        "du-lich-khach-san": ("Du lịch khách sạn", 5)
    }

    file_dn = os.path.join(BASE_DIR, "crawl_data_files", "doanh_nghiep.csv")
    file_chinhanh = os.path.join(BASE_DIR, "crawl_data_files", "chinhanh.csv")
    file_voucher_raw = os.path.join(BASE_DIR, "crawl_data_files", "voucher.csv")
    file_voucher_cn = os.path.join(BASE_DIR, "crawl_data_files", "voucher_chinhanh.csv")
    file_voucher_ready = os.path.join(BASE_DIR, "import_files", "ready_voucher_all.csv")

    cat_map = load_category_mapping()

    all_dn = {}          # key: brand_link -> dn record (dedupe DN trùng giữa các danh mục)
    all_chinhanh = []
    all_vouchers_raw = []
    all_voucher_cn = []
    all_vouchers_ready = []
    seen_voucher_keys = set()
    seen_voucher_cn_keys = set()

    for endpoint, (ten_danh_muc, max_pages) in inputs.items():
        print(f"\n===== ĐANG XỬ LÝ DANH MỤC: {ten_danh_muc} ({endpoint}) =====")

        target_clean = ten_danh_muc.strip().lower()
        ma_danh_muc_found = cat_map.get(target_clean)
        if not ma_danh_muc_found:
            print(f"⚠️ Cảnh báo: Không tìm thấy tên danh mục '{ten_danh_muc}' trong danh_muc_rows.csv! Bỏ qua danh mục này.")
            print(f"Các danh mục hiện có: {list(cat_map.keys())}")
            continue

        # --- 1. DOANH NGHIỆP + CHI NHÁNH (dedupe theo brand_link) ---
        data_dn = extract_enterprises_from_category(endpoint, max_pages=max_pages)
        new_items = [dn for dn in data_dn if dn.get("brand_link") and dn["brand_link"] not in all_dn]
        skipped = len(data_dn) - len(new_items)
        if skipped:
            print(f"ℹ️ Bỏ qua {skipped} doanh nghiệp đã gặp ở danh mục trước (không cào lại chi nhánh).")

        if new_items:
            branches = crawl_all_branches(new_items, delay=1.0)
            all_chinhanh.extend(branches)
            for dn in new_items:
                all_dn[dn["brand_link"]] = dn

        # --- 2. VOUCHER + MAP MÃ DANH MỤC NGAY CHO ENDPOINT NÀY ---
        results = extract_voucher_prices_from_category(endpoint, max_pages=max_pages)
        vouchers, urls = results[0], results[1]

        if urls:
            print(f"Bắt đầu cào chi tiết cho {len(urls)} Voucher...")
            for i in range(len(urls)):
                print(f"[{i + 1}/{len(urls)}]")
                detail = extract_voucher_detail(urls[i])
                vouchers[i].update(detail["detail"])

                for map_row in detail["map_rows"]:
                    key = voucher_location_identity(map_row)
                    if key in seen_voucher_cn_keys:
                        continue
                    seen_voucher_cn_keys.add(key)
                    all_voucher_cn.append(map_row)

                time.sleep(0.8)

            for v in vouchers:
                key = voucher_identity(v)
                if key in seen_voucher_keys:
                    continue
                seen_voucher_keys.add(key)
                all_vouchers_raw.append(v)
                all_vouchers_ready.append(build_ready_voucher_record(v, ma_danh_muc_found))

    # --- GHI FILE DOANH NGHIỆP ---
    if all_dn:
        fieldnames_dn = ["ten_dn", "logo", "ngay_tao", "trang_thai"]
        with open(file_dn, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_dn, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_dn.values())
        print(f"\n✅ Đã lưu {len(all_dn)} Doanh nghiệp vào: {file_dn}")

    # --- GỘP CHI NHÁNH TỪ TRANG DN + CHI NHÁNH SUY RA TỪ VOUCHER (khử trùng) ---
    all_chinhanh = merge_branches_with_voucher_locations(all_chinhanh, all_voucher_cn)

    # --- GHI FILE CHI NHÁNH ---
    if all_chinhanh:
        fieldnames_chinhanh = ["ten_dn", "ten_chi_nhanh", "dia_chi", "trang_thai", "khu_vuc"]
        with open(file_chinhanh, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_chinhanh)
            writer.writeheader()
            writer.writerows(all_chinhanh)
        print(f"✅ Đã lưu {len(all_chinhanh)} Chi nhánh vào: {file_chinhanh}")
    else:
        print("⚠️ Không cào được chi nhánh nào.")

    # --- GHI FILE VOUCHER THÔ (chưa map, để đối chiếu) ---
    if all_vouchers_raw:
        fieldnames_voucher = [
            "ten_dn", "ten_voucher", "gia_goc", "gia_tri_giam",
            "hinh_anh_url", "dieu_kien_ap_dung", "mo_ta"
        ]
        with open(file_voucher_raw, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_voucher, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_vouchers_raw)
        print(f"✅ Đã lưu {len(all_vouchers_raw)} Voucher (thô) vào: {file_voucher_raw}")

    # --- GHI FILE CHI NHÁNH ÁP DỤNG VOUCHER ---
    if all_voucher_cn:
        fieldnames_map = ["ten_voucher", "ten_dn", "dia_chi_chi_nhanh"]
        with open(file_voucher_cn, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_map)
            writer.writeheader()
            writer.writerows(all_voucher_cn)
        print(f"✅ Đã lưu {len(all_voucher_cn)} bản ghi liên kết vào: {file_voucher_cn}")
    else:
        print("⚠️ Không tìm thấy địa chỉ chi nhánh nào trong các voucher.")

    # --- GHI FILE VOUCHER SẴN SÀNG IMPORT (đã map ma_danh_muc theo từng endpoint) ---
    if all_vouchers_ready:
        fieldnames_ready = [
            "ten_voucher", "mo_ta", "gia_goc", "gia_tri_giam",
            "dieu_kien_ap_dung", "so_luong_phat_hanh", "tg_bat_dau_ban",
            "tg_ket_thuc_ban", "trang_thai", "chinh_sach_hoan_huy",
            "hinh_anh_url", "so_luong_da_ban", "ma_danh_muc"
        ]
        with open(file_voucher_ready, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_ready)
            writer.writeheader()
            writer.writerows(all_vouchers_ready)
        print(f"✅ Đã map & lưu {len(all_vouchers_ready)} Voucher sẵn sàng import vào: {file_voucher_ready}")