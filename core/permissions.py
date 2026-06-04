from rest_framework.permissions import BasePermission

from core.models import ThoiKhoaBieu


class IsQuanLy(BasePermission):
    message = "Bạn không có quyền thực hiện hành động này. Yêu cầu quyền Quản Lý!"

    def has_permission(self, request, view):
        # Đổi request.user.vai_tro thành getattr(request.user, 'vai_tro', None)
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'vai_tro', None) == 'quan_ly'
        )

class IsGiaoVien(BasePermission):
    message = "Yêu cầu quyền Giáo Viên!"

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'vai_tro', None) == 'giao_vien'
        )

class IsHocSinh(BasePermission):
    message = "Yêu cầu quyền Học Sinh!"

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'vai_tro', None) == 'hoc_sinh'
        )

class IsQuanLyOrGiaoVien(BasePermission):
    message = "Yêu cầu quyền Quản Lý hoặc Giáo Viên!"

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'vai_tro', None) in ['quan_ly', 'giao_vien']
        )

class IsGiaoVienCuaLop(BasePermission):
    message = "CẢNH BÁO: Bạn không được phân công giảng dạy lớp này, không có quyền can thiệp!"

    def has_permission(self, request, view):
        # 1. Chắc chắn phải là Giáo viên
        if getattr(request.user, 'vai_tro', None) != 'giao_vien':
            return False

        # 2. Tìm ID của lớp học mà request đang muốn chọc vào
        # (Nó có thể nằm trong URL params hoặc trong Body Data)
        lop_hoc_id = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            lop_hoc_id = request.data.get('lop_hoc_id') # Tìm trong JSON body
        else:
            # Nếu GET theo URL (ví dụ: /api/lop-hoc/5/diem-danh/)
            lop_hoc_id = view.kwargs.get('lop_hoc_pk') or view.kwargs.get('pk')

        # Nếu API này không dính dáng gì tới lop_hoc_id thì bỏ qua check
        if not lop_hoc_id:
            return True

        # 3. Kiểm tra bảng Thời Khóa Biểu
        # Xem user này có dạy lớp học này không?
        co_day_lop_nay = ThoiKhoaBieu.objects.filter(
            giao_vien__user=request.user, # Lọc theo User đang đăng nhập
            lop_hoc_id=lop_hoc_id         # Lọc theo Lớp mà họ muốn thao tác
        ).exists()

        # Thêm đặc quyền: Nếu là Giáo viên chủ nhiệm của lớp đó thì có quyền tuyệt đối
        from core.models import LopHoc
        la_chu_nhiem = LopHoc.objects.filter(
            id=lop_hoc_id,
            giao_vien_chu_nhiem__user=request.user
        ).exists()

        # Pass nếu là GV dạy môn đó HOẶC là GV chủ nhiệm
        return co_day_lop_nay or la_chu_nhiem