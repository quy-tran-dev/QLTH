from django.db import models
from django.contrib.auth.models import AbstractUser


# 1. BẢNG NGƯỜI DÙNG
class NguoiDung(AbstractUser):
    VAI_TRO_CHOICES = (
        ('quan_ly', 'Quản Lý'),
        ('giao_vien', 'Giáo Viên'),
        ('hoc_sinh', 'Học Sinh'),
    )

    cccd = models.CharField(max_length=12, unique=True, null=True, blank=True)
    ho_ten = models.CharField(max_length=100)
    vai_tro = models.CharField(max_length=20, choices=VAI_TRO_CHOICES)
    trang_thai = models.BooleanField(default=True)  # True = Đang hoạt động, False = Khóa

    def __str__(self):
        return self.username


# 2. BẢNG MÔN HỌC
class MonHoc(models.Model):
    ma_mon = models.CharField(max_length=20, unique=True)
    ten_mon = models.CharField(max_length=100)
    he_so = models.IntegerField(default=1)  # Hệ số điểm (Ví dụ Toán x2)

    def __str__(self):
        return self.ten_mon


# 3. BẢNG GIÁO VIÊN
class GiaoVien(models.Model):
    user = models.OneToOneField(NguoiDung, on_delete=models.CASCADE, related_name='giao_vien_profile')
    ma_giao_vien = models.CharField(max_length=20, unique=True)
    to_bo_mon = models.CharField(max_length=100, null=True, blank=True)  # VD: Tổ Toán - Tin
    bo_mon = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.ma_giao_vien


# 4. BẢNG LỚP HỌC (Ví dụ: 10A1, 11B2)
class LopHoc(models.Model):
    ma_lop = models.CharField(max_length=20, unique=True)
    ten_lop = models.CharField(max_length=50)
    nam_hoc = models.CharField(max_length=20)  # VD: 2025-2026
    giao_vien_chu_nhiem = models.ForeignKey(GiaoVien, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='lop_chu_nhiem')

    def __str__(self):
        return self.ma_lop


# 5. BẢNG HỌC SINH
class HocSinh(models.Model):
    user = models.OneToOneField(NguoiDung, on_delete=models.CASCADE, related_name='hoc_sinh_profile')
    ma_hoc_sinh = models.CharField(max_length=20, unique=True)

    lop_hoc = models.ForeignKey(LopHoc, on_delete=models.SET_NULL, null=True, blank=True, related_name='danh_sach_hoc_sinh')

    def __str__(self):
        return self.ma_hoc_sinh


# 6. BẢNG ĐIỂM SỐ (Dùng cho tính năng Excel sau này)
class BangDiem(models.Model):
    hoc_sinh = models.ForeignKey(HocSinh, on_delete=models.CASCADE, related_name='bang_diem')
    mon_hoc = models.ForeignKey(MonHoc, on_delete=models.CASCADE, related_name='diem_cac_lop')
    hoc_ky = models.IntegerField(choices=((1, 'Học kỳ 1'), (2, 'Học kỳ 2')))

    # Cho phép null=True để giáo viên tạo dòng trước, nhập điểm sau
    diem_15p = models.FloatField(null=True, blank=True)
    diem_giua_ky = models.FloatField(null=True, blank=True)
    diem_cuoi_ky = models.FloatField(null=True, blank=True)

    class Meta:
        # RÀNG BUỘC CỰC KỲ QUAN TRỌNG: 1 học sinh chỉ có 1 bảng điểm Toán trong 1 học kỳ
        unique_together = ['hoc_sinh', 'mon_hoc', 'hoc_ky']

    def __str__(self):
        return f"{self.hoc_sinh.ma_hoc_sinh} - {self.mon_hoc.ten_mon} - HK{self.hoc_ky}"


# 7. BẢNG THỜI KHÓA BIỂU (PHÂN CÔNG GIẢNG DẠY)
class ThoiKhoaBieu(models.Model):
    THU_CHOICES = (
        (2, 'Thứ 2'), (3, 'Thứ 3'), (4, 'Thứ 4'),
        (5, 'Thứ 5'), (6, 'Thứ 6'), (7, 'Thứ 7'),
    )

    giao_vien = models.ForeignKey(GiaoVien, on_delete=models.CASCADE, related_name='lich_day')
    lop_hoc = models.ForeignKey(LopHoc, on_delete=models.CASCADE, related_name='thoi_khoa_bieu')
    mon_hoc = models.ForeignKey(MonHoc, on_delete=models.CASCADE)

    ma_tkb = models.CharField(max_length=50, help_text="VD: TKB_KHOI10_THANG6_2026")
    ngay_hoc = models.DateField()  # Ngày cụ thể: 2026-06-08
    thu_trong_tuan = models.IntegerField(choices=THU_CHOICES)
    tiet_hoc = models.IntegerField()  # Tiết 1 -> 10

    class Meta:
        unique_together = ['giao_vien', 'ngay_hoc', 'tiet_hoc']

    def __str__(self):
        return f"{self.giao_vien.user.ho_ten} dạy {self.lop_hoc.ten_lop} - Tiết {self.tiet_hoc} Thứ {self.thu_trong_tuan} - Ngày {self.ngay_hoc}"
