from rest_framework import serializers
from core.models import GiaoVien
from .nguoi_dung_serializer import NguoiDungSerializer

class GiaoVienSerializer(serializers.ModelSerializer):
    user = NguoiDungSerializer(read_only=True)

    class Meta:
        model = GiaoVien
        fields = ['id', 'ma_giao_vien', 'user', 'to_bo_mon', "bo_mon"]