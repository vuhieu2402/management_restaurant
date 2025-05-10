from django.db import models
from user.models import NewUser

class ExportFile(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại'),
    )
    
    FILE_TYPE_CHOICES = (
        ('order_report', 'Báo cáo đơn hàng'),
        # Thêm các loại báo cáo khác ở đây
    )
    
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE, related_name='export_files')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    file_path = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    params = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.file_name} - {self.get_status_display()}"
