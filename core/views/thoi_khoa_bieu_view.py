from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from core.models import ThoiKhoaBieu
from core.permissions import IsQuanLy
from core.serializers import ThoiKhoaBieuSerializer
from core.services.thoi_khoa_bieu_service import ThoiKhoaBieuService


class ThoiKhoaBieuViewSet(viewsets.ModelViewSet):
    serializer_class = ThoiKhoaBieuSerializer

    def get_queryset(self):
        # Đổi tiet_bat_dau thành tiet_hoc, và sort theo ngay_hoc
        queryset = ThoiKhoaBieu.objects.all().order_by('ngay_hoc', 'tiet_hoc')

        ma_lop = self.request.query_params.get('ma_lop')
        if ma_lop:
            queryset = queryset.filter(lop_hoc__ma_lop=ma_lop)

        ma_giao_vien = self.request.query_params.get('ma_giao_vien')
        if ma_giao_vien:
            queryset = queryset.filter(giao_vien__ma_giao_vien=ma_giao_vien)

        return queryset

    @action(
        detail=False,
        methods=['post'],
        url_path='cuon-chieu',
        permission_classes=[IsQuanLy]  # Ăn chặt quyền quản lý tại đây
    )
    def cuon_chieu(self, request):
        ma_tkb_cu = request.data.get('ma_tkb_cu')
        ngay_bat_dau_str = request.data.get('ngay_bat_dau')
        danh_sach_tiet_moi = request.data.get('lich_moi', [])

        if not ma_tkb_cu or not ngay_bat_dau_str:
            return Response({"error": "Thiếu mã TKB cũ hoặc ngày bắt đầu áp dụng!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ngay_bat_dau = datetime.strptime(ngay_bat_dau_str, '%Y-%m-%d').date()

            ThoiKhoaBieuService.clean_future_and_bulk_create(
                ma_tkb_cu=ma_tkb_cu,
                ngay_bat_dau=ngay_bat_dau,
                danh_sach_tiet_moi=danh_sach_tiet_moi
            )

            return Response({"msg": "Cập nhật thời khóa biểu cuốn chiếu thành công! Dữ liệu quá khứ được bảo toàn."},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['post'],
        url_path='import-excel',
        parser_classes=[MultiPartParser, FormParser],
        permission_classes=[IsQuanLy]
    )
    def import_excel_data(self, request):
        file_obj = request.FILES.get('file')
        ma_tkb_moi = request.data.get('ma_tkb_moi')
        ngay_bat_dau_str = request.data.get('ngay_bat_dau')
        ngay_ket_thuc_str = request.data.get('ngay_ket_thuc')

        # ma_tkb_cu giờ là tùy chọn, không bắt buộc nữa
        ma_tkb_cu = request.data.get('ma_tkb_cu')

        if not file_obj or not ma_tkb_moi or not ngay_bat_dau_str or not ngay_ket_thuc_str:
            return Response({"error": "Vui lòng cung cấp đủ: file, ma_tkb_moi, ngay_bat_dau, ngay_ket_thuc!"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            ngay_bat_dau = datetime.strptime(ngay_bat_dau_str, '%Y-%m-%d').date()
            ngay_ket_thuc = datetime.strptime(ngay_ket_thuc_str, '%Y-%m-%d').date()

            if ngay_bat_dau > ngay_ket_thuc:
                return Response({"error": "Ngày bắt đầu không được lớn hơn ngày kết thúc!"},
                                status=status.HTTP_400_BAD_REQUEST)

            count = ThoiKhoaBieuService.import_excel_sinh_lich(
                file_obj=file_obj,
                ma_tkb_moi=ma_tkb_moi,
                ngay_bat_dau=ngay_bat_dau,
                ngay_ket_thuc=ngay_ket_thuc,
                ma_tkb_cu=ma_tkb_cu
            )

            return Response({
                "msg": f"Tuyệt vời! Hệ thống đã nhân bản khung TKB thành công {count} tiết học từ {ngay_bat_dau_str} đến {ngay_ket_thuc_str}!"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            clean_error = str(e).replace("[", "").replace("]", "").replace("'", "")
            return Response({"error": clean_error}, status=status.HTTP_400_BAD_REQUEST)
