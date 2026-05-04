from core.models import LopHoc, GiaoVien


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
        # Dùng select_related join thẳng sang GiaoVien và NguoiDung để chống N+1 Query
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
        # Do cài SET_NULL ở model, xóa Lớp Học sẽ không xóa Học Sinh, chỉ update cột lop_hoc_id của HS thành null
        LopHoc.objects.get(pk=lop_hoc_id).delete()