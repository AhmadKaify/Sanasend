"""
Message serializers
"""
from rest_framework import serializers
from messages.models import Message
from core.validators import validate_phone_number


class MessageSerializer(serializers.ModelSerializer):
    """Message serializer"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'username', 'recipient', 'message_type', 'content', 
                  'status', 'error_message', 'sent_at']
        read_only_fields = ['id', 'username', 'status', 'error_message', 'sent_at']


class SendTextMessageSerializer(serializers.Serializer):
    """Send text message serializer"""
    
    recipient = serializers.CharField(validators=[validate_phone_number])
    message = serializers.CharField(max_length=5000)


class SendMediaMessageSerializer(serializers.Serializer):
    """Send media message serializer"""
    
    recipient = serializers.CharField(validators=[validate_phone_number])
    media_type = serializers.ChoiceField(choices=['image', 'document', 'video'])
    file = serializers.FileField()
    caption = serializers.CharField(max_length=1000, required=False, allow_blank=True)

