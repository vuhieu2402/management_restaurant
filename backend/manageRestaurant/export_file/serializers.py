from rest_framework import serializers
from .models import ExportFile

class ExportFileSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    
    class Meta:
        model = ExportFile
        fields = ['id', 'file_name', 'file_type', 'file_type_display', 'status', 
                  'status_display', 'created_at', 'updated_at', 'file_path']
        read_only_fields = ['id', 'file_name', 'status', 'created_at', 'updated_at', 'file_path'] 