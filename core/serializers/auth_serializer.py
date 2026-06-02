from typing import Dict, Any
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomLoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = getattr(user, 'username', '')
        token['vai_tro'] = getattr(user, 'vai_tro', '')
        return token

    def validate(self, attrs) -> Dict[str, Any]:
        data: dict = super().validate(attrs)

        data['user'] = {
            'id': getattr(self.user, 'id', None),
            'username': getattr(self.user, 'username', ''),
            'ho_ten': getattr(self.user, 'ho_ten', ''),
            'vai_tro': getattr(self.user, 'vai_tro', '')
        }
        return data