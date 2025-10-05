"""
API Key serializers
"""
from rest_framework import serializers
from api_keys.models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    """API Key serializer"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = APIKey
        fields = ['id', 'username', 'name', 'is_active', 'last_used_at', 'created_at']
        read_only_fields = ['id', 'username', 'last_used_at', 'created_at']


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """API Key creation serializer"""
    
    class Meta:
        model = APIKey
        fields = ['user', 'name']

