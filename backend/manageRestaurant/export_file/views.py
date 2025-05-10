from django.shortcuts import render
import uuid
import os
import logging
from django.conf import settings
from django.http import HttpResponse, FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from minio import Minio
from minio.error import S3Error
from urllib.parse import urlparse
from .models import ExportFile
from .serializers import ExportFileSerializer
from .tasks import export_orders_to_csv

# Set up logging
logger = logging.getLogger(__name__)

class ExportFileViewSet(viewsets.ModelViewSet):
    """
    Viewset quản lý xuất file báo cáo
    """
    serializer_class = ExportFileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        return ExportFile.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve', 'download']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'])
    def export_orders(self, request):
        """
        API xuất báo cáo đơn hàng
        """
        user = request.user
        
        # Kiểm tra quyền truy cập (chỉ admin và staff mới có quyền)
        if not (user.is_staff or user.is_superuser):
            return Response({'detail': 'Permission denied.'}, status=403)
            
        # Lấy tham số từ request
        params = {}
        year = request.data.get('year')
        month = request.data.get('month')
        
        if year:
            params['year'] = year
        if month:
            params['month'] = month
            
        # Tạo tên file
        file_name = f"order_report_{uuid.uuid4().hex[:8]}.csv"
        if year and month:
            file_name = f"order_report_{year}_{month}.csv"
        elif year:
            file_name = f"order_report_{year}.csv"
            
        # Tạo record ExportFile
        export_file = ExportFile.objects.create(
            user=user,
            file_name=file_name,
            file_type='order_report',
            status='pending',
            params=params
        )
        
        # Gọi Celery task để xử lý bất đồng bộ
        export_orders_to_csv.delay(export_file.id, params)
        
        serializer = self.get_serializer(export_file)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        API tải xuống file báo cáo
        """
        try:
            # Log thông tin request
            logger.info(f"Download request received: User={request.user}, Auth={request.auth}")
            logger.info(f"Headers: {request.headers}")
            
            export_file = self.get_object()
            
            # Kiểm tra file đã hoàn thành chưa
            if export_file.status != 'completed':
                return Response(
                    {'detail': 'File chưa sẵn sàng để tải xuống.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Phân tích đường dẫn
            if export_file.file_path.startswith('minio://'):
                # Lấy thông tin kết nối MinIO từ biến môi trường hoặc settings
                minio_endpoint = os.environ.get('MINIO_ENDPOINT', settings.MINIO_ENDPOINT)
                minio_access_key = os.environ.get('MINIO_ACCESS_KEY', settings.MINIO_ACCESS_KEY)
                minio_secret_key = os.environ.get('MINIO_SECRET_KEY', settings.MINIO_SECRET_KEY)
                minio_use_ssl = os.environ.get('MINIO_USE_SSL', str(settings.MINIO_USE_SSL)).lower() == 'true'
                
                logger.info(f"Downloading from MinIO: endpoint={minio_endpoint}, file={export_file.file_name}")
                
                # Kết nối MinIO
                try:
                    client = Minio(
                        minio_endpoint,
                        access_key=minio_access_key,
                        secret_key=minio_secret_key,
                        secure=minio_use_ssl
                    )
                    
                    # Trích xuất bucket và object name từ URI
                    path_parts = urlparse(export_file.file_path.replace('minio://', 'http://'))
                    bucket_name = path_parts.netloc
                    object_name = path_parts.path.lstrip('/')
                    
                    logger.info(f"Retrieving object: bucket={bucket_name}, object={object_name}")
                    
                    # Tạo thư mục tạm thời nếu chưa tồn tại
                    os.makedirs(settings.EXPORT_FILES_ROOT, exist_ok=True)
                    temp_file_path = os.path.join(settings.EXPORT_FILES_ROOT, export_file.file_name)
                    
                    # Tải file về từ MinIO
                    client.fget_object(bucket_name, object_name, temp_file_path)
                    
                    # Đọc nội dung file
                    with open(temp_file_path, 'rb') as file:
                        file_content = file.read()
                    
                    # Xóa file tạm
                    os.remove(temp_file_path)
                    
                    # Trả về file cho người dùng với tất cả headers cần thiết
                    response = HttpResponse(
                        file_content,
                        content_type='text/csv; charset=utf-8-sig'
                    )
                    
                    # Sử dụng attachment để buộc trình duyệt tải xuống
                    response['Content-Disposition'] = f'attachment; filename="{export_file.file_name}"'
                    response['Content-Length'] = len(file_content)
                    response['Access-Control-Expose-Headers'] = 'Content-Disposition, Content-Length'
                    
                    logger.info(f"File download prepared successfully: {export_file.file_name}")
                    return response
                    
                except S3Error as e:
                    logger.error(f"MinIO S3 error during download: {str(e)}")
                    return Response(
                        {'detail': f'Lỗi S3 khi tải file: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(
                {'detail': 'Không thể tải file từ đường dẫn này.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return Response(
                {'detail': f'Lỗi khi tải file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
