"""
Analytics serializers
"""
from rest_framework import serializers
from analytics.models import UsageStats, APILog


class UsageStatsSerializer(serializers.ModelSerializer):
    """Serializer for usage statistics"""
    
    class Meta:
        model = UsageStats
        fields = [
            'id', 'date', 'messages_sent', 'api_requests', 
            'media_sent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class APILogSerializer(serializers.ModelSerializer):
    """Serializer for API logs"""
    
    class Meta:
        model = APILog
        fields = [
            'id', 'endpoint', 'method', 'status_code', 
            'response_time', 'timestamp', 'ip_address'
        ]
        read_only_fields = ['id', 'timestamp']

