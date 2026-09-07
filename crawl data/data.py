import csv
import random
import string
import os
import unicodedata
from datetime import datetime

# 1. Hàm bỏ dấu tiếng Việt (không phụ thuộc thư viện ngoài unidecode)
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFD', input_str)
    no_accent = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return no_accent.replace('đ', 'd').replace('Đ', 'D')

# 2. Danh sách họ tên mở rộng
FIRST_NAMES = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Vũ", "Võ", "Đặng", 
    "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đào", "Đinh", "Đoàn"
]
MIDDLE_NAMES_MALE = ["Văn", "Đức", "Minh", "Thành", "Quang", "Hữu", "Tuấn", "Thái", "Hải", "Đình", "Quốc"]
MIDDLE_NAMES_FEMALE = ["Thị", "Phương", "Khánh", "Ngọc", "Thảo", "Hồng", "Thanh", "Như", "Cẩm", "Bảo"]

LAST_NAMES_MALE = ["An", "Bình", "Cường", "Dũng", "Hải", "Tuấn", "Khang", "Khôi", "Long", "Nam", "Phúc", "Quân", "Sơn", "Tùng", "Vĩnh"]
LAST_NAMES_FEMALE = ["Linh", "Thảo", "Trang", "Anh", "Châu", "Hà", "Hương", "Mai", "Nhi", "Quyên", "Tâm", "Uyên", "Yến", "Vy"]

def generate_full_name():
    gioi_tinh = random.choice(["Nam", "Nu"])
    ho = random.choice(FIRST_NAMES)
    
    if gioi_tinh == "Nam":
        ten_lot = random.choice(MIDDLE_NAMES_MALE)
        ten = random.choice(LAST_NAMES_MALE)
    else:
        ten_lot = random.choice(MIDDLE_NAMES_FEMALE)
        ten = random.choice(LAST_NAMES_FEMALE)
        
    return f"{ho} {ten_lot} {ten}", gioi_tinh, ho, ten

def create_single_user(role, ma_hs, ma_chi_nhanh=None):
    full_name, gioi_tinh, ho, ten = generate_full_name()
    
    ten_clean = remove_accents(ten).lower()
    ho_clean = remove_accents(ho).lower()
    rand_digits = random.randint(1000, 9999)
    email = f"{ten_clean}.{ho_clean}{rand_digits}@gmail.com"
    
    phone = "09" + "".join(random.choices(string.digits, k=8))
    cccd = "0" + "".join(random.choices(string.digits, k=11))
    
    year = random.randint(1990, 2002)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    ngay_sinh = f"{year}-{month:02d}-{day:02d}"

    return {
        "ho_ten": full_name,
        "email": email,
        "sdt": phone,
        "ngay_sinh": ngay_sinh,
        "gioi_tinh": gioi_tinh,
        "cccd": cccd,
        "vai_tro": role,
        "trang_thai": "Dang hoat dong",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ma_chi_nhanh": ma_chi_nhanh,
        "ma_hs": ma_hs
    }

# 3. Đọc dữ liệu từ file hsdn.csv và chinhanh.csv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_hsdn = os.path.join(BASE_DIR, "export_files","hosodn_rows.csv")
file_chinhanh =  os.path.join(BASE_DIR, "export_files","chinhanh_rows.csv") 
output_file =  os.path.join(BASE_DIR, "import_files","user.csv")

# Gom nhóm danh sách mã chi nhánh theo từng mã hsdn
# Cấu trúc: { 'ma_hs_01': ['MA_CN_01', 'MA_CN_02'], ... }
branches_by_hsdn = {}

with open(file_chinhanh, mode="r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        hsdn_id = row["ma_hs"]
        cn_id = row["ma_chi_nhanh"]
        
        if hsdn_id not in branches_by_hsdn:
            branches_by_hsdn[hsdn_id] = []
        branches_by_hsdn[hsdn_id].append(cn_id)

all_users = []

# Đọc file hsdn.csv và tạo người dùng
with open(file_hsdn, mode="r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ma_hs = row["ma_hs"]
        
        # A. Tạo 1 Nhân viên quản lý voucher cho doanh nghiệp (không thuộc chi nhánh cụ thể nào)
        manager = create_single_user(
            role="Nhan vien quan ly voucher",
            ma_hs=ma_hs,
            ma_chi_nhanh=None
        )
        all_users.append(manager)
        
        # B. Tạo Nhân viên bán hàng cho từng chi nhánh của doanh nghiệp đó (nếu có)
        list_chi_nhanh = branches_by_hsdn.get(ma_hs, [])
        for ma_chi_nhanh in list_chi_nhanh:
            seller = create_single_user(
                role="Nhan vien ban hang",
                ma_hs=ma_hs,
                ma_chi_nhanh=ma_chi_nhanh
            )
            all_users.append(seller)

# 4. Xuất dữ liệu ra file nguoidung.csv
if all_users:
    fieldnames = list(all_users[0].keys())
    with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_users)
        
    print(f"Đã tạo thành công {len(all_users)} người dùng vào file {output_file}")