from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from core.exceptions import ExcelImportException
from core.models import GiaoVien
from core.permissions import IsQuanLy
from core.serializers import GiaoVienSerializer
from core.services import GiaoVienService

class GiaoVienViewSet(viewsets.ModelViewSet):
    queryset = GiaoVien.objects.all()
    serializer_class = GiaoVienSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsQuanLy]

        return [permission() for permission in permission_classes]

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

    @action(detail=True, methods=['post'], url_path='recover')
    def recover_account(self, request, pk=None):
        try:
            GiaoVienService.recover(pk)
            return Response({"msg": f"Đã khôi phục tài khoản giáo viên ID {pk} thành công!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # TẢI FILE MẪU EXCEL GIÁO VIÊN (GET /api/giao-vien/export-template/)
    # ==========================================
    @action(detail=False, methods=['get'], url_path='export-template')
    def download_template(self, request):
        output = GiaoVienService.export_template()

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Mau_Import_Giao_Vien.xlsx"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response

    # ==========================================
    # IMPORT FILE EXCEL GIÁO VIÊN (POST /api/giao-vien/import-excel/)
    # ==========================================
    @action(
        detail=False,
        methods=['post'],
        url_path='import-excel',
        parser_classes=[MultiPartParser, FormParser],
        permission_classes=[IsQuanLy]
    )
    def import_excel_data(self, request):
        file_obj = request.FILES.get('file')

        if not file_obj:
            return Response({"error": "Vui lòng đính kèm file Excel giáo viên (key: file)!"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            count = GiaoVienService.import_excel(file_obj)
            return Response({"msg": f"Đã import thành công {count} giáo viên vào hệ thống!"}, status=status.HTTP_200_OK)

        except ExcelImportException as ex:
            return Response({
                "error_type": "EXCEL_VALIDATION_FAILED",
                "message": "File Excel Giáo Viên chứa dữ liệu không hợp lệ. Vui lòng kiểm tra lại.",
                "chi_tiet_loi": ex.error_details
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)