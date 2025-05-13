FROM python:3.10-slim

WORKDIR /app

# Cài đặt các packages cần thiết
RUN apt-get update && apt-get install -y bash gcc python3-dev libffi-dev curl

# Copy requirements file và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Tạo thư mục cho export_files
RUN mkdir -p /app/manageRestaurant/export_files

# Đảm bảo các script có quyền thực thi
RUN chmod +x start_server.sh
RUN chmod +x check_server.sh
RUN chmod +x celery_start.sh
RUN chmod +x manageRestaurant/docker_seed_data.py
RUN chmod +x manageRestaurant/init_minio.py

# Expose cổng cho backend và WebSocket
EXPOSE 8000

# Sử dụng script start_server.sh để khởi động Django với Daphne
CMD ["/bin/bash", "start_server.sh"] 