from django.contrib import admin
from .models import ExportFile

@admin.register(ExportFile)
class ExportFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'file_type', 'user', 'status', 'created_at']
    list_filter = ['status', 'file_type']
    search_fields = ['file_name', 'user__user_name']
    readonly_fields = ['file_path', 'created_at', 'updated_at']
