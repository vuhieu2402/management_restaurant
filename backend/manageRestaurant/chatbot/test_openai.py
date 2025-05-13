import os
import sys
import django
from django.conf import settings
from openai import OpenAI

# Add the parent directory to Python path to find the settings module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thiết lập Django settings để có thể chạy script độc lập
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage_restaurant.settings')
django.setup()

def test_openai_connection():
    """
    Kiểm tra kết nối với OpenAI API hoặc OpenRouter API
    """
    if getattr(settings, 'USE_OPENROUTER', False):
        return test_openrouter_connection()
    else:
        return test_openai_direct_connection()

def test_openai_direct_connection():
    """
    Kiểm tra kết nối trực tiếp với OpenAI API
    """
    print("Kiểm tra kết nối đến OpenAI API...")
    
    # Kiểm tra API key
    if not settings.OPENAI_API_KEY:
        print("Lỗi: API key chưa được cấu hình!")
        print("Vui lòng thêm API key vào file settings.py tại OPENAI_API_KEY")
        return False
    
    # Khởi tạo client với API key
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    try:
        # Thử gọi API với một prompt đơn giản
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Bạn là trợ lý nhà hàng."},
                {"role": "user", "content": "Xin chào!"}
            ],
            max_tokens=50
        )
        
        # Kiểm tra phản hồi
        if response and response.choices and len(response.choices) > 0:
            print("✓ Kết nối thành công!")
            print(f"Model đang sử dụng: {settings.OPENAI_MODEL}")
            print(f"Phản hồi từ API: {response.choices[0].message.content}")
            return True
        else:
            print("✗ Lỗi: Nhận được phản hồi không hợp lệ từ API")
            return False
            
    except Exception as e:
        print(f"✗ Lỗi khi kết nối đến OpenAI API: {str(e)}")
        return False

def test_openrouter_connection():
    """
    Kiểm tra kết nối với OpenRouter API để sử dụng các model như Mistral, Claude, v.v.
    """
    print("Kiểm tra kết nối đến OpenRouter API...")
    
    # Kiểm tra API key
    if not settings.OPENROUTER_API_KEY:
        print("Lỗi: OpenRouter API key chưa được cấu hình!")
        print("Vui lòng đăng ký tại https://openrouter.ai và thêm API key vào file settings.py")
        return False
    
    # Khởi tạo client với API key và base URL của OpenRouter
    client = OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_API_BASE,
        default_headers={
            "HTTP-Referer": "https://restaurant-management-app.com",  # Tên domain ứng dụng của bạn
            "X-Title": "Restaurant Management System"  # Tên ứng dụng của bạn
        }
    )
    
    try:
        # Thử gọi API với một prompt đơn giản
        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "Bạn là trợ lý nhà hàng."},
                {"role": "user", "content": "Xin chào!"}
            ],
            max_tokens=50
        )
        
        # Kiểm tra phản hồi
        if response and response.choices and len(response.choices) > 0:
            print("✓ Kết nối đến OpenRouter thành công!")
            print(f"Model đang sử dụng: {settings.OPENROUTER_MODEL}")
            print(f"Phản hồi từ API: {response.choices[0].message.content}")
            return True
        else:
            print("✗ Lỗi: Nhận được phản hồi không hợp lệ từ OpenRouter API")
            return False
            
    except Exception as e:
        print(f"✗ Lỗi khi kết nối đến OpenRouter API: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_connection() 