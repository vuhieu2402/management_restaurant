#!/bin/bash

# Kiểm tra xem Docker đã được cài đặt hay chưa
if ! command -v docker &> /dev/null; then
    echo "Docker không được tìm thấy. Vui lòng cài đặt Docker trước."
    exit 1
fi

# Kiểm tra xem Docker Compose đã được cài đặt hay chưa
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose không được tìm thấy. Vui lòng cài đặt Docker Compose trước."
    exit 1
fi

# Đảm bảo file có quyền thực thi
chmod +x run.sh

# Hàm hiển thị menu
show_menu() {
    echo "===== Restaurant Management System ====="
    echo "1. Khởi chạy hệ thống"
    echo "2. Dừng hệ thống"
    echo "3. Xem logs"
    echo "4. Rebuild và khởi chạy lại"
    echo "5. Kiểm tra container"
    echo "6. Vào shell của container"
    echo "7. Cài đặt thêm dependencies trong backend"
    echo "8. Thoát"
    echo "========================================"
    echo -n "Chọn một tùy chọn (1-8): "
}

# Hàm cài đặt dependencies thiếu
install_missing_dependencies() {
    echo "Cài đặt dependencies thiếu trong container backend..."
    docker-compose exec backend pip install drf-yasg cloudinary django-cloudinary-storage
    echo "Đã cài đặt xong dependencies."
    read -p "Nhấn Enter để tiếp tục..."
}

# Vòng lặp chính
while true; do
    clear
    show_menu
    read choice
    
    case $choice in
        1)
            echo "Đang khởi chạy hệ thống..."
            docker-compose up -d
            echo "Hệ thống đã được khởi chạy!"
            echo "Frontend: http://localhost:3000"
            echo "Backend API: http://localhost:8000/api"
            read -p "Nhấn Enter để tiếp tục..."
            ;;
        2)
            echo "Đang dừng hệ thống..."
            docker-compose down
            echo "Hệ thống đã dừng!"
            read -p "Nhấn Enter để tiếp tục..."
            ;;
        3)
            echo "Hiển thị logs (Nhấn Ctrl+C để thoát)..."
            docker-compose logs -f
            ;;
        4)
            echo "Đang rebuild và khởi chạy lại hệ thống..."
            docker-compose down
            docker-compose build --no-cache
            docker-compose up -d
            echo "Hệ thống đã được rebuild và khởi chạy lại!"
            echo "Frontend: http://localhost:3000"
            echo "Backend API: http://localhost:8000/api"
            read -p "Nhấn Enter để tiếp tục..."
            ;;
        5)
            echo "Kiểm tra container đang chạy..."
            docker-compose ps
            echo ""
            echo "Kiểm tra cấu trúc thư mục trong container backend..."
            docker-compose exec backend ls -la /app
            docker-compose exec backend ls -la /app/manageRestaurant || echo "Lỗi: Không thể truy cập thư mục manageRestaurant"
            read -p "Nhấn Enter để tiếp tục..."
            ;;
        6)
            echo "Chọn container để truy cập shell:"
            echo "1. Backend"
            echo "2. Frontend"
            read -p "Chọn (1-2): " container_choice
            case $container_choice in
                1)
                    echo "Truy cập shell container backend..."
                    docker-compose exec backend bash || docker-compose exec backend sh
                    ;;
                2)
                    echo "Truy cập shell container frontend..."
                    docker-compose exec frontend sh
                    ;;
                *)
                    echo "Lựa chọn không hợp lệ!"
                    ;;
            esac
            ;;
        7)
            install_missing_dependencies
            ;;
        8)
            echo "Thoát chương trình..."
            exit 0
            ;;
        *)
            echo "Lựa chọn không hợp lệ, vui lòng thử lại!"
            read -p "Nhấn Enter để tiếp tục..."
            ;;
    esac
done 