from rest_framework import serializers
from core.models import LopHoc


class LopHocSerializer(serializers.ModelSerializer):
    giao_vien_chu_nhiem_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    ten_giao_vien = serializers.CharField(source='giao_vien_chu_nhiem.user.ho_ten', read_only=True)
    ma_giao_vien = serializers.CharField(source='giao_vien_chu_nhiem.ma_giao_vien', read_only=True)

    class Meta:
        model = LopHoc
        fields = ['id', 'ma_lop', 'ten_lop', 'nam_hoc', 'giao_vien_chu_nhiem_id', 'ten_giao_vien', 'ma_giao_vien']
