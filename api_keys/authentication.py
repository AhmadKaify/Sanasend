"""
API Key authentication class with enhanced security
"""
import logging
from django.utils import timezone
from rest_framework import authentication, exceptions
from core.security import validate_api_key_security
from .models import APIKey

logger = logging.getLogger(__name__)


class APIKeyAuthentication(authentication.BaseAuthentication):
    """Enhanced API key authentication with security features"""
    
    keyword = 'ApiKey'
    
    def authenticate(self, request):
        # Check for API key in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith(self.keyword + ' '):
            try:
                raw_key = auth_header.split(' ')[1]
                return self.authenticate_credentials(raw_key, request)
            except IndexError:
                raise exceptions.AuthenticationFailed('Invalid API key format')
        
        # Check for API key in X-API-Key header
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key:
            return self.authenticate_credentials(api_key, request)
        
        return None
    
    def authenticate_credentials(self, raw_key, request):
        """Authenticate API key with security checks"""
        # Validate API key with security middleware
        api_key_obj = validate_api_key_security(raw_key, request)
        
        if not api_key_obj:
            raise exceptions.AuthenticationFailed('Invalid or expired API key')
        
        # Check if user is active
        if not api_key_obj.user.is_active:
            logger.warning(f"Authentication attempt with inactive user: {api_key_obj.user.username}")
            raise exceptions.AuthenticationFailed('User account is disabled')
        
        # Check if API key is expired
        if api_key_obj.expires_at and timezone.now() > api_key_obj.expires_at:
            logger.warning(f"Authentication attempt with expired API key: {api_key_obj.id}")
            raise exceptions.AuthenticationFailed('API key has expired')
        
        # Log successful authentication
        logger.info(f"Successful API authentication: {api_key_obj.user.username} (Key: {api_key_obj.id})")
        
        return (api_key_obj.user, api_key_obj)
    
    def authenticate_header(self, request):
        return self.keyword


class XAPIKeyAuthentication(authentication.BaseAuthentication):
    """Alternative API key authentication using X-API-Key header"""
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
        
        return self.authenticate_credentials(api_key, request)
    
    def authenticate_credentials(self, raw_key, request):
        """Authenticate API key with security checks"""
        # Validate API key with security middleware
        api_key_obj = validate_api_key_security(raw_key, request)
        
        if not api_key_obj:
            raise exceptions.AuthenticationFailed('Invalid or expired API key')
        
        # Check if user is active
        if not api_key_obj.user.is_active:
            logger.warning(f"Authentication attempt with inactive user: {api_key_obj.user.username}")
            raise exceptions.AuthenticationFailed('User account is disabled')
        
        # Check if API key is expired
        if api_key_obj.expires_at and timezone.now() > api_key_obj.expires_at:
            logger.warning(f"Authentication attempt with expired API key: {api_key_obj.id}")
            raise exceptions.AuthenticationFailed('API key has expired')
        
        # Log successful authentication
        logger.info(f"Successful API authentication: {api_key_obj.user.username} (Key: {api_key_obj.id})")
        
        return (api_key_obj.user, api_key_obj)

