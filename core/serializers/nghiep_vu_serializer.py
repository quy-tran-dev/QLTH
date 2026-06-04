from rest_framework import serializers
from core.models import ThoiKhoaBieu, BangDiem


class ThoiKhoaBieuSerializer(serializers.ModelSerializer):
    ten_giao_vien = serializers.CharField(source='giao_vien.user.ho_ten', read_only=True)
    ten_lop = serializers.CharField(source='lop_hoc.ten_lop', read_only=True)
    ten_mon = serializers.CharField(source='mon_hoc.ten_mon', read_only=True)

    class Meta:
        model = ThoiKhoaBieu
        fields = [
            'id', 'ma_tkb', 'ngay_hoc', 'thu_trong_tuan', 'tiet_hoc',
            'giao_vien', 'ten_giao_vien', 'lop_hoc', 'ten_lop', 'mon_hoc', 'ten_mon'
        ]

    validators = []

    def create(self, validated_data):
        try:
            from core.services.thoi_khoa_bieu_service import ThoiKhoaBieuService
            return ThoiKhoaBieuService.validate_and_create_tkb(validated_data)
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e).replace("[", "").replace("]", "").replace("'", "")})


class BangDiemSerializer(serializers.ModelSerializer):
    ten_hoc_sinh = serializers.CharField(source='hoc_sinh.user.ho_ten', read_only=True)
    ten_mon = serializers.CharField(source='mon_hoc.ten_mon', read_only=True)

    class Meta:
        model = BangDiem
        fields = '__all__'
