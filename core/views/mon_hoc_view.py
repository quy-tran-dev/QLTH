from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import MonHoc
from core.permissions import IsQuanLy
from core.serializers import MonHocSerializer
from core.services import MonHocService

class MonHocViewSet(viewsets.ModelViewSet):
    queryset = MonHoc.objects.all()
    serializer_class = MonHocSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsQuanLy]

        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        return Response(self.get_serializer(MonHocService.list(), many=True).data)

    def retrieve(self, request, *args, **kwargs):
        try:
            return Response(self.get_serializer(MonHocService.get(kwargs.get('pk'))).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        try:
            return Response(self.get_serializer(MonHocService.create(request.data)).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            return Response(self.get_serializer(MonHocService.update(kwargs.get('pk'), request.data)).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            MonHocService.delete(kwargs.get('pk'))
            return Response({"msg": "Xóa môn học thành công"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)