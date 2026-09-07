import csv
import random
import string
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------
# 1. HÀM BỔ TRỢ
# -------------------------------------------------------------

def generate_tax_code():
    """Sinh Mã số thuế ngẫu nhiên dạng 10 chữ số (VD: 0312345678)."""
    return "03" + "".join(random.choices(string.digits, k=8))

def get_first_address_map(branch_csv_path):
    """Đọc file chi nhánh để lấy địa chỉ ĐẦU TIÊN của từng Doanh nghiệp."""
    first_addresses = {}
    if not os.path.exists(branch_csv_path):
        print(f"⚠️ Không tìm thấy file chi nhánh tại: {branch_csv_path}")
        return first_addresses

    with open(branch_csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ten_dn = row.get("ten_dn")
            dia_chi = row.get("dia_chi")
            if ten_dn and dia_chi and ten_dn not in first_addresses:
                first_addresses[ten_dn] = dia_chi
    return first_addresses

# -------------------------------------------------------------
# 2. XỬ LÝ HỒ SƠ DOANH NGHIỆP (BƯỚC 1 - chạy và đẩy lên Supabase TRƯỚC)
# -------------------------------------------------------------

def process_enterprises(input_dn_csv, input_cn_csv, output_dn_csv):
    """
    Chuẩn hoá dữ liệu Doanh nghiệp cào thô -> file sẵn sàng import vào bảng hosodn.
    Bảng hosodn hiện KHÔNG còn cột id_nguoi_dai_dien (quan hệ đã đảo chiều sang nguoidung.ma_hsdn),
    nên hàm này chỉ lo đúng phần hosodn, không sinh người đại diện ở đây nữa.
    """
    with open(input_dn_csv, mode="r", encoding="utf-8-sig") as f:
        data_dn = [row for row in csv.DictReader(f)]

    first_addrs = get_first_address_map(input_cn_csv)

    gpkd_default = "https://ketoananpha.vn/uploads/images/post/36-moi/Phan-biet-giay-phep-kinh-doanh-va-giay-chung-nhan-dang-ky-doanh-nghiep-03.jpg"
    final_dn_data = []

    for dn in data_dn:
        ten_dn = dn.get("ten_dn")
        dia_chi_dau_tien = first_addrs.get(ten_dn, "Đang cập nhật")

        final_dn_data.append({
            "ten_dn": ten_dn,
            "ma_so_thue": generate_tax_code(),
            "dia_chi": dia_chi_dau_tien,
            "giay_phep_kinh_doanh": gpkd_default,
            "ngay_tao": dn.get("ngay_tao", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "trang_thai": dn.get("trang_thai", "Dang hoat dong"),
            "logo": dn.get("logo")
        })

    # Đã bỏ "id_nguoi_dai_dien" khỏi schema hosodn
    fieldnames_dn = [
        "ten_dn", "ma_so_thue", "dia_chi", "giay_phep_kinh_doanh",
        "ngay_tao", "trang_thai", "logo"
    ]

    os.makedirs(os.path.dirname(output_dn_csv), exist_ok=True)
    with open(output_dn_csv, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_dn)
        writer.writeheader()
        writer.writerows(final_dn_data)

    print(f"✅ Đã tạo file Hồ sơ doanh nghiệp sẵn sàng import: {output_dn_csv}")
    print("👉 Bước tiếp theo: đẩy file này lên Supabase (bảng hosodn), export lại để lấy "
          "cột ma_hs tự sinh, rồi chạy generate_representatives.py")

# ==========================================
# CHẠY SCRIPT
# ==========================================
if __name__ == "__main__":
    FILE_DN_CRAWL = os.path.join(BASE_DIR, "crawl_data_files", "doanh_nghiep.csv")
    FILE_CN_CRAWL = os.path.join(BASE_DIR, "crawl_data_files", "chinhanh.csv")

    FILE_DN_OUT = os.path.join(BASE_DIR, "import_files", f"ready_hosodn_bonus.csv")

    process_enterprises(
        input_dn_csv=FILE_DN_CRAWL,
        input_cn_csv=FILE_CN_CRAWL,
        output_dn_csv=FILE_DN_OUT
    )