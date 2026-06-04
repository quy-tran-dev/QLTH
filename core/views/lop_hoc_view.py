from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import LopHoc
from core.permissions import IsQuanLy
from core.serializers import LopHocSerializer
from core.services import LopHocService

class LopHocViewSet(viewsets.ModelViewSet):
    queryset = LopHoc.objects.all()
    serializer_class = LopHocSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsQuanLy]

        return [permission() for permission in permission_classes]

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

    # =========================================================================
    # XUẤT EXCEL DANH SÁCH HỌC SINH (GET /api/lop-hoc/export-hoc-sinh/?ma_lop=10A1)
    # =========================================================================
    @action(
        detail=False,
        methods=['get'],
        url_path='export-hoc-sinh',
        permission_classes=[IsQuanLy]
    )
    def export_hoc_sinh_theo_lop(self, request):
        ma_lop = request.query_params.get('ma_lop')

        if not ma_lop:
            return Response({"error": "Vui lòng cung cấp tham số 'ma_lop' trên URL!"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            output, filename = LopHocService.export_danh_sach_hoc_sinh(ma_lop)

            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response

        except ValueError as val_err:
            return Response({"error": str(val_err)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Lỗi hệ thống bất ngờ: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)