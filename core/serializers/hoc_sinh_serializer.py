from rest_framework import serializers
from core.models import HocSinh
from .nguoi_dung_serializer import NguoiDungSerializer


class HocSinhSerializer(serializers.ModelSerializer):
    user = NguoiDungSerializer(read_only=True)

    lop_hoc_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    ten_lop = serializers.CharField(source='lop_hoc.ten_lop', read_only=True)

    class Meta:
        model = HocSinh
        fields = ['id', 'ma_hoc_sinh', 'user', 'lop_hoc_id', 'ten_lop']