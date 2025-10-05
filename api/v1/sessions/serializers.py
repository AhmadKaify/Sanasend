"""
Session serializers
"""
from rest_framework import serializers
from sessions.models import WhatsAppSession


class WhatsAppSessionSerializer(serializers.ModelSerializer):
    """WhatsApp Session serializer"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = WhatsAppSession
        fields = ['id', 'username', 'session_id', 'status', 'phone_number', 
                  'connected_at', 'last_active_at']
        read_only_fields = ['id', 'session_id', 'connected_at', 'last_active_at']

