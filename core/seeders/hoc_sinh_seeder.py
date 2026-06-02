import random
from datetime import datetime
from core.services.hoc_sinh_service import HocSinhService
from core.models import HocSinh


class HocSinhSeeder:
    @staticmethod
    def run(stdout, cac_lop_da_tao: list):
        stdout.write("-> Đang dọn dẹp dữ liệu Học Sinh cũ...")
        HocSinh.objects.all().delete()

        stdout.write("-> Đang tự động sinh ngẫu nhiên Học Sinh cho 15 lớp học...")

        # 1. Khởi tạo các mảng dữ liệu để phối hợp tên ngẫu nhiên
        list_ho = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi']
        list_ten_lot = ['Thành', 'Văn', 'Thị', 'Minh', 'Hoàng', 'Tuyết', 'Khánh', 'Đức', 'Tuấn', 'Ngọc', 'Huyền']
        list_ten = ['Đông', 'Minh', 'An', 'Bình', 'Chi', 'Dũng', 'Hương', 'Hải', 'Khánh', 'Linh', 'Long', 'Nhi', 'Phúc',
                    'Quân', 'Sơn', 'Tâm', 'Trang', 'Tú', 'Vy']

        # Lấy năm hiện tại để tính năm sinh chuẩn xác theo từng Khối (Ví dụ hiện tại là 2026)
        nam_hien_tai = datetime.now().year

        # Số lượng học sinh bạn muốn sinh ra cho MỖI lớp (Ví dụ: 5 học sinh/lớp để test)
        so_hoc_sinh_moi_lop = 36
        stt_cccd = 100000  # Biến chạy để sinh số CCCD ngẫu nhiên không trùng nhau
        tong_so_hs_da_tao = 0

        for lop in cac_lop_da_tao:
            # Xác định khối lớp dựa vào ký tự đầu của mã lớp (Ví dụ: '10A1' -> khối = 10)
            try:
                khoi = int(lop.ma_lop[:2])
            except ValueError:
                khoi = 10  # Dự phòng nếu mã lớp không bắt đầu bằng số

            # Tính tuổi và năm sinh dựa theo logic bạn đưa ra
            # Lớp 10 -> 15 tuổi, Lớp 11 -> 16 tuổi, Lớp 12 -> 17 tuổi
            tuoi = 15 if khoi == 10 else (16 if khoi == 11 else 17)
            nam_sinh = nam_hien_tai - tuoi

            for i in range(so_hoc_sinh_moi_lop):
                # 2. Phối hợp ngẫu nhiên Họ + Tên lót + Tên
                ho = random.choice(list_ho)
                ten_lot = random.choice(list_ten_lot)
                ten = random.choice(list_ten)
                ho_ten = f"{ho} {ten_lot} {ten}"

                # Khối lớp 10A1 muốn giữ lại tài khoản cốt cán của bạn để test quyền
                if lop.ma_lop == '10A1' and i == 0:
                    username = 'dong'
                    ho_ten = 'Tô Huyền Đông'
                    cccd = '079012345634'
                else:
                    # Tạo username ngẫu nhiên theo cấu trúc: hs_malop_stt (Ví dụ: hs_10a1_1)
                    username = f"hs_{lop.ma_lop.lower()}_{i + 1}"
                    # Sinh CCCD dạng chuỗi chạy tăng dần để đảm bảo tính Unique toàn hệ thống
                    cccd = f"001099{stt_cccd}"
                    stt_cccd += 1

                # 3. Tạo ngày sinh ngẫu nhiên trong đúng năm sinh đã tính
                ngay_ngau_nhien = random.randint(1, 28)
                thang_ngau_nhien = random.randint(1, 12)
                ngay_sinh = datetime(year=nam_sinh, month=thang_ngau_nhien, day=ngay_ngau_nhien).date()

                # 4. Gom dữ liệu gọi tầng Service xử lý (Mã học sinh tự sinh trong Service như bạn nói)
                payload = {
                    'username': username,
                    'password': '123456',  # Mật khẩu mặc định như bạn yêu cầu
                    'ho_ten': ho_ten,
                    'cccd': cccd,
                    'ngay_sinh': ngay_sinh,
                    'lop_hoc_id': lop.id
                }

                try:
                    HocSinhService.create(payload)
                    tong_so_hs_da_tao += 1
                except Exception as e:
                    stdout.write(f"Bỏ qua dòng lỗi sinh học sinh: {str(e)}")

        stdout.write(f"Đã tự động sinh thành công {tong_so_hs_da_tao} học sinh chia đều cho 15 lớp!")