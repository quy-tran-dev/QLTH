from datetime import date, timedelta
from django.core.exceptions import ValidationError
from core.models import ThoiKhoaBieu, GiaoVien, LopHoc, MonHoc
import pandas as pd


class ThoiKhoaBieuService:

    @staticmethod
    def validate_and_create_tkb(data: dict) -> ThoiKhoaBieu:
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

        if ThoiKhoaBieu.objects.filter(
                lop_hoc_id=lop_id,
                ngay_hoc=ngay_hoc,
                tiet_hoc=tiet_hoc
        ).exists():
            raise ValidationError(f"Lớp này đã có lịch học môn khác vào ngày {ngay_hoc}, Tiết {tiet_hoc} rồi!")

        if ThoiKhoaBieu.objects.filter(
                giao_vien_id=gv_id,
                ngay_hoc=ngay_hoc,
                tiet_hoc=tiet_hoc
        ).exists():
            raise ValidationError(
                f"Giáo viên đã có lịch dạy lớp khác vào ngày {ngay_hoc}, Tiết {tiet_hoc}!")

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
        ThoiKhoaBieu.objects.filter(
            ma_tkb=ma_tkb_cu,
            ngay_hoc__gte=ngay_bat_dau
        ).delete()

        cac_doi_tuong_tkb = []
        for tiet in danh_sach_tiet_moi:
            ngay_tiet = tiet.get('ngay_hoc')
            tiet_num = tiet.get('tiet_hoc')

            gv_id = tiet.get('giao_vien_id') if tiet.get('giao_vien_id') is not None else tiet.get('giao_vien')
            lop_id = tiet.get('lop_hoc_id') if tiet.get('lop_hoc_id') is not None else tiet.get('lop_hoc')
            mon_id = tiet.get('mon_hoc_id') if tiet.get('mon_hoc_id') is not None else tiet.get('mon_hoc')

            if ThoiKhoaBieu.objects.filter(giao_vien_id=gv_id, ngay_hoc=ngay_tiet, tiet_hoc=tiet_num).exists():
                raise ValidationError(
                    f"Xung đột lịch: Giáo viên đã có lịch dạy vào ngày {ngay_tiet}, tiết {tiet_num}!")

            if ThoiKhoaBieu.objects.filter(lop_hoc_id=lop_id, ngay_hoc=ngay_tiet, tiet_hoc=tiet_num).exists():
                raise ValidationError(
                    f"Xung đột lịch: Lớp đã có môn học khác vào ngày {ngay_tiet}, tiết {tiet_num}!")

            cac_doi_tuong_tkb.append(ThoiKhoaBieu(
                ma_tkb=tiet.get('ma_tkb'),
                ngay_hoc=ngay_tiet,
                thu_trong_tuan=tiet.get('thu_trong_tuan'),
                tiet_hoc=tiet_num,
                giao_vien_id=gv_id,
                lop_hoc_id=lop_id,
                mon_hoc_id=mon_id
            ))

        return ThoiKhoaBieu.objects.bulk_create(cac_doi_tuong_tkb)


    @staticmethod
    def import_excel_sinh_lich(file_obj, ma_tkb_moi: str, ngay_bat_dau: date, ngay_ket_thuc: date,
                               ma_tkb_cu: str = None) -> int:
        try:
            if ma_tkb_cu:
                ThoiKhoaBieu.objects.filter(ma_tkb=ma_tkb_cu, ngay_hoc__gte=ngay_bat_dau).delete()

            df = pd.read_excel(file_obj)
            df = df.dropna(how='all')

            dict_giao_vien = {gv.ma_giao_vien: gv.id for gv in GiaoVien.objects.all()}
            dict_lop_hoc = {lh.ma_lop: lh.id for lh in LopHoc.objects.all()}
            dict_mon_hoc = {mh.ma_mon: mh.id for mh in MonHoc.objects.all()}

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
                    "mon_hoc_id": dict_mon_hoc[m_mon],
                    "ten_hien_thi_gv": m_gv,
                    "ten_hien_thi_lop": m_lop
                })

            cac_doi_tuong_tkb = []
            ngay_hien_tai = ngay_bat_dau

            while ngay_hien_tai <= ngay_ket_thuc:
                thu_cua_ngay = ngay_hien_tai.weekday() + 2

                if thu_cua_ngay in khung_tuan:
                    for tiet in khung_tuan[thu_cua_ngay]:

                        gv_id = tiet["giao_vien_id"]
                        lop_id = tiet["lop_hoc_id"]
                        tiet_num = tiet["tiet_hoc"]

                        gv_ten = tiet["ten_hien_thi_gv"]
                        lop_ten = tiet["ten_hien_thi_lop"]
                        ngay_format = ngay_hien_tai.strftime('%d/%m/%Y')

                        if ThoiKhoaBieu.objects.filter(giao_vien_id=gv_id, ngay_hoc=ngay_hien_tai,
                                                       tiet_hoc=tiet_num).exists():
                            raise ValidationError(
                                f"Xung đột! Giáo viên [{gv_ten}] đã có lịch dạy lớp khác vào ngày {ngay_format}, Tiết {tiet_num}")

                        if ThoiKhoaBieu.objects.filter(lop_hoc_id=lop_id, ngay_hoc=ngay_hien_tai,
                                                       tiet_hoc=tiet_num).exists():
                            raise ValidationError(
                                f"Xung đột! Lớp [{lop_ten}] đã có lịch học môn khác vào ngày {ngay_format}, Tiết {tiet_num}")

                        cac_doi_tuong_tkb.append(ThoiKhoaBieu(
                            ma_tkb=ma_tkb_moi,
                            ngay_hoc=ngay_hien_tai,
                            thu_trong_tuan=thu_cua_ngay,
                            tiet_hoc=tiet_num,
                            giao_vien_id=gv_id,
                            lop_hoc_id=lop_id,
                            mon_hoc_id=tiet["mon_hoc_id"]
                        ))

                ngay_hien_tai += timedelta(days=1)

            ThoiKhoaBieu.objects.bulk_create(cac_doi_tuong_tkb)
            return len(cac_doi_tuong_tkb)

        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise ValidationError(f"Lỗi: {str(e)}")