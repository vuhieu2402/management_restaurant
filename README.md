# Quản lý Nhà hàng - Restaurant Management System

Hệ thống quản lý nhà hàng với chức năng đặt bàn, đặt món, quản lý menu, v.v.

## Cấu trúc project

- **Backend**: Django REST API
- **Frontend**: React JS

## Cài đặt và chạy với Docker

### Yêu cầu
- Docker và Docker Compose

### Các bước cài đặt

1. Clone repository
```bash
git clone <repository-url>
cd manage_restaurant
```

2. Khởi động các dịch vụ bằng Docker Compose
```bash
docker-compose up -d
```

3. Truy cập ứng dụng:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api

### Các lệnh Docker hữu ích

- Xem logs của các dịch vụ:
```bash
docker-compose logs -f
```

- Dừng các dịch vụ:
```bash
docker-compose down
```

- Rebuild các dịch vụ:
```bash
docker-compose up -d --build
```

## Chạy ứng dụng không dùng Docker

### Backend
```bash
cd backend
pip install -r requirements.txt
cd manage_restaurant
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend/my-app
npm install
npm start
```

## API Endpoints

- **Đặt bàn**: POST /api/reserve/
- **Món ăn**: GET /api/dishes/

## Chức năng

1. Đăng nhập/Đăng ký
2. Đặt bàn
3. Xem menu và đặt món
4. Tìm kiếm món ăn
5. Giỏ hàng và thanh toán 