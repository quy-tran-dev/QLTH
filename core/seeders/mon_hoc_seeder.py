from core.services.mon_hoc_service import MonHocService
from core.models import MonHoc

class MonHocSeeder:
    @staticmethod
    def run(stdout):
        stdout.write("-> Đang xóa dữ liệu Môn Học cũ...")
        MonHoc.objects.all().delete()
        stdout.write("-> Đang khởi tạo 11 Môn Học...")

        danh_sach_mon = [
            {'ma_mon': 'TOAN', 'ten_mon': 'Toán Học', 'he_so': 2},
            {'ma_mon': 'VAN', 'ten_mon': 'Ngữ Văn', 'he_so': 2},
            {'ma_mon': 'ANH', 'ten_mon': 'Tiếng Anh', 'he_so': 2},
            {'ma_mon': 'LY', 'ten_mon': 'Vật Lý', 'he_so': 1},
            {'ma_mon': 'HOA', 'ten_mon': 'Hóa Học', 'he_so': 1},
            {'ma_mon': 'SINH', 'ten_mon': 'Sinh Học', 'he_so': 1},
            {'ma_mon': 'SU', 'ten_mon': 'Lịch Sử', 'he_so': 1},
            {'ma_mon': 'DIA', 'ten_mon': 'Địa Lý', 'he_so': 1},
            {'ma_mon': 'GDCD', 'ten_mon': 'Giáo Dục Công Dân', 'he_so': 1},
            {'ma_mon': 'TIN', 'ten_mon': 'Tin Học', 'he_so': 1},
            {'ma_mon': 'TD', 'ten_mon': 'Thể Dục', 'he_so': 1},
        ]

        for mon in danh_sach_mon:
            MonHocService.create(mon)

        stdout.write("-> Đã khởi tạo 11 Môn Học.")
