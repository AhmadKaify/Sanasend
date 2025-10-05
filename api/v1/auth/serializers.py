"""
Authentication serializers
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must provide username and password')


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_staff', 'is_active', 'max_messages_per_day', 'created_at']
        read_only_fields = fields

