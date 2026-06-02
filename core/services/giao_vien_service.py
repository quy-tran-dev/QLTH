from django.db import transaction

from core.exceptions import ExcelImportException
from core.models import GiaoVien
from core.services.nguoi_dung_service import NguoiDungService
from datetime import datetime
import pandas as pd
from io import BytesIO


class GiaoVienService:
    @staticmethod
    def _tao_ma_giao_vien():
        # Sinh mã tự động: GV2026001
        year = datetime.now().year
        prefix = f"GV{year}"
        last_gv = GiaoVien.objects.filter(ma_giao_vien__startswith=prefix).order_by('-ma_giao_vien').first()

        if last_gv:
            last_number = int(last_gv.ma_giao_vien[-3:])
            return f"{prefix}{last_number + 1:03d}"
        return f"{prefix}001"

    @staticmethod
    def create(data):
        with transaction.atomic():
            # 1. ỦY QUYỀN TẠO USER (Truyền cứng role là giao_vien)
            user = NguoiDungService.create_profile(data, vai_tro='giao_vien')

            # 2. XỬ LÝ VIỆC CỦA GIÁO VIÊN
            ma_tu_dong = GiaoVienService._tao_ma_giao_vien()

            return GiaoVien.objects.create(
                user=user,
                ma_giao_vien=ma_tu_dong,
                to_bo_mon=data.get('to_bo_mon', '')
            )

    @staticmethod
    def get(gv_id):
        return GiaoVien.objects.select_related('user').get(pk=gv_id)

    @staticmethod
    def list():
        return GiaoVien.objects.select_related('user').all()

    @staticmethod
    def update(gv_id, data):
        with transaction.atomic():
            gv = GiaoVien.objects.select_related('user').get(pk=gv_id)

            # 1. ỦY QUYỀN: Giao phó toàn bộ việc update bảng NguoiDung cho base service
            NguoiDungService.update_profile(gv.user, data)

            # 2. XỬ LÝ RIÊNG: Cập nhật thông tin đặc thù của Giáo Viên
            if 'ma_giao_vien' in data:
                new_ma_gv = data['ma_giao_vien']
                if GiaoVien.objects.filter(ma_giao_vien=new_ma_gv).exclude(pk=gv.pk).exists():
                    raise ValueError(f"Mã giáo viên '{new_ma_gv}' đã tồn tại!")
                gv.ma_giao_vien = new_ma_gv

            if 'to_bo_mon' in data:
                gv.to_bo_mon = data['to_bo_mon']

            gv.save()
            return gv

    @staticmethod
    def delete(gv_id):
        gv = GiaoVien.objects.get(pk=gv_id)
        gv.user.trang_thai = False
        gv.user.save()

    @staticmethod
    def recover(gv_id):
        gv = GiaoVien.objects.get(pk=gv_id)
        gv.user.trang_thai = True
        gv.user.save()

    @staticmethod
    def export_template():
        """Tạo ra một file Excel mẫu trắng để điền danh sách Giáo viên"""
        df = pd.DataFrame(columns=['STT', 'Họ Tên', 'CCCD', 'Tên Đăng Nhập', 'Mật Khẩu', 'Tổ Bộ Môn'])

        # Điền sẵn 1 dòng dữ liệu mẫu chuẩn để người dùng dễ hình dung
        df.loc[0] = [1, 'Nguyễn Văn Toán', '001099123456', 'gvtoan', '123456', 'Tự Nhiên']

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Danh_Sach_Giao_Vien')

        output.seek(0)
        return output

    @staticmethod
    def import_excel(file_obj):
        try:
            df = pd.read_excel(file_obj)
        except Exception:
            raise ValueError("File đính kèm không đúng định dạng Excel (.xlsx)")

        # Kiểm tra các cột bắt buộc
        required_cols = ['Họ Tên', 'Tên Đăng Nhập']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"File Excel thiếu cột bắt buộc: '{col}'")

        all_row_errors = []
        success_count = 0

        try:
            with transaction.atomic():  # Lá chắn Transaction bảo vệ DB
                for index, row in df.iterrows():

                    row_num = int(str(index)) + 2
                    current_row_errors = []

                    # 1. CHUẨN HÓA DATA
                    clean_user_data = NguoiDungService.clean_excel_row(row)

                    # 2. VALIDATE TRÙNG LẶP
                    user_errors = NguoiDungService.validate_import_row(
                        username=clean_user_data['username'],
                        cccd=clean_user_data['cccd']
                    )
                    current_row_errors.extend(user_errors)

                    # 3. Kiểm tra riêng nghiệp vụ Giáo Viên
                    if not clean_user_data['ho_ten']:
                        current_row_errors.append("Họ tên giáo viên không được để trống.")

                    if current_row_errors:
                        all_row_errors.append({
                            "dong": row_num,
                            "ten_dang_nhap": clean_user_data['username'] or "Trống",
                            "loi": current_row_errors
                        })
                        continue

                    # 4. Tiến hành tạo nếu file sạch
                    if not all_row_errors:
                        user = NguoiDungService.create_profile(clean_user_data, vai_tro='giao_vien')

                        to_bo_mon_val = str(row.get('Tổ Bộ Môn', '')).strip()
                        to_bo_mon = '' if to_bo_mon_val == 'nan' else to_bo_mon_val

                        ma_gv = GiaoVienService._tao_ma_giao_vien()
                        GiaoVien.objects.create(user=user, ma_giao_vien=ma_gv, to_bo_mon=to_bo_mon)
                        success_count += 1

                # Kết thúc duyệt file: Nếu mảng gom lỗi có chứa phần tử, ném Exception để Rollback toàn bộ DB
                if all_row_errors:
                    raise ExcelImportException(error_details=all_row_errors)

        except ExcelImportException as e:
            raise e
        except Exception as e:
            raise ValueError(f"Lỗi hệ thống bất ngờ: {str(e)}")

        return success_count
