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
        try:
            lop = LopHoc.objects.get(pk=lop_hoc_id)
            mon = MonHoc.objects.get(pk=mon_hoc_id)
        except (LopHoc.DoesNotExist, MonHoc.DoesNotExist):
            raise ValueError("Lớp học hoặc Môn học không tồn tại!")

        hoc_sinh_list = HocSinh.objects.filter(lop_hoc_id=lop_hoc_id).select_related('user')

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
    def export_bang_diem_theo_lop_co_diem(lop_hoc_id, mon_hoc_id, hoc_ky):
        try:
            lop = LopHoc.objects.get(pk=lop_hoc_id)
            mon = MonHoc.objects.get(pk=mon_hoc_id)
        except (LopHoc.DoesNotExist, MonHoc.DoesNotExist):
            raise ValueError("Lớp học hoặc Môn học không tồn tại!")

        # Lấy danh sách học sinh của lớp
        hoc_sinh_list = HocSinh.objects.filter(lop_hoc_id=lop_hoc_id).select_related('user')

        # Lấy bảng điểm của lớp này, môn này, học kỳ này
        bang_diem_list = BangDiem.objects.filter(
            hoc_sinh__lop_hoc_id=lop_hoc_id,
            mon_hoc_id=mon_hoc_id,
            hoc_ky=hoc_ky
        )

        # Tạo một dictionary để tra cứu điểm theo ID học sinh cho nhanh (Tối ưu hiệu năng)
        diem_dict = {bd.hoc_sinh_id: bd for bd in bang_diem_list}

        data_rows = []
        for index, hs in enumerate(hoc_sinh_list):
            # Lấy object điểm của học sinh (nếu đã được nhập điểm)
            diem_hs = diem_dict.get(hs.id)

            # Xử lý an toàn: Nếu chưa có điểm thì để trống, có điểm rồi thì lấy ra
            d_15p = diem_hs.diem_15p if diem_hs and diem_hs.diem_15p is not None else ''
            d_gk = diem_hs.diem_giua_ky if diem_hs and diem_hs.diem_giua_ky is not None else ''
            d_ck = diem_hs.diem_cuoi_ky if diem_hs and diem_hs.diem_cuoi_ky is not None else ''

            data_rows.append({
                'STT': index + 1,
                'Mã Học Sinh': hs.ma_hoc_sinh,
                'Họ Tên': hs.user.ho_ten,
                'Điểm 15P': d_15p,
                'Điểm Giữa Kỳ': d_gk,
                'Điểm Cuối Kỳ': d_ck
            })

        df = pd.DataFrame(data_rows)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Đổi tên sheet cho đúng ý nghĩa là Bảng Điểm
            df.to_excel(writer, index=False, sheet_name=f"BangDiem_{lop.ma_lop}_{mon.ma_mon}")

        output.seek(0)
        # Tên file trả về cũng bỏ chữ "Mau_" đi
        return output, f"BangDiem_{lop.ma_lop}_{mon.ma_mon}_HK{hoc_ky}.xlsx"

    @staticmethod
    def import_excel_diem(file_obj, lop_hoc_id, mon_hoc_id, hoc_ky):
        try:
            df = pd.read_excel(file_obj)
        except Exception:
            raise ValueError("File đính kèm không đúng định dạng Excel (.xlsx)")

        required_cols = ['Mã Học Sinh', 'Điểm 15P', 'Điểm Giữa Kỳ', 'Điểm Cuối Kỳ']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"File Excel điểm định dạng sai, thiếu cột: '{col}'")

        all_row_errors = []
        success_count = 0

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
            with transaction.atomic():
                for index, row in df.iterrows():
                    row_num = int(str(index)) + 2
                    current_row_errors = []

                    ma_hs = str(row.get('Mã Học Sinh', '')).strip()

                    if not ma_hs or ma_hs == 'nan':
                        current_row_errors.append("Mã học sinh không được để trống.")
                        all_row_errors.append({"dong": row_num, "ma_hoc_sinh": "Trống", "loi": current_row_errors})
                        continue

                    try:
                        hoc_sinh_obj = HocSinh.objects.get(ma_hoc_sinh=ma_hs, lop_hoc_id=lop_hoc_id)
                    except HocSinh.DoesNotExist:
                        current_row_errors.append(f"Học sinh mã '{ma_hs}' không tồn tại trong lớp học hiện tại.")
                        all_row_errors.append({"dong": row_num, "ma_hoc_sinh": ma_hs, "loi": current_row_errors})
                        continue

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

                    if current_row_errors:
                        all_row_errors.append({
                            "dong": row_num,
                            "ma_hoc_sinh": ma_hs,
                            "loi": current_row_errors
                        })
                        continue

                    if not all_row_errors:
                        BangDiem.objects.update_or_create(
                            hoc_sinh=hoc_sinh_obj,  # Truyền thẳng nguyên cái cục object tìm được ở trên
                            mon_hoc_id=mon_hoc_id,
                            hoc_ky=int(hoc_ky),
                            defaults={
                                'diem_15p': diem_15p,
                                'diem_giua_ky': diem_gk,
                                'diem_cuoi_ky': diem_ck,
                            }
                        )
                        success_count += 1

                if all_row_errors:
                    raise ExcelImportException(error_details=all_row_errors)

        except ExcelImportException as e:
            raise e
        except Exception as e:
            raise ValueError(f"Lỗi hệ thống bất ngờ: {str(e)}")

        return success_count