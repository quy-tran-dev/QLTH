from core.models import ThoiKhoaBieu
from core.serializers.nghiep_vu_serializer import ThoiKhoaBieuSerializer


class ThoiKhoaBieuService:
    @staticmethod
    def create(data):
        # Logic check trùng lịch dạy của giáo viên
        if ThoiKhoaBieu.objects.filter(
                giao_vien_id=data['giao_vien'],
                thu_trong_tuan=data['thu_trong_tuan'],
                tiet_hoc=data['tiet_hoc']
        ).exists():
            raise ValueError("Giáo viên này đã có lịch dạy ở lớp khác vào thời gian này!")

        serializer = ThoiKhoaBieuSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @staticmethod
    def import_excel(file_obj):
        # TODO: Sẽ dùng Pandas đọc file Excel, bóc tách dòng, check trùng lặp
        # và insert hàng loạt (bulk_create) vào DB ở đây.
        pass