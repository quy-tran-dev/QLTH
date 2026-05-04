from rest_framework import serializers
from core.models import NguoiDung

class NguoiDungSerializer(serializers.ModelSerializer):

    trang_thai = serializers.BooleanField(required=False)

    class Meta:
        model = NguoiDung
        fields = ['id', 'username', 'ho_ten', 'cccd', 'vai_tro', 'trang_thai']

        extra_kwargs = {
            'password': {'write_only': True}
        }