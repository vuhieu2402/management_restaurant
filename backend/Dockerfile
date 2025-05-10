FROM python:3.10-slim

WORKDIR /app

# Cài đặt các packages cần thiết
RUN apt-get update && apt-get install -y bash gcc python3-dev

# Copy requirements file và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Tạo thư mục cho export_files
RUN mkdir -p /app/manageRestaurant/export_files

# Chuyển đến thư mục manageRestaurant
WORKDIR /app/manageRestaurant

# Đảm bảo các script có quyền thực thi
RUN chmod +x seed_data.py
RUN chmod +x docker_seed_data.py

# Expose cổng cho backend
EXPOSE 8000

# Lệnh chạy được định nghĩa trong docker-compose.yml
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 