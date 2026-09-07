import csv
import random
import string
import os
from datetime import datetime
import unidecode
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------
# 1. HÀM SINH 1 NGƯỜI ĐẠI DIỆN, ĐÃ MAP SẴN ma_hsdn
# -------------------------------------------------------------

def generate_one_representative(ma_hsdn, unique_suffix):
    first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đặng", "Bùi"]
    middle_names = ["Văn", "Thị", "Đức", "Minh", "Thành", "Quang", "Phương"]
    last_names = ["An", "Bình", "Cường", "Dũng", "Hải", "Linh", "Thảo", "Tuấn"]

    ho = random.choice(first_names)
    ten_lot = random.choice(middle_names)
    ten = random.choice(last_names)
    full_name = f"{ho} {ten_lot} {ten}"
    
    # Tạo username chuẩn: ten.ho (chuyển về không dấu, chữ thường)
    ten_clean = unidecode.unidecode(ten.lower())
    ho_clean = unidecode.unidecode(ho.lower())
    
    # Email định dạng: ten.ho.ma_hsdn@gmail.com (vừa đẹp vừa đảm bảo UNIQUE)
    email = f"{ten_clean}.{ho_clean}{random.randint(1000, 9999)}@gmail.com"    
    phone = "09" + "".join(random.choices(string.digits, k=8))
    cccd = "0" + "".join(random.choices(string.digits, k=11))

    return {
        "ho_ten": full_name,
        "email": email,
        "sdt": phone,
        "ngay_sinh": "1985-06-15",
        "gioi_tinh": random.choice(["Nam", "Nu"]),
        "cccd": cccd,
        "vai_tro": "Nguoi dai dien",
        "trang_thai": "Dang hoat dong",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ma_chi_nhanh": None,
        "ma_hsdn": ma_hsdn
    }

# -------------------------------------------------------------
# 2. KHỚP TÊN DOANH NGHIỆP & SINH NGƯỜI ĐẠI DIỆN
# -------------------------------------------------------------

def generate_representatives_from_exported_hosodn(
    ready_hosodn_csv, 
    exported_hosodn_csv, 
    output_rep_csv
):
    """
    1. Đọc ready_hosodn_csv để lấy danh sách ten_dn cần tạo người đại diện đợt này.
    2. Đọc exported_hosodn_csv để tìm ma_hs tương ứng với ten_dn đó.
    3. Sinh người đại diện nếu khớp tên doanh nghiệp.
    """
    if not os.path.exists(ready_hosodn_csv):
        print(f"⚠️ Không tìm thấy file local ready_hosodn: {ready_hosodn_csv}")
        return

    if not os.path.exists(exported_hosodn_csv):
        print(f"⚠️ Không tìm thấy file export từ Supabase: {exported_hosodn_csv}")
        return

    # Bước A: Đọc danh sách ten_dn từ file ready_hosodn local
    target_dn_names = set()
    with open(ready_hosodn_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ten_dn = row.get("ten_dn", "").strip().lower()
            if ten_dn:
                target_dn_names.add(ten_dn)

    print(f"📋 Tìm thấy {len(target_dn_names)} doanh nghiệp cần sinh Người đại diện trong đợt này.")

    # Bước B: Đọc file export từ Supabase để lấy ma_hs theo ten_dn khớp
    reps_data = []
    matched_count = 0
    skipped = 0

    with open(exported_hosodn_csv, mode="r", encoding="utf-8-sig") as f:
        hosodn_rows = [row for row in csv.DictReader(f)]

    for idx, row in enumerate(hosodn_rows, 1):
        ten_dn_db = row.get("ten_dn", "").strip().lower()
        ma_hs = row.get("ma_hs") or row.get("id")  # Tương thích cả cột ma_hs hoặc id

        # Chỉ xử lý khi tên doanh nghiệp nằm trong danh sách ready_hosodn VÀ đã có ma_hs
        if ten_dn_db in target_dn_names:
            if ma_hs:
                reps_data.append(generate_one_representative(ma_hs, idx))
                matched_count += 1
            else:
                skipped += 1

    if skipped:
        print(f"⚠️ Có {skipped} doanh nghiệp trùng tên nhưng chưa có ma_hs trên Supabase.")

    # Bước C: Ghi ra file người dùng sẵn sàng import
    fieldnames_rep = [
        "ho_ten", "email", "sdt", "ngay_sinh",
        "gioi_tinh", "cccd", "vai_tro", "trang_thai",
        "created_at", "ma_chi_nhanh", "ma_hsdn"
    ]

    os.makedirs(os.path.dirname(output_rep_csv), exist_ok=True)
    with open(output_rep_csv, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_rep)
        writer.writeheader()
        writer.writerows(reps_data)

    print(f"✅ Đã khớp và tạo thành công {matched_count} Người đại diện: {output_rep_csv}")

# ==========================================
# CHẠY SCRIPT
# ==========================================
if __name__ == "__main__":

    # File local chứa danh sách doanh nghiệp vừa xử lý đợt này
    FILE_READY_HOSODN = os.path.join(BASE_DIR, "import_files", "ready_hosodn_bonus.csv")
    
    # File hosodn export từ Supabase (có ma_hs)
    FILE_EXPORTED_HOSODN = os.path.join(BASE_DIR, "export_files", "hosodn_rows.csv")
    
    # File kết quả đầu ra
    FILE_REP_OUT = os.path.join(BASE_DIR, "import_files", "ready_nguoidung.csv")

    generate_representatives_from_exported_hosodn(
        ready_hosodn_csv=FILE_READY_HOSODN,
        exported_hosodn_csv=FILE_EXPORTED_HOSODN,
        output_rep_csv=FILE_REP_OUT
    )