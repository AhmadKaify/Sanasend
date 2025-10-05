"""
Analytics serializers
"""
from rest_framework import serializers
from analytics.models import UsageStats, APILog


class UsageStatsSerializer(serializers.ModelSerializer):
    """Usage Statistics serializer"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UsageStats
        fields = ['id', 'username', 'date', 'messages_sent', 'api_requests', 'media_sent']
        read_only_fields = ['id', 'username', 'date']


class APILogSerializer(serializers.ModelSerializer):
    """API Log serializer"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = APILog
        fields = ['id', 'username', 'endpoint', 'method', 'status_code', 'ip_address', 'timestamp']
        read_only_fields = ['id', 'username', 'endpoint', 'method', 'status_code', 'ip_address', 'timestamp']

