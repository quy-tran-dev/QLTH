from core.models import MonHoc


class MonHocService:
    @staticmethod
    def create(data):
        if MonHoc.objects.filter(ma_mon=data.get('ma_mon')).exists():
            raise ValueError(f"Mã môn học '{data.get('ma_mon')}' đã tồn tại!")
        return MonHoc.objects.create(
            ma_mon=data['ma_mon'],
            ten_mon=data['ten_mon'],
            he_so=data.get('he_so', 1)
        )

    @staticmethod
    def list():
        return MonHoc.objects.all()

    @staticmethod
    def get(mon_hoc_id):
        return MonHoc.objects.get(pk=mon_hoc_id)

    @staticmethod
    def update(mon_hoc_id, data):
        mon_hoc = MonHoc.objects.get(pk=mon_hoc_id)

        if 'ma_mon' in data:
            if MonHoc.objects.filter(ma_mon=data['ma_mon']).exclude(pk=mon_hoc_id).exists():
                raise ValueError(f"Mã môn học '{data['ma_mon']}' đã tồn tại!")
            mon_hoc.ma_mon = data['ma_mon']

        if 'ten_mon' in data: mon_hoc.ten_mon = data['ten_mon']
        if 'he_so' in data: mon_hoc.he_so = data['he_so']

        mon_hoc.save()
        return mon_hoc

    @staticmethod
    def delete(mon_hoc_id):
        MonHoc.objects.get(pk=mon_hoc_id).delete()