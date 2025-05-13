# Hướng dẫn cập nhật API key cho OpenRouter

Để tính năng chatbot đề xuất món ăn hoạt động, bạn cần có một API key hợp lệ từ OpenRouter. API key hiện tại đã hết hạn hoặc không còn hợp lệ.

## Các bước để lấy API key mới

1. Truy cập trang web OpenRouter tại địa chỉ: https://openrouter.ai
2. Đăng ký tài khoản nếu chưa có, hoặc đăng nhập vào tài khoản hiện có
3. Sau khi đăng nhập, vào mục "Keys" trong dashboard
4. Nhấn vào nút "Create Key" để tạo API key mới
5. Đặt tên cho API key (ví dụ: "Restaurant Chatbot")
6. Sao chép API key vừa được tạo (lưu ý: key chỉ hiển thị một lần)

## Cách cập nhật API key trong ứng dụng

### Phương pháp 1: Cập nhật trong file docker-compose.yml

1. Mở file `docker-compose.yml` 
2. Tìm biến môi trường `OPENROUTER_API_KEY` trong cả hai service `backend` và `celery_worker`
3. Thay thế giá trị key cũ bằng key mới vừa tạo
4. Lưu file và khởi động lại container với lệnh:
   ```
   docker-compose down
   docker-compose up --build
   ```

### Phương pháp 2: Sử dụng biến môi trường khi khởi chạy

Bạn có thể cung cấp API key thông qua biến môi trường khi khởi chạy docker-compose:

```
OPENROUTER_API_KEY=sk-or-v1-your-new-key docker-compose up
```

## Xác nhận key hoạt động

Sau khi cập nhật API key và khởi động lại container, bạn có thể kiểm tra logs để xác nhận API key mới hoạt động:

```
docker-compose logs backend | grep OpenRouter
```

Nếu bạn thấy thông báo "Connection successful!" hoặc không thấy lỗi 401 Unauthorized, điều đó có nghĩa là API key đã hoạt động.

## Lưu ý quan trọng

- Giữ API key an toàn và không chia sẻ công khai
- API key của OpenRouter có thể có giới hạn sử dụng tùy thuộc vào tài khoản của bạn
- Nếu API key hết hạn hoặc vượt quá giới hạn, bạn cần tạo key mới và cập nhật lại

## Thông tin thêm

Để biết thêm chi tiết về cách sử dụng OpenRouter API, vui lòng tham khảo tài liệu chính thức tại: https://openrouter.ai/docs 