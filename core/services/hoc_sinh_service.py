from django.db import transaction

from core.exceptions import ExcelImportException
from core.models import NguoiDung, HocSinh, LopHoc  # Nhớ import thêm LopHoc
from datetime import datetime
import pandas as pd
from io import BytesIO
from core.services.nguoi_dung_service import NguoiDungService


class HocSinhService:
    @staticmethod
    def _tao_ma_hoc_sinh(nien_khoa=None):
        year = nien_khoa or datetime.now().year
        prefix = f"HS{year}"
        last_student = HocSinh.objects.filter(ma_hoc_sinh__startswith=prefix).order_by('-ma_hoc_sinh').first()
        if last_student:
            return f"{prefix}{int(last_student.ma_hoc_sinh[-3:]) + 1:03d}"
        return f"{prefix}001"

    @staticmethod
    def create(data):
        # Kiểm tra lớp học hợp lệ (Việc riêng của học sinh)
        lop_hoc_obj = None
        if data.get('lop_hoc_id'):
            from core.models import LopHoc
            try:
                lop_hoc_obj = LopHoc.objects.get(pk=data['lop_hoc_id'])
            except LopHoc.DoesNotExist:
                raise ValueError(f"Lớp học không tồn tại!")

        with transaction.atomic():
            # 1. ỦY QUYỀN TẠO USER (Truyền cứng role là hoc_sinh)
            user = NguoiDungService.create_profile(data, vai_tro='hoc_sinh')

            # 2. XỬ LÝ VIỆC CỦA HỌC SINH
            ma_tu_dong = HocSinhService._tao_ma_hoc_sinh(data.get('nien_khoa'))

            return HocSinh.objects.create(
                user=user,
                ma_hoc_sinh=ma_tu_dong,
                lop_hoc=lop_hoc_obj
            )

    @staticmethod
    def get(student_id):
        # TỐI ƯU QUERY: Bổ sung 'lop_hoc' vào select_related
        return HocSinh.objects.select_related('user', 'lop_hoc').get(pk=student_id)

    @staticmethod
    def list():
        # TỐI ƯU QUERY: Bổ sung 'lop_hoc' vào select_related
        return HocSinh.objects.select_related('user', 'lop_hoc').all()

    @staticmethod
    def update(student_id, data):
        with transaction.atomic():
            student = HocSinh.objects.select_related('user').get(pk=student_id)

            NguoiDungService.update_profile(student.user, data)

            if 'ma_hoc_sinh' in data:
                if HocSinh.objects.filter(ma_hoc_sinh=data['ma_hoc_sinh']).exclude(pk=student.pk).exists():
                    raise ValueError(f"Mã học sinh '{data['ma_hoc_sinh']}' đã tồn tại!")
                student.ma_hoc_sinh = data['ma_hoc_sinh']

            # CẬP NHẬT LỚP HỌC MỚI
            if 'lop_hoc_id' in data:
                if not data['lop_hoc_id']:
                    student.lop_hoc = None
                else:
                    try:
                        student.lop_hoc = LopHoc.objects.get(pk=data['lop_hoc_id'])
                    except LopHoc.DoesNotExist:
                        raise ValueError(f"Lớp học không tồn tại!")

            student.save()
            return student

    @staticmethod
    def delete(student_id):
        student = HocSinh.objects.get(pk=student_id)
        student.user.trang_thai = False
        student.user.save()

    @staticmethod
    def recover(student_id):
        student = HocSinh.objects.get(pk=student_id)
        student.user.trang_thai = True
        student.user.save()

    @staticmethod
    def export_template():
        """Tạo ra một file Excel mẫu trắng để đưa cho Giáo viên/Quản lý điền"""
        df = pd.DataFrame(columns=['STT', 'Họ Tên', 'CCCD', 'Tên Đăng Nhập', 'Mật Khẩu', 'Mã Lớp'])

        # Điền sẵn 1 dòng dữ liệu mẫu để họ biết cách nhập
        df.loc[0] = [1, 'Nguyễn Văn A', '079123456789', 'nguyenvana', '123456', '10A1']

        output = BytesIO()  # Ghi ra bộ nhớ ảo RAM thay vì lưu file rác xuống ổ cứng
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Danh_Sach_Hoc_Sinh')

        output.seek(0)
        return output

    @staticmethod
    def import_excel(file_obj):
        try:
            df = pd.read_excel(file_obj)
        except Exception:
            raise ValueError("File đính kèm không đúng định dạng Excel (.xlsx)")

        # Kiểm tra cấu trúc cột tối thiểu
        required_cols = ['Họ Tên', 'Tên Đăng Nhập']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"File Excel định dạng sai, thiếu cột bắt buộc: '{col}'")

        all_row_errors = []
        success_count = 0

        try:
            with transaction.atomic():
                for index, row in df.iterrows():

                    row_num = int(str(index)) + 2
                    current_row_errors = []

                    # 1. CHUẨN HÓA DATA
                    clean_user_data = NguoiDungService.clean_excel_row(row)

                    # 2. VALIDATE TRÙNG LẶP (Username, CCCD)
                    user_errors = NguoiDungService.validate_import_row(
                        username=clean_user_data['username'],
                        cccd=clean_user_data['cccd']
                    )
                    current_row_errors.extend(user_errors)

                    # 3. Check thêm logic nghiệp vụ đặc thù của riêng Học Sinh
                    if not clean_user_data['ho_ten']:
                        current_row_errors.append("Họ tên học sinh không được để trống.")

                    lop_hoc_obj = None
                    ma_lop = str(row.get('Mã Lớp', '')).strip()
                    if ma_lop and ma_lop != 'nan':
                        try:
                            lop_hoc_obj = LopHoc.objects.get(ma_lop=ma_lop)
                        except LopHoc.DoesNotExist:
                            current_row_errors.append(f"Không tìm thấy lớp học nào có mã '{ma_lop}'.")

                    # 4. Gom lỗi nếu dòng này có biến
                    if current_row_errors:
                        all_row_errors.append({
                            "dong": row_num,
                            "ten_dang_nhap": clean_user_data['username'] or "Trống",
                            "loi": current_row_errors
                        })
                        continue  # Nhảy sang dòng tiếp theo để quét tiếp lỗi, không chèn dòng này

                    # 5. Nếu chưa từng có dòng nào lỗi từ file -> Tiến hành tạo mới
                    if not all_row_errors:

                        user = NguoiDungService.create_profile(clean_user_data, vai_tro='hoc_sinh')

                        # Tự động sinh mã học sinh dựa theo thuật toán của trường
                        ma_hs = HocSinhService._tao_ma_hoc_sinh()
                        HocSinh.objects.create(user=user, ma_hoc_sinh=ma_hs, lop_hoc=lop_hoc_obj)
                        success_count += 1

                # KẾT THÚC VÒNG LẶP: Nếu phát hiện bất kỳ dòng lỗi nào, kích hoạt hủy (Rollback) toàn bộ dữ liệu
                if all_row_errors:
                    raise ExcelImportException(error_details=all_row_errors)

        except ExcelImportException as e:
            raise e
        except Exception as e:
            raise ValueError(f"Lỗi hệ thống bất ngờ: {str(e)}")

        return success_count
