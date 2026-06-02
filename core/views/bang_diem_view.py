from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse

from core.models import BangDiem
from core.serializers.nghiep_vu_serializer import BangDiemSerializer
from core.services.bang_diem_service import BangDiemService
from core.services.hoc_sinh_service import ExcelImportException
from core.permissions import IsQuanLy, IsGiaoVienCuaLop


class BangDiemViewSet(viewsets.ModelViewSet):
    queryset = BangDiem.objects.all()
    serializer_class = BangDiemSerializer

    # ==========================================
    # API 1: TẢI FILE MẪU NHẬP ĐIỂM THEO LỚP (GET /api/bang-diem/export-mau/?lop_hoc_id=1&mon_hoc_id=2&hoc_ky=1)
    # ==========================================
    @action(
        detail=False,
        methods=['get'],
        url_path='export-mau',
        permission_classes=[IsQuanLy | IsGiaoVienCuaLop]  # Quản lý hoặc GV dạy lớp đó mới được tải
    )
    def download_mau_diem(self, request):
        lop_hoc_id = request.query_params.get('lop_hoc_id')
        mon_hoc_id = request.query_params.get('mon_hoc_id')
        hoc_ky = request.query_params.get('hoc_ky', 1)

        if not lop_hoc_id or not mon_hoc_id:
            return Response({"error": "Vui lòng cung cấp 'lop_hoc_id' và 'mon_hoc_id' qua query params!"}, status=400)

        try:
            output, filename = BangDiemService.export_template_theo_lop(lop_hoc_id, mon_hoc_id, hoc_ky)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    # ==========================================
    # API 2: IMPORT FILE EXCEL BẢNG ĐIỂM (POST /api/bang-diem/import-excel/)
    # ==========================================
    @action(
        detail=False,
        methods=['post'],
        url_path='import-excel',
        parser_classes=[MultiPartParser, FormParser],
        permission_classes=[IsQuanLy | IsGiaoVienCuaLop]
    )
    def import_excel_diem_data(self, request):
        file_obj = request.FILES.get('file')
        lop_hoc_id = request.data.get('lop_hoc_id')
        mon_hoc_id = request.data.get('mon_hoc_id')
        hoc_ky = request.data.get('hoc_ky')

        if not all([file_obj, lop_hoc_id, mon_hoc_id, hoc_ky]):
            return Response({"error": "Vui lòng điền đủ form-data gồm: file, lop_hoc_id, mon_hoc_id, hoc_ky!"},
                            status=400)

        try:
            count = BangDiemService.import_excel_diem(file_obj, lop_hoc_id, mon_hoc_id, hoc_ky)
            return Response({"msg": f"Đã cập nhật bảng điểm thành công cho {count} học sinh!"},
                            status=status.HTTP_200_OK)

        except ExcelImportException as ex:
            # Nếu giáo viên nhập điểm bậy bạ (ví dụ dòng 3 nhập điểm 15, dòng 4 nhập chữ 'A')
            return Response({
                "error_type": "EXCEL_VALIDATION_FAILED",
                "message": "File Excel bảng điểm chứa dữ liệu không hợp lệ.",
                "chi_tiet_loi": ex.error_details
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)