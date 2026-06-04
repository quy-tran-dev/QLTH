from rest_framework_simplejwt.views import TokenObtainPairView
from core.serializers.auth_serializer import CustomLoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from core.services.nguoi_dung_service import NguoiDungService

class LoginView(TokenObtainPairView):
    serializer_class = CustomLoginSerializer


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        if not username:
            return Response({"error": "Vui lòng nhập Tên đăng nhập!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = NguoiDungService.generate_reset_password_token(username)

            print(f"\n[RESET PASSWORD TOKEN FOR {username}]: {token}\n")

            return Response({
                "msg": "Tạo mã khôi phục thành công! (Mã có hiệu lực trong 15 phút)",
                "token": token
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not token or not new_password:
            return Response({"error": "Vui lòng cung cấp đầy đủ 'token' và 'new_password'!"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            NguoiDungService.reset_password_with_token(token, new_password)
            return Response({"msg": "Chúc mừng! Bạn đã đổi mật khẩu thành công. Hãy thử đăng nhập lại!"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)