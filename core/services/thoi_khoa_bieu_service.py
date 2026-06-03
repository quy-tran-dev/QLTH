from datetime import date, timedelta
from django.core.exceptions import ValidationError
from core.models import ThoiKhoaBieu, GiaoVien, LopHoc, MonHoc
import pandas as pd


class ThoiKhoaBieuService:

    @staticmethod
    def validate_and_create_tkb(data: dict) -> ThoiKhoaBieu:
        # Sử dụng getattr để dọn sạch cảnh báo 'Unresolved attribute reference' của IDE
        gv = data.get('giao_vien')
        lop = data.get('lop_hoc')
        mon = data.get('mon_hoc')

        gv_id = getattr(gv, 'id', gv)
        lop_id = getattr(lop, 'id', lop)
        mon_id = getattr(mon, 'id', mon)

        ngay_hoc = data.get('ngay_hoc')
        tiet_hoc = data.get('tiet_hoc')
        thu_trong_tuan = data.get('thu_trong_tuan')
        ma_tkb = data.get('ma_tkb')

        # 1. Check trùng lịch Lớp học vào NGÀY ĐÓ, TIẾT ĐÓ
        if ThoiKhoaBieu.objects.filter(
                lop_hoc_id=lop_id,
                ngay_hoc=ngay_hoc,
                tiet_hoc=tiet_hoc
        ).exists():
            raise ValidationError(f"Lớp này đã có lịch học môn khác vào ngày {ngay_hoc}, Tiết {tiet_hoc} rồi!")

        # 2. Check trùng lịch Giáo viên vào NGÀY ĐÓ, TIẾT ĐÓ
        if ThoiKhoaBieu.objects.filter(
                giao_vien_id=gv_id,
                ngay_hoc=ngay_hoc,
                tiet_hoc=tiet_hoc
        ).exists():
            raise ValidationError(
                f"Giáo viên đã có lịch dạy lớp khác vào ngày {ngay_hoc}, Tiết {tiet_hoc}!")

        # 3. Đóng gói dữ liệu sạch với hậu tố _id để tránh lỗi ép kiểu instance của Django
        clean_data = {
            "ma_tkb": ma_tkb,
            "ngay_hoc": ngay_hoc,
            "thu_trong_tuan": thu_trong_tuan,
            "tiet_hoc": tiet_hoc,
            "giao_vien_id": gv_id,
            "lop_hoc_id": lop_id,
            "mon_hoc_id": mon_id
        }

        return ThoiKhoaBieu.objects.create(**clean_data)

    @staticmethod
    def clean_future_and_bulk_create(ma_tkb_cu: str, ngay_bat_dau: date, danh_sach_tiet_moi: list):
        # 1. Chỉ dọn dẹp các lịch học thuộc tương lai (>= ngay_bat_dau), bảo toàn lịch sử quá khứ
        ThoiKhoaBieu.objects.filter(
            ma_tkb=ma_tkb_cu,
            ngay_hoc__gte=ngay_bat_dau
        ).delete()

        # 2. Chuẩn bị dữ liệu và kiểm tra xung đột trước khi insert hàng loạt
        cac_doi_tuong_tkb = []
        for tiet in danh_sach_tiet_moi:
            ngay_tiet = tiet.get('ngay_hoc')
            tiet_num = tiet.get('tiet_hoc')

            # Hỗ trợ linh hoạt cả hai định dạng key: từ Postman JSON ("giao_vien") hoặc từ Excel Mapping ("giao_vien_id")
            gv_id = tiet.get('giao_vien_id') if tiet.get('giao_vien_id') is not None else tiet.get('giao_vien')
            lop_id = tiet.get('lop_hoc_id') if tiet.get('lop_hoc_id') is not None else tiet.get('lop_hoc')
            mon_id = tiet.get('mon_hoc_id') if tiet.get('mon_hoc_id') is not None else tiet.get('mon_hoc')

            # Thực hiện validate trùng chéo lịch trước khi thực hiện bulk_create
            if ThoiKhoaBieu.objects.filter(giao_vien_id=gv_id, ngay_hoc=ngay_tiet, tiet_hoc=tiet_num).exists():
                raise ValidationError(
                    f"Xung đột lịch: Giáo viên đã có lịch dạy vào ngày {ngay_tiet}, tiết {tiet_num}!")

            if ThoiKhoaBieu.objects.filter(lop_hoc_id=lop_id, ngay_hoc=ngay_tiet, tiet_hoc=tiet_num).exists():
                raise ValidationError(
                    f"Xung đột lịch: Lớp đã có môn học khác vào ngày {ngay_tiet}, tiết {tiet_num}!")

            # Tạo instance mẫu và gán giá trị khóa ngoại qua hậu tố _id chống crash hệ thống
            cac_doi_tuong_tkb.append(ThoiKhoaBieu(
                ma_tkb=tiet.get('ma_tkb'),
                ngay_hoc=ngay_tiet,
                thu_trong_tuan=tiet.get('thu_trong_tuan'),
                tiet_hoc=tiet_num,
                giao_vien_id=gv_id,
                lop_hoc_id=lop_id,
                mon_hoc_id=mon_id
            ))

        # Sử dụng bulk_create để đẩy toàn bộ danh sách xuống DB giúp tối ưu hóa hiệu năng
        return ThoiKhoaBieu.objects.bulk_create(cac_doi_tuong_tkb)


    @staticmethod
    def import_excel_sinh_lich(file_obj, ma_tkb_moi: str, ngay_bat_dau: date, ngay_ket_thuc: date,
                               ma_tkb_cu: str = None) -> int:
        try:
            # 1. Nếu có cung cấp mã cũ thì tiến hành dọn dẹp lịch tương lai của mã đó
            if ma_tkb_cu:
                ThoiKhoaBieu.objects.filter(ma_tkb=ma_tkb_cu, ngay_hoc__gte=ngay_bat_dau).delete()

            # 2. Đọc file Excel Khung Tuần
            df = pd.read_excel(file_obj)
            df = df.dropna(how='all')

            dict_giao_vien = {gv.ma_giao_vien: gv.id for gv in GiaoVien.objects.all()}
            dict_lop_hoc = {lh.ma_lop: lh.id for lh in LopHoc.objects.all()}
            dict_mon_hoc = {mh.ma_mon: mh.id for mh in MonHoc.objects.all()}

            # Lưu khung tuần vào một dictionary: {thu_trong_tuan: [danh_sach_tiet_cua_thu_do]}
            khung_tuan = {thu: [] for thu in range(2, 8)}

            for index, row in df.iterrows():
                stt_dong = int(str(index)) + 2
                thu = int(row['thu_trong_tuan'])

                m_gv, m_lop, m_mon = str(row['ma_giao_vien']).strip(), str(row['ma_lop']).strip(), str(
                    row['ma_mon']).strip()

                if m_gv not in dict_giao_vien: raise ValidationError(f"Dòng {stt_dong}: Không có GV [{m_gv}]")
                if m_lop not in dict_lop_hoc: raise ValidationError(f"Dòng {stt_dong}: Không có Lớp [{m_lop}]")
                if m_mon not in dict_mon_hoc: raise ValidationError(f"Dòng {stt_dong}: Không có Môn [{m_mon}]")

                khung_tuan[thu].append({
                    "tiet_hoc": int(row['tiet_hoc']),
                    "giao_vien_id": dict_giao_vien[m_gv],
                    "lop_hoc_id": dict_lop_hoc[m_lop],
                    "mon_hoc_id": dict_mon_hoc[m_mon]
                })

            # 3. NHÂN BẢN LỊCH THEO NGÀY (Từ ngày bắt đầu đến ngày kết thúc)
            cac_doi_tuong_tkb = []
            ngay_hien_tai = ngay_bat_dau

            while ngay_hien_tai <= ngay_ket_thuc:
                # Trong Python, weekday() trả về: 0 = Thứ 2, 1 = Thứ 3...
                # Do DB của mình Thứ 2 là 2, nên cộng thêm 2
                thu_cua_ngay = ngay_hien_tai.weekday() + 2

                # Nếu ngày hiện tại là ngày có trong khung tuần (không phải chủ nhật)
                if thu_cua_ngay in khung_tuan:
                    for tiet in khung_tuan[thu_cua_ngay]:

                        # Kiểm tra trùng chéo (bảo mật thêm 1 lớp)
                        gv_id = tiet["giao_vien_id"]
                        lop_id = tiet["lop_hoc_id"]
                        tiet_num = tiet["tiet_hoc"]

                        if ThoiKhoaBieu.objects.filter(giao_vien_id=gv_id, ngay_hoc=ngay_hien_tai,
                                                       tiet_hoc=tiet_num).exists():
                            raise ValidationError(
                                f"Xung đột! GV ID {gv_id} đã có lịch vào {ngay_hien_tai}, Tiết {tiet_num}")
                        if ThoiKhoaBieu.objects.filter(lop_hoc_id=lop_id, ngay_hoc=ngay_hien_tai,
                                                       tiet_hoc=tiet_num).exists():
                            raise ValidationError(
                                f"Xung đột! Lớp ID {lop_id} đã có môn học khác vào {ngay_hien_tai}, Tiết {tiet_num}")

                        cac_doi_tuong_tkb.append(ThoiKhoaBieu(
                            ma_tkb=ma_tkb_moi,
                            ngay_hoc=ngay_hien_tai,
                            thu_trong_tuan=thu_cua_ngay,
                            tiet_hoc=tiet_num,
                            giao_vien_id=gv_id,
                            lop_hoc_id=lop_id,
                            mon_hoc_id=tiet["mon_hoc_id"]
                        ))

                # Tiến lên ngày tiếp theo
                ngay_hien_tai += timedelta(days=1)

            # 4. Insert toàn bộ vào DB
            ThoiKhoaBieu.objects.bulk_create(cac_doi_tuong_tkb)
            return len(cac_doi_tuong_tkb)

        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise ValidationError(f"Lỗi: {str(e)}")