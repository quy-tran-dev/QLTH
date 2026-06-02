from core.services.giao_vien_service import GiaoVienService
from core.services.lop_hoc_service import LopHocService
from core.models import LopHoc


class LopHocSeeder:
    @staticmethod
    def run(stdout) -> list:
        stdout.write("-> Đang dọn dẹp dữ liệu Lớp Học cũ...")
        LopHoc.objects.all().delete()

        stdout.write("-> Đang tự động cấu hình 15 Lớp Học & Giáo Viên Chủ Nhiệm...")

        # Cấu trúc trường học: 3 Khối x 5 Lớp (A1 -> A5) = 15 Lớp
        khoi_hoc = [10, 11, 12]
        phong_hoc = ['A1', 'A2', 'A3', 'A4', 'A5']
        cac_lop_da_tao = []

        stt_gv = 1
        for khoi in khoi_hoc:
            for p in phong_hoc:
                ten_lop_choosed = f"{khoi}{p}"  # VD: 10A1, 11A5, 12A2

                # 1. Tạo Giáo viên chủ nhiệm độc bản cho từng lớp để không vi phạm ràng buộc unique
                gv_chu_nhiem = GiaoVienService.create({
                    'username': f'gv_cn_{ten_lop_choosed.lower()}',
                    'password': '123456',
                    'ho_ten': f'Giáo Viên Chủ Nhiệm {ten_lop_choosed}',
                    'cccd': f'001099{stt_gv:06d}',  # Sinh CCCD tăng dần không lo trùng lặp
                    'to_bo_mon': 'Cơ Bản'
                })
                stt_gv += 1

                # 2. Tạo Lớp học gắn với Giáo viên chủ nhiệm đó
                lop_obj = LopHocService.create({
                    'ma_lop': ten_lop_choosed,
                    'ten_lop': ten_lop_choosed,
                    'nam_hoc': '2025-2026',
                    'giao_vien_chu_nhiem_id': gv_chu_nhiem.id
                })
                cac_lop_da_tao.append(lop_obj)

        stdout.write(f"Đã tạo thành công {len(cac_lop_da_tao)} lớp học từ Khối 10 đến Khối 12.")
        return cac_lop_da_tao