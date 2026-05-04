from django.db import transaction
from core.models import NguoiDung, GiaoVien
from core.services import NguoiDungService
from datetime import datetime


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
        # 1 DÒNG ĐỂ CHECK TRÙNG LẶP CHO CẢ USERNAME & CCCD
        NguoiDungService.validate_unique(username=data.get('username'), cccd=data.get('cccd'))

        with transaction.atomic():
            user = NguoiDung.objects.create_user(
                username=data['username'],
                password=data.get('password', '123456'),
                ho_ten=data['ho_ten'],
                cccd=data.get('cccd'),
                vai_tro='giao_vien',  # Gán cứng role
                trang_thai=True  # Thường GV tạo xong cho hoạt động luôn
            )

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
            user = gv.user

            # 1 DÒNG ĐỂ CHECK TRÙNG (Loại trừ ID hiện tại)
            NguoiDungService.validate_unique(
                username=data.get('username'),
                cccd=data.get('cccd'),
                exclude_user_id=user.pk
            )

            # Cập nhật thông tin User
            if 'username' in data: user.username = data['username']
            if 'cccd' in data and data['cccd']: user.cccd = data['cccd']
            if 'ho_ten' in data: user.ho_ten = data['ho_ten']
            if 'trang_thai' in data:
                raw_status = data['trang_thai']
                user.trang_thai = raw_status.lower() in ['true', '1', 't', 'yes'] if isinstance(raw_status,
                                                                                                str) else bool(
                    raw_status)
            user.save()

            # Cập nhật thông tin Giáo Viên
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