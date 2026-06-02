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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and hasattr(request, 'user'):
            user_dang_goid_api = request.user
            la_quan_ly = getattr(user_dang_goid_api, 'vai_tro', None) == 'quan_ly'
            la_chinh_chu = user_dang_goid_api.id == instance.id

            if not (la_quan_ly or la_chinh_chu):
                if data.get('cccd'):
                    data['cccd'] = '***'
                    # data.pop('cccd', None)

        return data