from django.db import transaction
from core.models import NguoiDung, HocSinh, LopHoc  # Nhớ import thêm LopHoc
from datetime import datetime

from core.services import NguoiDungService


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
        NguoiDungService.validate_unique(username=data.get('username'), cccd=data.get('cccd'))

        # KIỂM TRA LỚP HỌC (NẾU CÓ TRUYỀN VÀO)
        lop_hoc_obj = None
        if data.get('lop_hoc_id'):
            try:
                lop_hoc_obj = LopHoc.objects.get(pk=data['lop_hoc_id'])
            except LopHoc.DoesNotExist:
                raise ValueError(f"Lớp học không tồn tại!")

        with transaction.atomic():
            user = NguoiDung.objects.create_user(
                username=data['username'],
                password=data.get('password', '123456'),
                ho_ten=data['ho_ten'],
                cccd=data.get('cccd'),
                vai_tro='hoc_sinh',
                trang_thai=True  # Học sinh mới tạo mình cứ set True cho dễ test nhé
            )
            ma_tu_dong = HocSinhService._tao_ma_hoc_sinh(data.get('nien_khoa'))

            # Gán thêm biến lop_hoc_obj vào đây
            return HocSinh.objects.create(user=user, ma_hoc_sinh=ma_tu_dong, lop_hoc=lop_hoc_obj)

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
            user = student.user

            NguoiDungService.validate_unique(
                username=data.get('username'),
                cccd=data.get('cccd'),
                exclude_user_id=user.pk
            )

            if 'username' in data:user.username = data['username']
            if 'cccd' in data:user.cccd = data['cccd']
            if 'ho_ten' in data: user.ho_ten = data['ho_ten']
            if 'trang_thai' in data:
                raw_status = data['trang_thai']
                user.trang_thai = raw_status.lower() in ['true', '1', 't', 'yes'] if isinstance(raw_status, str) else bool(raw_status)
            user.save()

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