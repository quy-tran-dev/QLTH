from rest_framework import viewsets, status
from rest_framework.response import Response
from core.models import LopHoc
from core.serializers import LopHocSerializer
from core.services import LopHocService

class LopHocViewSet(viewsets.ModelViewSet):
    queryset = LopHoc.objects.all()
    serializer_class = LopHocSerializer

    def list(self, request, *args, **kwargs):
        return Response(self.get_serializer(LopHocService.list(), many=True).data)

    def retrieve(self, request, *args, **kwargs):
        try:
            return Response(self.get_serializer(LopHocService.get(kwargs.get('pk'))).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        try:
            return Response(self.get_serializer(LopHocService.create(request.data)).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            return Response(self.get_serializer(LopHocService.update(kwargs.get('pk'), request.data)).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            LopHocService.delete(kwargs.get('pk'))
            return Response({"msg": "Xóa lớp học thành công"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)