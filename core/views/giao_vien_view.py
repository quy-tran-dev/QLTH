from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from core.models import GiaoVien
from core.serializers import GiaoVienSerializer
from core.services import GiaoVienService

class GiaoVienViewSet(viewsets.ModelViewSet):
    queryset = GiaoVien.objects.all()
    serializer_class = GiaoVienSerializer

    def list(self, request, *args, **kwargs):
        try:
            teachers = GiaoVienService.list()
            return Response(self.get_serializer(teachers, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            teacher = GiaoVienService.get(kwargs.get('pk'))
            return Response(self.get_serializer(teacher).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            teacher = GiaoVienService.create(request.data)
            return Response(self.get_serializer(teacher).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            teacher = GiaoVienService.update(kwargs.get('pk'), request.data)
            return Response(self.get_serializer(teacher).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            GiaoVienService.delete(kwargs.get('pk'))
            return Response({"msg": "Đã khóa tài khoản giáo viên thành công"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Tuyến đường phụ (Extra Route) để khôi phục tài khoản
    @action(detail=True, methods=['post'], url_path='recover')
    def recover_account(self, request, pk=None):
        try:
            GiaoVienService.recover(pk)
            return Response({"msg": f"Đã khôi phục tài khoản giáo viên ID {pk} thành công!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)