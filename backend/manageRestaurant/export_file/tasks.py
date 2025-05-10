import os
import csv
import logging
from celery import shared_task
from django.conf import settings
from minio import Minio
from minio.error import S3Error
from datetime import datetime
from .models import ExportFile
from order.models import Order, OrderDetails

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def export_orders_to_csv(export_file_id, params=None):
    """
    Task xuất danh sách đơn hàng ra file CSV
    """
    export_file = ExportFile.objects.get(id=export_file_id)
    
    try:
        # Lấy dữ liệu đơn hàng
        orders = Order.objects.all().order_by('-order_date')
        
        # Lọc theo tham số nếu có
        if params and 'year' in params:
            orders = orders.filter(order_date__year=params['year'])
        if params and 'month' in params:
            orders = orders.filter(order_date__month=params['month'])
        
        # Tạo thư mục xuất file nếu chưa tồn tại
        os.makedirs(settings.EXPORT_FILES_ROOT, exist_ok=True)
        
        # Đường dẫn đến file CSV tạm thời
        temp_file_path = os.path.join(settings.EXPORT_FILES_ROOT, export_file.file_name)
        
        # Tạo file CSV và ghi dữ liệu vào
        with open(temp_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            # Tạo tiêu đề
            fieldnames = ['ID', 'Khách hàng', 'Ngày đặt', 'Tổng tiền', 'Địa chỉ', 'Số điện thoại', 'Trạng thái', 'Các món']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Thêm dữ liệu từng đơn hàng
            for order in orders:
                order_details = OrderDetails.objects.filter(order_id=order)
                order_items = ", ".join([f"{detail.dish_id.name} x{detail.quantity}" for detail in order_details])
                
                writer.writerow({
                    'ID': order.id,
                    'Khách hàng': order.user_id.user_name,
                    'Ngày đặt': order.order_date.strftime('%d/%m/%Y %H:%M:%S'),
                    'Tổng tiền': float(order.total_price),
                    'Địa chỉ': order.address,
                    'Số điện thoại': order.phone,
                    'Trạng thái': 'Đã hoàn thành' if order.status else 'Chưa hoàn thành',
                    'Các món': order_items
                })
        
        # Kết nối đến MinIO
        # Lấy thông tin kết nối từ biến môi trường hoặc settings
        minio_endpoint = os.environ.get('MINIO_ENDPOINT', settings.MINIO_ENDPOINT)
        minio_access_key = os.environ.get('MINIO_ACCESS_KEY', settings.MINIO_ACCESS_KEY)
        minio_secret_key = os.environ.get('MINIO_SECRET_KEY', settings.MINIO_SECRET_KEY)
        minio_use_ssl = os.environ.get('MINIO_USE_SSL', str(settings.MINIO_USE_SSL)).lower() == 'true'
        minio_bucket_name = os.environ.get('MINIO_BUCKET_NAME', settings.MINIO_BUCKET_NAME)

        logger.info(f"Connecting to MinIO: endpoint={minio_endpoint}, bucket={minio_bucket_name}, ssl={minio_use_ssl}")
        
        try:
            client = Minio(
                minio_endpoint,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=minio_use_ssl
            )
            
            # Tạo bucket nếu chưa tồn tại
            if not client.bucket_exists(minio_bucket_name):
                logger.info(f"Creating bucket: {minio_bucket_name}")
                client.make_bucket(minio_bucket_name)
            
            # Upload file lên MinIO
            current_date = datetime.now().strftime('%Y/%m/%d')
            minio_path = f"{current_date}/{export_file.file_name}"
            logger.info(f"Uploading file to: {minio_bucket_name}/{minio_path}")
            client.fput_object(minio_bucket_name, minio_path, temp_file_path)
            
            # Cập nhật trạng thái và đường dẫn của file
            export_file.status = 'completed'
            export_file.file_path = f"minio://{minio_bucket_name}/{minio_path}"
            export_file.save()
            
            # Xóa file tạm thời
            os.remove(temp_file_path)
            
            return {
                'status': 'success',
                'file_path': export_file.file_path
            }
        except S3Error as e:
            logger.error(f"MinIO S3 error: {str(e)}")
            raise
            
    except Exception as e:
        # Cập nhật trạng thái nếu xảy ra lỗi
        logger.error(f"Error exporting file: {str(e)}")
        export_file.status = 'failed'
        export_file.save()
        
        return {
            'status': 'error',
            'message': str(e)
        } 