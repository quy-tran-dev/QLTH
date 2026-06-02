from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import HocSinhViewSet, GiaoVienViewSet, LopHocViewSet, MonHocViewSet
from core.views.auth_view import ForgotPasswordView, ResetPasswordView, LoginView

router = DefaultRouter()
router.register(r'hoc-sinh', HocSinhViewSet, basename='hoc-sinh')
router.register(r'giao-vien', GiaoVienViewSet, basename='giao-vien')
router.register(r'lop-hoc', LopHocViewSet, basename='lop-hoc')
router.register(r'mon-hoc', MonHocViewSet, basename='mon-hoc')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('', include(router.urls)),
]