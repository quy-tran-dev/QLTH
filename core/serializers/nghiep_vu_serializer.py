from rest_framework import serializers
from core.models import ThoiKhoaBieu, BangDiem, DanhGiaChuyenCan

class ThoiKhoaBieuSerializer(serializers.ModelSerializer):
    ten_giao_vien = serializers.CharField(source='giao_vien.user.ho_ten', read_only=True)
    ten_lop = serializers.CharField(source='lop_hoc.ten_lop', read_only=True)
    ten_mon = serializers.CharField(source='mon_hoc.ten_mon', read_only=True)

    class Meta:
        model = ThoiKhoaBieu
        fields = '__all__'

class BangDiemSerializer(serializers.ModelSerializer):
    ten_hoc_sinh = serializers.CharField(source='hoc_sinh.user.ho_ten', read_only=True)
    ten_mon = serializers.CharField(source='mon_hoc.ten_mon', read_only=True)

    class Meta:
        model = BangDiem
        fields = '__all__'

class DanhGiaChuyenCanSerializer(serializers.ModelSerializer):
    ten_hoc_sinh = serializers.CharField(source='hoc_sinh.user.ho_ten', read_only=True)
    ten_giao_vien = serializers.CharField(source='giao_vien_danh_gia.user.ho_ten', read_only=True)

    class Meta:
        model = DanhGiaChuyenCan
        fields = '__all__'