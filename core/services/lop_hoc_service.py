from core.models import LopHoc, GiaoVien, HocSinh
import pandas as pd
from io import BytesIO

class LopHocService:
    @staticmethod
    def create(data):
        if LopHoc.objects.filter(ma_lop=data.get('ma_lop')).exists():
            raise ValueError(f"Mã lớp '{data.get('ma_lop')}' đã tồn tại!")

        gv_chu_nhiem = None
        if data.get('giao_vien_chu_nhiem_id'):
            try:
                gv_chu_nhiem = GiaoVien.objects.get(pk=data['giao_vien_chu_nhiem_id'])
            except GiaoVien.DoesNotExist:
                raise ValueError("Giáo viên chủ nhiệm không tồn tại!")

        return LopHoc.objects.create(
            ma_lop=data['ma_lop'],
            ten_lop=data['ten_lop'],
            nam_hoc=data['nam_hoc'],
            giao_vien_chu_nhiem=gv_chu_nhiem
        )

    @staticmethod
    def list():
        return LopHoc.objects.select_related('giao_vien_chu_nhiem', 'giao_vien_chu_nhiem__user').all()

    @staticmethod
    def get(lop_hoc_id):
        return LopHoc.objects.select_related('giao_vien_chu_nhiem', 'giao_vien_chu_nhiem__user').get(pk=lop_hoc_id)

    @staticmethod
    def update(lop_hoc_id, data):
        lop_hoc = LopHoc.objects.get(pk=lop_hoc_id)

        if 'ma_lop' in data:
            if LopHoc.objects.filter(ma_lop=data['ma_lop']).exclude(pk=lop_hoc_id).exists():
                raise ValueError(f"Mã lớp '{data['ma_lop']}' đã tồn tại!")
            lop_hoc.ma_lop = data['ma_lop']

        if 'ten_lop' in data: lop_hoc.ten_lop = data['ten_lop']
        if 'nam_hoc' in data: lop_hoc.nam_hoc = data['nam_hoc']

        if 'giao_vien_chu_nhiem_id' in data:
            if not data['giao_vien_chu_nhiem_id']:
                lop_hoc.giao_vien_chu_nhiem = None
            else:
                try:
                    lop_hoc.giao_vien_chu_nhiem = GiaoVien.objects.get(pk=data['giao_vien_chu_nhiem_id'])
                except GiaoVien.DoesNotExist:
                    raise ValueError("Giáo viên chủ nhiệm không tồn tại!")

        lop_hoc.save()
        return lop_hoc

    @staticmethod
    def delete(lop_hoc_id):
        LopHoc.objects.get(pk=lop_hoc_id).delete()

    @staticmethod
    def export_danh_sach_hoc_sinh(ma_lop: str):

        try:
            lop = LopHoc.objects.get(ma_lop=ma_lop)
        except LopHoc.DoesNotExist:
            raise ValueError(f"Không tìm thấy lớp học nào có mã '{ma_lop}'")

        hoc_sinh_list = HocSinh.objects.filter(lop_hoc=lop).select_related('user')

        data_rows = []
        for index, hs in enumerate(hoc_sinh_list):
            data_rows.append({
                'STT': index + 1,
                'Mã Học Sinh': hs.ma_hoc_sinh,
                'Họ Tên': hs.user.ho_ten,
                'Tên Đăng Nhập': hs.user.username,
                'Số CCCD': hs.user.cccd if hs.user.cccd else 'Chưa cập nhật',
                'Trạng Thái': 'Đang học' if hs.user.trang_thai else 'Đã nghỉ/Khóa'
            })

        df = pd.DataFrame(data_rows)

        if df.empty:
            df = pd.DataFrame(columns=['STT', 'Mã Học Sinh', 'Họ Tên', 'Tên Đăng Nhập', 'Số CCCD', 'Trạng Thái'])

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=f"Danh_Sach_Lop_{ma_lop}")

        output.seek(0)
        filename = f"Danh_Sach_Hoc_Sinh_Lop_{ma_lop}.xlsx"
        return output, filename