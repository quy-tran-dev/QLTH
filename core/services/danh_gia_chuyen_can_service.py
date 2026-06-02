from core.models import DanhGiaChuyenCan
from core.serializers.nghiep_vu_serializer import DanhGiaChuyenCanSerializer
from django.db import transaction


class DanhGiaChuyenCanService:
    @staticmethod
    def create(data, giao_vien_id):
        data['giao_vien_danh_gia'] = giao_vien_id
        serializer = DanhGiaChuyenCanSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @staticmethod
    def diem_danh_nhanh_lop(lop_hoc_id, giao_vien_id, danh_sach_vang_mat):
        """
        danh_sach_vang_mat: Dạng mảng chứa các object, ví dụ:
        [
            {"hoc_sinh_id": 5, "loai_vi_pham": "vang_khong_phep", "chi_tiet": "Cúp tiết"},
            {"hoc_sinh_id": 12, "loai_vi_pham": "tre", "chi_tiet": "Kẹt xe"}
        ]
        """
        with transaction.atomic():
            danh_gia_list = []
            for item in danh_sach_vang_mat:
                danh_gia_list.append(
                    DanhGiaChuyenCan(
                        hoc_sinh_id=item['hoc_sinh_id'],
                        lop_hoc_id=lop_hoc_id,
                        loai_vi_pham=item['loai_vi_pham'],
                        chi_tiet=item.get('chi_tiet', ''),
                        giao_vien_danh_gia_id=giao_vien_id
                    )
                )

            # Dùng bulk_create để insert cùng lúc, tối ưu tốc độ Database
            if danh_gia_list:
                DanhGiaChuyenCan.objects.bulk_create(danh_gia_list)

            return f"Đã ghi nhận vắng/trễ cho {len(danh_gia_list)} học sinh."