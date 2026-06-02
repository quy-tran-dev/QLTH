from django.core.management.base import BaseCommand
from core.models import NguoiDung

# Import đầy đủ cả 4 seeder đã được phân tách rạch ròi
from core.seeders.mon_hoc_seeder import MonHocSeeder
from core.seeders.giao_vien_seeder import GiaoVienSeeder
from core.seeders.lop_hoc_seeder import LopHocSeeder
from core.seeders.hoc_sinh_seeder import HocSinhSeeder

class Command(BaseCommand):
    help = 'Tự động khởi tạo dữ liệu mẫu (Seeder) chuẩn chỉnh cấu trúc phân rã OOP'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("=== BẮT ĐẦU QUÁ TRÌNH SEED DATA TOÀN HỆ THỐNG ==="))

        # 1. Clear sạch User hệ thống cũ (Trừ superuser)
        NguoiDung.objects.exclude(is_superuser=True).delete()

        # 2. Khởi tạo tài khoản Admin tối cao
        self.stdout.write("-> Khởi tạo tài khoản Quản Lý Hệ Thống...")
        NguoiDung.objects.create_user(
            username='admin', password='123456',
            ho_ten='Quản Trị Viên Hệ Thống', vai_tro='quan_ly', trang_thai=True
        )

        # 3. Tạo 11 Môn Học bám sát cấu trúc Bộ Giáo Dục
        MonHocSeeder.run(self.stdout)

        # 4. Tạo các Giáo viên bộ môn tự do (Toán, Văn...)
        GiaoVienSeeder.run(self.stdout)

        # 5. Tạo 15 Lớp Học riêng biệt (Nhận về danh sách lớp học vừa tạo)
        danh_sach_lop = LopHocSeeder.run(self.stdout)

        # 6. Truyền danh sách lớp sang cho Seeder học sinh tự xử lý nhét học sinh vào lớp
        HocSinhSeeder.run(self.stdout, danh_sach_lop)

        self.stdout.write(self.style.SUCCESS("=== CHÚC MỪNG! HỆ THỐNG ĐÃ SEED DỮ LIỆU ĐỒNG BỘ THÀNH CÔNG! ==="))