#!/usr/bin/env python
import os
import time
from minio import Minio
from minio.error import S3Error

def init_minio():
    """
    Script to initialize MinIO connection and create bucket
    """
    # Lấy thông tin kết nối từ biến môi trường
    minio_endpoint = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
    minio_access_key = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
    minio_secret_key = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
    minio_use_ssl = os.environ.get('MINIO_USE_SSL', 'False').lower() == 'true'
    minio_bucket_name = os.environ.get('MINIO_BUCKET_NAME', 'restaurant-exports')
    
    print(f"Initializing MinIO connection to: {minio_endpoint}")
    
    # Đợi để MinIO khởi động
    max_retries = 5
    retry_count = 0
    connected = False
    
    while retry_count < max_retries and not connected:
        try:
            client = Minio(
                minio_endpoint,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=minio_use_ssl
            )
            
            # Tạo bucket nếu chưa tồn tại
            if not client.bucket_exists(minio_bucket_name):
                print(f"Creating bucket: {minio_bucket_name}")
                client.make_bucket(minio_bucket_name)
                print(f"Bucket '{minio_bucket_name}' created successfully")
            else:
                print(f"Bucket '{minio_bucket_name}' already exists")
                
            connected = True
            print("MinIO initialized successfully")
            
        except Exception as e:
            retry_count += 1
            wait_time = 5 * retry_count
            print(f"MinIO connection failed (attempt {retry_count}/{max_retries}): {str(e)}")
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    if not connected:
        print("Failed to connect to MinIO after multiple attempts")
        return False
        
    return True

if __name__ == "__main__":
    init_minio() 