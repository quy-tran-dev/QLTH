from core.exceptions import ExcelImportException
from core.models import BangDiem, LopHoc, MonHoc, HocSinh
import pandas as pd
from io import BytesIO
from django.db import transaction

class BangDiemService:
    @staticmethod
    def upsert_diem(data):
        diem, created = BangDiem.objects.update_or_create(
            hoc_sinh_id=data['hoc_sinh'],
            mon_hoc_id=data['mon_hoc'],
            hoc_ky=data['hoc_ky'],
            defaults={
                'diem_15p': data.get('diem_15p'),
                'diem_giua_ky': data.get('diem_giua_ky'),
                'diem_cuoi_ky': data.get('diem_cuoi_ky'),
            }
        )
        return diem

    @staticmethod
    def export_template_theo_lop(lop_hoc_id, mon_hoc_id, hoc_ky):
        """Xuất file Excel chứa sẵn danh sách học sinh của lớp để giáo viên nhập điểm"""
        try:
            lop = LopHoc.objects.get(pk=lop_hoc_id)
            mon = MonHoc.objects.get(pk=mon_hoc_id)
        except (LopHoc.DoesNotExist, MonHoc.DoesNotExist):
            raise ValueError("Lớp học hoặc Môn học không tồn tại!")

        # Lấy danh sách học sinh thuộc lớp này
        hoc_sinh_list = HocSinh.objects.filter(lop_hoc_id=lop_hoc_id).select_related('user')

        # Tạo cấu trúc file Excel mẫu
        data_rows = []
        for index, hs in enumerate(hoc_sinh_list):
            data_rows.append({
                'STT': index + 1,
                'Mã Học Sinh': hs.ma_hoc_sinh,
                'Họ Tên': hs.user.ho_ten,
                'Điểm 15P': '',
                'Điểm Giữa Kỳ': '',
                'Điểm Cuối Kỳ': ''
            })

        df = pd.DataFrame(data_rows)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=f"Diem_{lop.ma_lop}_{mon.ma_mon}")

        output.seek(0)
        return output, f"Mau_Diem_{lop.ma_lop}_{mon.ma_mon}_HK{hoc_ky}.xlsx"

    @staticmethod
    def import_excel_diem(file_obj, lop_hoc_id, mon_hoc_id, hoc_ky):
        """Đọc file Excel điểm, validate dữ liệu từng dòng và thực hiện Upsert"""
        try:
            df = pd.read_excel(file_obj)
        except Exception:
            raise ValueError("File đính kèm không đúng định dạng Excel (.xlsx)")

        # Kiểm tra các cột bắt buộc phải có
        required_cols = ['Mã Học Sinh', 'Điểm 15P', 'Điểm Giữa Kỳ', 'Điểm Cuối Kỳ']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"File Excel điểm định dạng sai, thiếu cột: '{col}'")

        all_row_errors = []
        success_count = 0

        # Hàm helper để validate điểm số hợp lệ từ 0 đến 10
        def clean_and_validate_diem(val, col_name):
            if pd.isna(val) or str(val).strip() == '' or str(val).strip().lower() == 'nan':
                return None
            try:
                diem_float = float(val)
                if not (0 <= diem_float <= 10):
                    raise ValueError(f"{col_name} phải nằm trong khoảng từ 0 đến 10.")
                return diem_float
            except (TypeError, ValueError):
                raise ValueError(f"{col_name} không đúng định dạng số.")

        try:
            with transaction.atomic():  # Đảm bảo tính nguyên tử (All or Nothing)
                for index, row in df.iterrows():
                    row_num = int(str(index)) + 2
                    current_row_errors = []

                    ma_hs = str(row.get('Mã Học Sinh', '')).strip()

                    # 1. Kiểm tra mã học sinh có trống không
                    if not ma_hs or ma_hs == 'nan':
                        current_row_errors.append("Mã học sinh không được để trống.")
                        all_row_errors.append({"dong": row_num, "ma_hoc_sinh": "Trống", "loi": current_row_errors})
                        continue

                    # 2. Kiểm tra học sinh có tồn tại và có thuộc lớp này không
                    try:
                        hoc_sinh_obj = HocSinh.objects.get(ma_hoc_sinh=ma_hs, lop_hoc_id=lop_hoc_id)
                    except HocSinh.DoesNotExist:
                        current_row_errors.append(f"Học sinh mã '{ma_hs}' không tồn tại trong lớp học hiện tại.")
                        all_row_errors.append({"dong": row_num, "ma_hoc_sinh": ma_hs, "loi": current_row_errors})
                        continue

                    # 3. Ép kiểu và validate điểm số từ hàm helper
                    diem_15p = None
                    diem_gk = None
                    diem_ck = None

                    try:
                        diem_15p = clean_and_validate_diem(row.get('Điểm 15P'), 'Điểm 15P')
                    except ValueError as err:
                        current_row_errors.append(str(err))

                    try:
                        diem_gk = clean_and_validate_diem(row.get('Điểm Giữa Kỳ'), 'Điểm Giữa Kỳ')
                    except ValueError as err:
                        current_row_errors.append(str(err))

                    try:
                        diem_ck = clean_and_validate_diem(row.get('Điểm Cuối Kỳ'), 'Điểm Cuối Kỳ')
                    except ValueError as err:
                        current_row_errors.append(str(err))

                    # 4. Gom lỗi nếu dòng này điểm bậy bạ
                    if current_row_errors:
                        all_row_errors.append({
                            "dong": row_num,
                            "ma_hoc_sinh": ma_hs,
                            "loi": current_row_errors
                        })
                        continue

                    # 5. Nếu file sạch hoàn toàn từ đầu đến giờ mới thực hiện Upsert dữ liệu
                    if not all_row_errors:
                        BangDiem.objects.update_or_create(
                            hoc_sh_id=hoc_sinh_obj.ma_hoc_sinh,  # Tên trường FK trong model BangDiem của bạn
                            mon_hoc_id=mon_hoc_id,
                            hoc_ky=int(hoc_ky),
                            defaults={
                                'diem_15p': diem_15p,
                                'diem_giua_ky': diem_gk,
                                'diem_cuoi_ky': diem_ck,
                            }
                        )
                        success_count += 1

                # Kết thúc duyệt file: Nếu có bất kỳ lỗi nào, Rollback sạch sẽ dữ liệu ngay lập tức
                if all_row_errors:
                    raise ExcelImportException(error_details=all_row_errors)

        except ExcelImportException as e:
            raise e
        except Exception as e:
            raise ValueError(f"Lỗi hệ thống bất ngờ: {str(e)}")

        return success_count