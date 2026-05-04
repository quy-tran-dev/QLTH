from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import HocSinh
from core.serializers import HocSinhSerializer
from core.services import HocSinhService

class HocSinhViewSet(viewsets.ModelViewSet):
    queryset = HocSinh.objects.all()
    serializer_class = HocSinhSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            student_id = kwargs.get('pk')
            student = HocSinhService.get(student_id)
            return Response(self.get_serializer(student).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            students = HocSinhService.list()
            return Response(self.get_serializer(students, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Ghi đè API POST (Tạo mới)
    def create(self, request, *args, **kwargs):
        try:
            student = HocSinhService.create(request.data)
            return Response(self.get_serializer(student).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Ghi đè API PUT/PATCH (Cập nhật)
    def update(self, request, *args, **kwargs):
        try:
            student_id = kwargs.get('pk') # Lấy ID từ URL
            student = HocSinhService.update(student_id, request.data)
            return Response(self.get_serializer(student).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Ghi đè API DELETE (Xóa/Khóa)
    def destroy(self, request, *args, **kwargs):
        try:
            HocSinhService.delete(kwargs.get('pk'))
            return Response({"msg": "Đã khóa tài khoản học sinh thành công"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='recover')
    def recover_account(self, request, pk=None):
        try:
            HocSinhService.recover(pk)
            return Response({"msg": f"Đã khôi phục tài khoản học sinh ID {pk} thành công!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)