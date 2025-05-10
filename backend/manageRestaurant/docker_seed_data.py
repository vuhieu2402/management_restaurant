import os
import django
import sys

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage_restaurant.settings')
django.setup()

from django.db import transaction
from user.models import NewUser

def run_seed_data():
    """
    Chạy seed_data.py nếu chưa có dữ liệu mẫu
    """
    try:
        # Kiểm tra xem đã có dữ liệu mẫu chưa
        if NewUser.objects.filter(email="manager1@example.com").exists():
            print("Dữ liệu mẫu đã tồn tại, bỏ qua việc tạo dữ liệu mẫu.")
            return
        
        # Nếu chưa có dữ liệu mẫu, chạy seed_data.py
        print("Bắt đầu tạo dữ liệu mẫu...")
        
        # Import seed_data.py trực tiếp thay vì sử dụng exec()
        # File seed_data.py đã được cập nhật để xử lý lỗi bên trong
        import seed_data
        
        print("Tạo dữ liệu mẫu thành công.")
    except Exception as e:
        print(f"Lỗi khi tạo dữ liệu mẫu: {str(e)}")
        return

if __name__ == "__main__":
    run_seed_data() 