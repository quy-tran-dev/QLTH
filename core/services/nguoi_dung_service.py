from core.models import NguoiDung


class NguoiDungService:

    @staticmethod
    def validate_unique(username=None, cccd=None, exclude_user_id=None):
        """
        Hàm dùng chung để check trùng lặp Username và CCCD cho mọi Role.
        - Lúc Create: Không truyền exclude_user_id.
        - Lúc Update: Truyền ID của User đang sửa vào exclude_user_id để bỏ qua chính nó.
        """
        if username:
            query = NguoiDung.objects.filter(username=username)
            if exclude_user_id:
                query = query.exclude(pk=exclude_user_id)
            if query.exists():
                raise ValueError(f"Tên đăng nhập '{username}' đã có người sử dụng!")

        if cccd:
            query = NguoiDung.objects.filter(cccd=cccd)
            if exclude_user_id:
                query = query.exclude(pk=exclude_user_id)
            if query.exists():
                raise ValueError(f"Số CCCD '{cccd}' đã được đăng ký trong hệ thống!")