from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.exceptions import ExcelImportException
from core.models import HocSinh
from core.permissions import IsQuanLy
from core.serializers import HocSinhSerializer
from core.services import HocSinhService


class HocSinhViewSet(viewsets.ModelViewSet):
    queryset = HocSinh.objects.all()
    serializer_class = HocSinhSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsQuanLy]

        return [permission() for permission in permission_classes]

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

    def create(self, request, *args, **kwargs):
        try:
            student = HocSinhService.create(request.data)
            return Response(self.get_serializer(student).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            student_id = kwargs.get('pk')  # Lấy ID từ URL
            student = HocSinhService.update(student_id, request.data)
            return Response(self.get_serializer(student).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

    # TẢI FILE MẪU EXCEL (GET /api/hoc-sinh/export-template/)
    # ==========================================
    @action(detail=False, methods=['get'], url_path='export-template')
    def download_template(self, request):
        output = HocSinhService.export_template()

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Mau_Import_Hoc_Sinh.xlsx"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response

    # ==========================================
    # IMPORT FILE EXCEL (POST /api/hoc-sinh/import-excel/)
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
            return Response({"error": "Vui lòng đính kèm file Excel (key: file)!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            count = HocSinhService.import_excel(file_obj)
            return Response({"msg": f"Tuyệt vời! Đã import thành công {count} học sinh vào hệ thống!"},
                            status=status.HTTP_200_OK)

        except ExcelImportException as ex:
            return Response({
                "error_type": "EXCEL_VALIDATION_FAILED",
                "message": "File Excel chứa dữ liệu không hợp lệ. Vui lòng sửa lại các dòng sau đây.",
                "chi_tiet_loi": ex.error_details
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
