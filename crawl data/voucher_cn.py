import csv
import os
import re
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def clean_text(text):
    """Làm sạch chuỗi: xóa xuống dòng, tab, khoảng trắng thừa và đưa về lowercase."""
    if not text:
        return ""
    text = re.sub(r'[\r\n\t]+', ' ', str(text))
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()


def normalize_for_match(value):
    if value is None:
        return ""
    text = str(value)
    text = text.replace('–', '-').replace('—', '-')
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def map_voucher_chinhanh(
    exported_voucher_csv,
    exported_hosodn_csv,
    exported_chinhanh_csv,
    raw_voucher_cn_csv,
    output_voucher_cn_csv,
):
    # -----------------------------------------------------------------
    # BƯỚC 1: Load bảng tra cứu Voucher
    # -----------------------------------------------------------------
    voucher_map = {}
    with open(exported_voucher_csv, mode="r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ten_v = normalize_for_match(row.get("ten_voucher"))
            ma_v = row.get("ma_voucher") or row.get("id")
            if ten_v and ma_v:
                voucher_map[ten_v] = ma_v

    # -----------------------------------------------------------------
    # BƯỚC 2: Load bảng tra cứu Hồ sơ DN
    # -----------------------------------------------------------------
    hosodn_map = {}
    with open(exported_hosodn_csv, mode="r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ten_dn = normalize_for_match(row.get("ten_dn"))
            ma_hs = row.get("ma_hs") or row.get("id")
            if ten_dn and ma_hs:
                hosodn_map[ten_dn] = ma_hs

    # -----------------------------------------------------------------
    # BƯỚC 3: Load bảng tra cứu Chi nhánh & Secondary Map O(1)
    # -----------------------------------------------------------------
    chinhanh_map = {}
    address_fallback_map = {}
    with open(exported_chinhanh_csv, mode="r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ma_cn = row.get("ma_chi_nhanh") or row.get("id")
            ma_hs = row.get("ma_hs") or ""
            dia_chi = row.get("dia_chi")

            if ma_cn and dia_chi:
                key_hs = normalize_for_match(ma_hs)
                key_dia = normalize_for_match(dia_chi)
                chinhanh_map[(key_hs, key_dia)] = ma_cn
                address_fallback_map.setdefault(key_dia, ma_cn)

    print(f"🔍 Đã load dữ liệu tra cứu thành công từ Supabase!")

    # -----------------------------------------------------------------
    # BƯỚC 4: Map dữ liệu crawl & lọc trùng theo DB constraint
    # -----------------------------------------------------------------
    # Một bản ghi hợp lệ trong DB là duy nhất theo cặp (ma_voucher, ma_chi_nhanh).
    # Nếu cùng cặp xuất hiện nhiều lần trong raw, cần giữ bản ghi đầu tiên và ghi phần
    # còn lại vào file failed_voucher_cn.csv để kiểm tra/điều chỉnh thủ công.
    final_records = []
    failed_records = []
    seen_pairs = set()
    total_processed = 0

    with open(raw_voucher_cn_csv, mode="r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            total_processed += 1
            ten_v_raw = normalize_for_match(row.get("ten_voucher"))
            ten_dn_raw = normalize_for_match(row.get("ten_dn"))
            dia_chi_raw = normalize_for_match(row.get("dia_chi_chi_nhanh"))

            ma_voucher = voucher_map.get(ten_v_raw)
            ma_hs = hosodn_map.get(ten_dn_raw)

            ma_chi_nhanh = None
            if ma_hs:
                ma_chi_nhanh = chinhanh_map.get((normalize_for_match(ma_hs), dia_chi_raw))
            if not ma_chi_nhanh:
                ma_chi_nhanh = address_fallback_map.get(dia_chi_raw)

            if not ma_voucher or not ma_chi_nhanh:
                failed_records.append({
                    "ten_voucher": row.get("ten_voucher"),
                    "ten_dn": row.get("ten_dn"),
                    "dia_chi_chi_nhanh": row.get("dia_chi_chi_nhanh"),
                    "reason": "missing ma_voucher or ma_chi_nhanh",
                })
                continue

            pair = (ma_voucher, ma_chi_nhanh)
            if pair in seen_pairs:
                failed_records.append({
                    "ten_voucher": row.get("ten_voucher"),
                    "ten_dn": row.get("ten_dn"),
                    "dia_chi_chi_nhanh": row.get("dia_chi_chi_nhanh"),
                    "reason": "duplicate (ma_voucher, ma_chi_nhanh)",
                })
                continue

            seen_pairs.add(pair)
            final_records.append({
                "ma_voucher": ma_voucher,
                "ma_chi_nhanh": ma_chi_nhanh,
            })

    with open(output_voucher_cn_csv, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["ma_voucher", "ma_chi_nhanh"])
        writer.writeheader()
        writer.writerows(final_records)

    failed_path = os.path.join(os.path.dirname(output_voucher_cn_csv), "failed_voucher_cn.csv")
    with open(failed_path, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["ten_voucher", "ten_dn", "dia_chi_chi_nhanh", "reason"])
        writer.writeheader()
        writer.writerows(failed_records)

    # Thống kê báo cáo
    print(f"\n================ BÁO CÁO KẾT QUẢ ================")
    print(f"📊 Tổng số dòng trong file raw: {total_processed}")
    print(f"📊 Số dòng đã map thành công: {len(final_records)}")
    print(f"📊 Số dòng bị loại do fail/duplicate: {len(failed_records)}")
    print(f"📁 File sẵn sàng import Supabase: {output_voucher_cn_csv}")
    print(f"📄 File lý do fail: {failed_path}")


# ==========================================
# CHẠY SCRIPT
# ==========================================
if __name__ == "__main__":
    FILE_EXPORT_VOUCHER = os.path.join(BASE_DIR, "export_files", "voucher_rows.csv")
    FILE_EXPORT_HOSODN = os.path.join(BASE_DIR, "export_files", "hosodn_rows.csv")
    FILE_EXPORT_CHINHANH = os.path.join(BASE_DIR, "export_files", "chinhanh_rows.csv")

    FILE_RAW_VOUCHER_CN = os.path.join(BASE_DIR, "crawl_data_files", "voucher_chinhanh.csv")

    FILE_FINAL_VOUCHER_CN = os.path.join(BASE_DIR, "import_files", "ready_voucher_cn.csv")
    FILE_FAILED_LOG = os.path.join(BASE_DIR, "import_files", "failed_voucher_cn.csv")

    map_voucher_chinhanh(
        exported_voucher_csv=FILE_EXPORT_VOUCHER,
        exported_hosodn_csv=FILE_EXPORT_HOSODN,
        exported_chinhanh_csv=FILE_EXPORT_CHINHANH,
        raw_voucher_cn_csv=FILE_RAW_VOUCHER_CN,
        output_voucher_cn_csv=FILE_FINAL_VOUCHER_CN,
    )