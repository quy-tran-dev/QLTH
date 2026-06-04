from datetime import timedelta

from rest_framework_simplejwt.tokens import AccessToken

from core.models import NguoiDung


class NguoiDungService:

    @staticmethod
    def validate_unique(username=None, cccd=None, exclude_user_id=None):

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

    @staticmethod
    def create_profile(data, vai_tro, trang_thai=True):

        NguoiDungService.validate_unique(username=data.get('username'), cccd=data.get('cccd'))

        return NguoiDung.objects.create_user(
            username=data['username'],
            password=data.get('password', '123456'),  # Pass mặc định nếu không truyền
            ho_ten=data['ho_ten'],
            cccd=data.get('cccd'),
            vai_tro=vai_tro,
            trang_thai=trang_thai
        )

    @staticmethod
    def update_profile(user, data):
        NguoiDungService.validate_unique(
            username=data.get('username'),
            cccd=data.get('cccd'),
            exclude_user_id=user.pk
        )

        if 'username' in data: user.username = data['username']
        if 'cccd' in data and data['cccd']: user.cccd = data['cccd']
        if 'ho_ten' in data: user.ho_ten = data['ho_ten']
        if 'trang_thai' in data:
            raw_status = data['trang_thai']
            user.trang_thai = raw_status.lower() in ['true', '1', 't', 'yes'] if isinstance(raw_status, str) else bool(
                raw_status)

        user.save()
        return user

    @staticmethod
    def generate_reset_password_token(username: str) -> str:
        try:
            user = NguoiDung.objects.get(username=username, trang_thai=True)
        except NguoiDung.DoesNotExist:
            raise ValueError("Tên đăng nhập không tồn tại hoặc tài khoản đã bị khóa!")

        token = AccessToken.for_user(user)

        token.set_exp(lifetime=timedelta(minutes=15))

        token['action'] = 'reset_password'

        return str(token)

    @staticmethod
    def reset_password_with_token(token_str: str, new_password: str):
        if not new_password or len(new_password) < 6:
            raise ValueError("Mật khẩu mới phải từ 6 ký tự trở lên!")

        try:
            token = AccessToken(token_str)

            if token.get('action') != 'reset_password':
                raise ValueError("Mã xác thực không đúng mục đích!")

            user_id = token.get('user_id')
            user = NguoiDung.objects.get(pk=user_id, trang_thai=True)

        except Exception:
            raise ValueError("Mã xác thực (Token) không hợp lệ hoặc đã hết hạn!")

        user.set_password(new_password)
        user.save()
        return user

    @staticmethod
    def clean_excel_row(row) -> dict:

        username = str(row.get('Tên Đăng Nhập', '')).strip()
        ho_ten = str(row.get('Họ Tên', '')).strip()

        cccd_val = str(row.get('CCCD', '')).strip()
        cccd = None if (cccd_val == 'nan' or not cccd_val) else cccd_val

        mat_khau_val = str(row.get('Mật Khẩu', '123456')).strip()
        password = '123456' if (mat_khau_val == 'nan' or not mat_khau_val) else mat_khau_val

        return {
            'username': username,
            'ho_ten': ho_ten,
            'cccd': cccd,
            'password': password
        }

    @staticmethod
    def validate_import_row(username: str, cccd: str = None) -> list:

        row_errors = []

        if not username or username == 'nan':
            row_errors.append("Tên đăng nhập không được để trống.")
        elif NguoiDung.objects.filter(username=username).exists():
            row_errors.append(f"Tên đăng nhập '{username}' đã tồn tại trên hệ thống.")

        if cccd and cccd != 'nan':
            if NguoiDung.objects.filter(cccd=cccd).exists():
                row_errors.append(f"Số CCCD '{cccd}' đã được đăng ký bởi tài khoản khác.")

        return row_errors

