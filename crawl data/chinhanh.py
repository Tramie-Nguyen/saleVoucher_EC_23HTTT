import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def normalize_text(s):
    """Chuẩn hoá text để so khớp: lowercase, gộp khoảng trắng thừa."""
    if not s:
        return ""
    import re
    s = str(s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def map_ma_hs_to_chinhanh(
    exported_hosodn_csv, 
    raw_chinhanh_csv, 
    final_chinhanh_csv
):
    """
    1. Đọc file hosodn (đã có ma_hs) để tạo dictionary: ten_dn -> ma_hs
    2. Đọc file chinhanh thô, map ma_hs dựa vào ten_dn
    3. Xuất file chinhanh hoàn chỉnh (không chứa ten_dn thừa, KHÔNG ghi dòng thiếu ma_hs)
    """
    
    # BƯỚC 1: Tạo bảng tra cứu ten_dn -> ma_hs
    dn_to_ma_hs = {}
    with open(exported_hosodn_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ten_dn = row.get("ten_dn", "").strip()
            ma_hs = row.get("ma_hs") or row.get("id")  # Hỗ trợ cả tên cột ma_hs hoặc id
            
            if ten_dn and ma_hs:
                dn_to_ma_hs[normalize_text(ten_dn)] = ma_hs

    print(f"🔍 Đã load {len(dn_to_ma_hs)} doanh nghiệp để chuẩn bị map Chi nhánh.")

    # BƯỚC 2: Map ma_hs vào dữ liệu chi nhánh
    final_chinhanh_data = []
    unmatched_rows = []  # lưu riêng các dòng KHÔNG khớp để bạn kiểm tra thủ công
    matched_count = 0

    with open(raw_chinhanh_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ten_dn = row.get("ten_dn", "").strip()
            
            # Tìm ma_hs tương ứng dựa vào ten_dn (đã chuẩn hoá)
            ma_hs = dn_to_ma_hs.get(normalize_text(ten_dn))
            
            if not ma_hs:
                # KHÔNG đưa vào file final — tránh ghi "" vào cột uuid
                unmatched_rows.append(row)
                continue

            matched_count += 1

            # Tạo record mới đúng Schema Supabase (Loại bỏ ten_dn)
            final_chinhanh_data.append({
                "ten_chi_nhanh": row.get("ten_chi_nhanh"),
                "dia_chi": row.get("dia_chi"),
                "trang_thai": row.get("trang_thai", "Dang_hoat_dong"),
                "khu_vuc": row.get("khu_vuc"),
                "ma_hs": ma_hs
            })

    # BƯỚC 3: Ghi file CSV hoàn chỉnh (chỉ chứa dòng ĐÃ map thành công)
    fieldnames = ["ten_chi_nhanh", "dia_chi", "trang_thai", "ma_hs", "khu_vuc"]

    os.makedirs(os.path.dirname(final_chinhanh_csv), exist_ok=True)
    with open(final_chinhanh_csv, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_chinhanh_data)

    # Ghi thêm file riêng cho các dòng KHÔNG khớp, để bạn kiểm tra tên DN bị lệch
    if unmatched_rows:
        unmatched_path = final_chinhanh_csv.replace(".csv", "_unmatched.csv")
        with open(unmatched_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(unmatched_rows)
        print(f"⚠️ File chứa {len(unmatched_rows)} chi nhánh KHÔNG khớp ten_dn: {unmatched_path}")

    print(f"✅ Đã map thành công {matched_count} chi nhánh (Thất bại: {len(unmatched_rows)})")
    print(f"📁 File sẵn sàng import Supabase: {final_chinhanh_csv}")
# ==========================================
# CHẠY SCRIPT
# ==========================================
if __name__ == "__main__":

    # 1. File hosodn xuất từ Supabase (ĐÃ CÓ CỘT ma_hs)
    FILE_EXPORTED_HOSODN = os.path.join(BASE_DIR, "export_files", "hosodn_rows.csv") 
    
    # 2. File chi nhánh cào thô ban đầu
    FILE_RAW_CHINHANH = os.path.join(BASE_DIR,"crawl_data_files","chinhanh.csv") 
    
    # 3. File đầu ra cuối cùng để import vào Supabase
    FILE_FINAL_CHINHANH = os.path.join(BASE_DIR, "import_files", "ready_chinhanh.csv")

    map_ma_hs_to_chinhanh(
        exported_hosodn_csv=FILE_EXPORTED_HOSODN,
        raw_chinhanh_csv=FILE_RAW_CHINHANH,
        final_chinhanh_csv=FILE_FINAL_CHINHANH
    )