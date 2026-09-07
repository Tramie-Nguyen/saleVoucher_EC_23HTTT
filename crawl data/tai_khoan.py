import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_nguoidung_rows = os.path.join(BASE_DIR, "export_files", "nguoidung_rows.csv")
file_user = os.path.join(BASE_DIR, "import_files", "ready_nguoidung_bonus.csv")
output_file = os.path.join(BASE_DIR, "import_files", "account.csv")

FIXED_PASSWORD = (
    "$2b$10$EoJ9ZswFE82nq5SNzhPwn.GEUl7zmuAFyDP9gVsanlxkrMZAHrZiy"
)

# 1. Đọc dữ liệu
df_nguoidung = pd.read_csv(file_nguoidung_rows)
df_user = pd.read_csv(file_user)

# In ra danh sách cột của 2 file để bạn kiểm tra nếu cần
print("Các cột trong nguoidung_rows.csv:", df_nguoidung.columns.tolist())
print("Các cột trong user.csv:", df_user.columns.tolist())

# 2. Xử lý khớp dữ liệu (Join)
# Trường hợp 1: Nếu 2 file dùng chung tên cột email để so sánh
if "email" in df_user.columns and "email" in df_nguoidung.columns:
    df_matched = pd.merge(
        df_nguoidung, 
        df_user[["email"]], 
        on="email", 
        how="inner"
    )

# Trường hợp 2: Nếu file user.csv đặt tên cột là 'id' hoặc 'user_id' thay vì 'ma_nguoi_dung'
elif "id" in df_user.columns and "ma_nguoi_dung" in df_nguoidung.columns:
    df_matched = pd.merge(
        df_nguoidung, 
        df_user[["id"]], 
        left_on="ma_nguoi_dung", 
        right_on="id", 
        how="inner"
    )

# Trường hợp 3: Khớp theo mã người dùng nếu cả 2 file đều có 'ma_nguoi_dung'
elif "ma_nguoi_dung" in df_user.columns and "ma_nguoi_dung" in df_nguoidung.columns:
    df_matched = pd.merge(
        df_nguoidung, 
        df_user[["ma_nguoi_dung"]], 
        on="ma_nguoi_dung", 
        how="inner"
    )

else:
    raise KeyError("Không tìm thấy cột chung (như email, id, ma_nguoi_dung) giữa 2 file để ghép dữ liệu!")

# 3. Tạo DataFrame cho bảng tài khoản từ dữ liệu đã lọc thành công
df_tai_khoan = pd.DataFrame()
df_tai_khoan["thong_tin_dang_nhap"] = df_matched["email"]
df_tai_khoan["mat_khau"] = FIXED_PASSWORD
df_tai_khoan["ma_nguoi_dung"] = df_matched["ma_nguoi_dung"]

# 4. Sắp xếp thứ tự cột
df_tai_khoan = df_tai_khoan[
    ["thong_tin_dang_nhap", "mat_khau", "ma_nguoi_dung"]
]

# 5. Xuất file kết quả
os.makedirs(os.path.dirname(output_file), exist_ok=True)
df_tai_khoan.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Đã xuất thành công {len(df_tai_khoan)} tài khoản khớp vào file: {output_file}")