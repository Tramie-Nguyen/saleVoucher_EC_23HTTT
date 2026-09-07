import os
import csv
import re

# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN — chỉnh lại cho khớp với project của bạn
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_EXISTING = os.path.join(BASE_DIR,"export_files","voucher_cn_rows.csv")        # file đã có sẵn trên DB/Supabase
PATH_NEW = os.path.join(BASE_DIR,"import_files","ready_voucher_cn.csv")      # file vừa cào ra, cần lọc
PATH_OUTPUT = os.path.join(BASE_DIR,"import_files","ready_voucher_cn_bonus.csv")     # file kết quả: chỉ chứa dòng KHÔNG trùng

# Các cột dùng để xác định 1 dòng là "trùng" hay không.
# Phải khớp CHÍNH XÁC với header trong voucher_rows.csv mà bạn cung cấp.
KEY_COLUMNS = [
"ma_voucher","ma_chi_nhanh"
]

# Các cột dạng SỐ — so sánh theo giá trị số (tránh lệch do "100000" vs "100000.0")
NUMERIC_COLUMNS = {"gia_goc", "gia_tri_giam", "so_luong_phat_hanh", "so_luong_da_ban"}


def normalize_text(s):
    """Chuẩn hoá text: lowercase, gộp khoảng trắng, bỏ khoảng trắng thừa đầu/cuối."""
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_value(col_name, value):
    """Chuẩn hoá giá trị 1 cột tuỳ theo kiểu dữ liệu (số hay text)."""
    if col_name in NUMERIC_COLUMNS:
        digits = re.sub(r"[^\d\-]", "", str(value)) if value not in (None, "") else ""
        try:
            return int(digits) if digits not in ("", "-") else 0
        except ValueError:
            return 0
    return normalize_text(value)


def build_row_key(row, key_columns):
    """Tạo khoá duy nhất (tuple) từ các cột trong KEY_COLUMNS."""
    return tuple(normalize_value(col, row.get(col)) for col in key_columns)


def load_existing_keys(path, key_columns):
    """Đọc file voucher_rows.csv đã có, trả về tập hợp các khoá đã tồn tại."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy file: {path}")

    keys = set()
    with open(path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        missing_cols = [c for c in key_columns if c not in reader.fieldnames]
        if missing_cols:
            raise ValueError(
                f"File '{path}' thiếu các cột: {missing_cols}. "
                f"Các cột hiện có: {reader.fieldnames}"
            )

        for row in reader:
            keys.add(build_row_key(row, key_columns))

    return keys


def filter_new_rows(path_new, path_output, existing_keys, key_columns):
    """Lọc file mới, chỉ giữ lại dòng KHÔNG trùng với existing_keys."""
    if not os.path.exists(path_new):
        raise FileNotFoundError(f"Không tìm thấy file: {path_new}")

    with open(path_new, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        missing_cols = [c for c in key_columns if c not in fieldnames]
        if missing_cols:
            raise ValueError(
                f"File '{path_new}' thiếu các cột: {missing_cols}. "
                f"Các cột hiện có: {fieldnames}"
            )

        all_rows = list(reader)

    new_rows = []
    duplicate_count = 0
    seen_in_new_file = set()  # tránh trùng lặp ngay trong chính file mới

    for row in all_rows:
        key = build_row_key(row, key_columns)

        if key in existing_keys or key in seen_in_new_file:
            duplicate_count += 1
            continue

        seen_in_new_file.add(key)
        new_rows.append(row)

    os.makedirs(os.path.dirname(path_output), exist_ok=True)
    with open(path_output, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"📄 Tổng số dòng trong file mới: {len(all_rows)}")
    print(f"🔁 Số dòng trùng (đã bỏ qua): {duplicate_count}")
    print(f"✅ Số dòng MỚI (không trùng) đã lưu: {len(new_rows)}")
    print(f"➡️  File kết quả: {path_output}")

    return new_rows


if __name__ == "__main__":
    print("Đang đọc dữ liệu đã có từ:", PATH_EXISTING)
    existing_keys = load_existing_keys(PATH_EXISTING, KEY_COLUMNS)
    print(f"  -> Tìm thấy {len(existing_keys)} dòng đã tồn tại.\n")

    print("Đang lọc dữ liệu mới từ:", PATH_NEW)
    filter_new_rows(PATH_NEW, PATH_OUTPUT, existing_keys, KEY_COLUMNS)