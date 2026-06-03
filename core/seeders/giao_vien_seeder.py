import random
from core.services.giao_vien_service import GiaoVienService  # Thay bằng tên file thực tế của bạn
from core.models import GiaoVien


class GiaoVienSeeder:
    @staticmethod
    def run(stdout):
        stdout.write("-> Đang dọn dẹp dữ liệu Giáo Viên cũ...")
        GiaoVien.objects.all().delete()

        stdout.write("-> Đang tự động sinh Giáo Viên theo định ngạch môn học...")

        # 1. Mảng dữ liệu thô để phối hợp tên ngẫu nhiên cho Thầy/Cô
        list_ho = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi']
        list_ten_lot_nam = ['Văn', 'Minh', 'Đức', 'Tuấn', 'Hoàng', 'Quốc', 'Thành', 'Xuân', 'Hải']
        list_ten_lot_nu = ['Thị', 'Ngọc', 'Tuyết', 'Huyền', 'Trà', 'Như', 'Bích', 'Phương', 'Mai']

        list_ten_nam = [ 'Sinh', 'Hùng', 'Cường', 'Dũng', 'Sơn', 'Long', 'Phúc', 'An']
        list_ten_nu = ['Vân', 'Anh', 'Linh', 'Nhi', 'Vy', 'Trang', 'Hương', 'My', 'Chi', 'Tú']

        # 2. Định nghĩa số lượng giáo viên cần sinh cho từng Mã Môn Học
        cau_hinh_danh_ngach = {
            'TOAN': 5,
            'VAN': 5,
            'ANH': 5,
            'LY': 3,
            'HOA': 3,
            'SINH': 3,
            'SU': 3,
            'DIA': 3,
            'GDCD': 3,
            'TIN': 2,
            'TD': 2
        }

        # Các môn thuộc tổ Xã Hội (để tự động phân tổ bộ môn)
        mon_xa_hoi = ['VAN', 'ANH', 'SU', 'DIA', 'GDCD']

        stt_cccd = 200000  # Vùng CCCD riêng cho giáo viên (Học sinh dùng đầu 100000)
        tong_so_gv_da_tao = 0

        # Biến hứng giáo viên Toán và Văn đầu tiên để trả về làm giáo viên chủ nhiệm mẫu (nếu file tổng cần)
        gv_toan_mau = None
        gv_van_mau = None

        # Duyệt qua từng cấu hình môn học
        for ma_mon, so_luong in cau_hinh_danh_ngach.items():

            # Tự động xác định Tổ bộ môn dựa vào mã môn học
            if ma_mon == 'TD':
                to_bo_mon = 'Năng Khiếu'
            elif ma_mon in mon_xa_hoi:
                to_bo_mon = 'Xã Hội'
            else:
                to_bo_mon = 'Tự Nhiên'

            for i in range(so_luong):
                # Quyết định ngẫu nhiên giới tính để phối hợp tên cho chuẩn thực tế
                gioi_tinh = random.choice(['Nam', 'Nữ'])

                ho = random.choice(list_ho)
                if gioi_tinh == 'Nam':
                    ten_lot = random.choice(list_ten_lot_nam)
                    # Ưu tiên lấy tên trùng với môn học cho giáo viên đầu tiên để dễ nhận diện khi test
                    ten = ma_mon.capitalize() if (i == 0 and ma_mon.capitalize() in list_ten_nam) else random.choice(
                        list_ten_nam)
                else:
                    ten_lot = random.choice(list_ten_lot_nu)
                    ten = ma_mon.capitalize() if (i == 0 and ma_mon.capitalize() in list_ten_nu) else random.choice(
                        list_ten_nu)

                ho_ten = f"{ho} {ten_lot} {ten}"

                # Tạo username có phân biệt môn và số thứ tự (Ví dụ: gv_toan_1, gv_anh_3)
                username = f"gv_{ma_mon.lower()}_{i + 1}"
                cccd = f"001099{stt_cccd}"
                stt_cccd += 1

                payload = {
                    'username': username,
                    'password': '123456',  # Mật khẩu mặc định đúng bài bạn gán
                    'ho_ten': ho_ten,
                    'cccd': cccd,
                    'to_bo_mon': to_bo_mon,
                    'bo_mon': ma_mon,
                }

                try:
                    # Gọi Service xử lý tạo tài khoản người dùng và sinh mã GV tự động
                    gv_obj = GiaoVienService.create(payload)
                    tong_so_gv_da_tao += 1

                    # Lưu lại giáo viên Toán và Văn đầu tiên để trả về cho file tổng điều phối
                    if ma_mon == 'TOAN' and gv_toan_mau is None:
                        gv_toan_mau = gv_obj
                    elif ma_mon == 'VAN' and gv_van_mau is None:
                        gv_van_mau = gv_obj

                except Exception as e:
                    stdout.write(f"Bỏ qua giáo viên lỗi: {str(e)}")

        stdout.write(f"Đã tự động sinh thành công {tong_so_gv_da_tao} Giáo Viên bộ môn vào hệ thống!")

        # Trả về 2 giáo viên mẫu để không làm gãy logic nhận tham số của file seed tổng
        return gv_toan_mau, gv_van_mau