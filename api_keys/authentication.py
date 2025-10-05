"""
Custom authentication classes for API access
"""
from rest_framework import authentication, exceptions
from django.conf import settings
from api_keys.models import APIKey
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication for API key-based access
    Supports two formats:
    1. X-Api-Key header: X-Api-Key: YOUR_KEY
    2. Authorization header: Authorization: ApiKey YOUR_KEY
    """
    
    def authenticate(self, request):
        # Try X-Api-Key header first
        api_key = request.META.get('HTTP_X_API_KEY')
        
        # If not found, try Authorization header with ApiKey prefix
        if not api_key:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('ApiKey '):
                api_key = auth_header[7:]  # Remove 'ApiKey ' prefix
        
        if not api_key:
            return None
        
        # Since keys are hashed, we need to check all active keys
        # Extract prefix to identify potential keys (format: wsk_timestamp_randompart)
        if not api_key.startswith('wsk_'):
            logger.warning(f'Invalid API key format: {api_key[:10]}...')
            raise exceptions.AuthenticationFailed('Invalid API key')
        
        # Hash the provided key and look it up
        import hmac
        import hashlib
        secret = settings.SECRET_KEY.encode('utf-8')
        hashed_key = hmac.new(secret, api_key.encode('utf-8'), hashlib.sha256).hexdigest()
        
        try:
            key_obj = APIKey.objects.select_related('user').get(
                key=hashed_key,
                is_active=True
            )
            
            # Check if key is expired
            if key_obj.expires_at and key_obj.expires_at < timezone.now():
                logger.warning(f'Expired API key attempted for user {key_obj.user.username}')
                raise exceptions.AuthenticationFailed('API key has expired')
            
            # Check if user is active
            if not key_obj.user.is_active:
                logger.warning(f'Inactive user attempted to use API key: {key_obj.user.username}')
                raise exceptions.AuthenticationFailed('User account is disabled')
            
            # Update last used
            key_obj.last_used_at = timezone.now()
            key_obj.save(update_fields=['last_used_at'])
            
            logger.info(f'API key authenticated for user {key_obj.user.username} (key: {key_obj.name})')
            
            return (key_obj.user, key_obj)
            
        except APIKey.DoesNotExist:
            logger.warning(f'Invalid API key attempted: {api_key[:10]}...')
            raise exceptions.AuthenticationFailed('Invalid API key')


class NodeServiceAuthentication(authentication.BaseAuthentication):
    """
    Authentication for Node.js service webhooks
    Uses a special API key configured in settings
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            raise exceptions.AuthenticationFailed('API key required')
        
        # Check against Node.js service API key
        expected_key = getattr(settings, 'NODE_SERVICE_API_KEY', None)
        
        if not expected_key:
            logger.error('NODE_SERVICE_API_KEY not configured in settings')
            raise exceptions.AuthenticationFailed('Service authentication not configured')
        
        if api_key != expected_key:
            raise exceptions.AuthenticationFailed('Invalid service API key')
        
        # Return None for user since this is service-to-service authentication
        return (None, None)
