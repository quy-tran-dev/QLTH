from rest_framework import serializers
from core.models import MonHoc

class MonHocSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonHoc
        fields = ['id', 'ma_mon', 'ten_mon', 'he_so']