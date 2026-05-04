from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import HocSinhViewSet, GiaoVienViewSet, LopHocViewSet, MonHocViewSet

router = DefaultRouter()
router.register(r'hoc-sinh', HocSinhViewSet, basename='hoc-sinh')
router.register(r'giao-vien', GiaoVienViewSet, basename='giao-vien')
router.register(r'lop-hoc', LopHocViewSet, basename='lop-hoc')
router.register(r'mon-hoc', MonHocViewSet, basename='mon-hoc')

urlpatterns = [
    path('', include(router.urls)),
]