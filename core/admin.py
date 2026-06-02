from django.contrib import admin
from core.models import NguoiDung, HocSinh, GiaoVien, LopHoc, MonHoc, BangDiem

# 1. Đăng ký model Người Dùng Custom của bạn
@admin.register(NguoiDung)
class NguoiDungAdmin(admin.ModelAdmin):
    list_display = ('username', 'ho_ten', 'vai_tro', 'trang_thai', 'is_staff')
    list_filter = ('vai_tro', 'trang_thai')
    search_fields = ('username', 'ho_ten', 'cccd')

# 2. Đăng ký các model nghiệp vụ còn lại
@admin.register(LopHoc)
class LopHocAdmin(admin.ModelAdmin):
    list_display = ('ma_lop', 'ten_lop', 'nam_hoc', 'giao_vien_chu_nhiem')
    search_fields = ('ma_lop', 'ten_lop')

@admin.register(HocSinh)
class HocSinhAdmin(admin.ModelAdmin):
    list_display = ('ma_hoc_sinh', 'get_ho_ten', 'lop_hoc')
    search_fields = ('ma_hoc_sinh', 'user__ho_ten')

    # Hàm helper để hiển thị cột Họ tên lấy từ bảng User liên kết
    def get_ho_ten(self, obj):
        return obj.user.ho_ten
    get_ho_ten.short_description = 'Họ và Tên'

@admin.register(GiaoVien)
class GiaoVienAdmin(admin.ModelAdmin):
    list_display = ('ma_giao_vien', 'get_ho_ten', 'to_bo_mon')
    search_fields = ('ma_giao_vien', 'user__ho_ten')

    def get_ho_ten(self, obj):
        return obj.user.ho_ten
    get_ho_ten.short_description = 'Họ và Tên'

@admin.register(MonHoc)
class MonHocAdmin(admin.ModelAdmin):
    list_display = ('ma_mon', 'ten_mon', 'he_so')

@admin.register(BangDiem)
class BangDiemAdmin(admin.ModelAdmin):
    # Sửa 'hoc_sh' thành 'hoc_sinh' (hoặc tên chính xác bạn đặt trong models.py)
    list_display = ('hoc_sinh', 'mon_hoc', 'hoc_ky', 'diem_15p', 'diem_giua_ky', 'diem_cuoi_ky')
    list_filter = ('hoc_ky', 'mon_hoc')