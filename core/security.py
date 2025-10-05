"""
Security utilities and middleware
"""
import logging
import time
import re
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.db.models import Q
import ipaddress
import hashlib
import hmac

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.tailwindcss.com https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp
        
        # HSTS (only for HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class BruteForceProtectionMiddleware(MiddlewareMixin):
    """Protect against brute force attacks"""
    
    def process_request(self, request):
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Get client IP
        ip = self._get_client_ip(request)
        
        # Check for brute force attempts
        if self._is_brute_force_attempt(ip):
            return self._brute_force_response()
        
        return None
    
    def _get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_brute_force_attempt(self, ip):
        """Check if IP is making too many requests"""
        try:
            now = timezone.now()
            minute_key = f"brute_force:{ip}:{now.strftime('%Y-%m-%d-%H-%M')}"
            hour_key = f"brute_force:{ip}:{now.strftime('%Y-%m-%d-%H')}"
            
            # Check per-minute limit (20 requests)
            minute_count = cache.get(minute_key, 0)
            if minute_count >= 20:
                return True
            
            # Check per-hour limit (200 requests)
            hour_count = cache.get(hour_key, 0)
            if hour_count >= 200:
                return True
            
            # Increment counters
            cache.set(minute_key, minute_count + 1, 60)  # Expire in 60 seconds
            cache.set(hour_key, hour_count + 1, 3600)  # Expire in 1 hour
            
            return False
        except Exception as e:
            # If cache is unavailable (e.g., Redis not running), log and allow request
            logger.warning(f"Brute force protection cache error: {e}. Allowing request.")
            return False
    
    def _brute_force_response(self):
        """Return brute force protection response"""
        return JsonResponse({
            'success': False,
            'message': 'Too many requests. Please try again later.',
            'error_code': 'BRUTE_FORCE_DETECTED'
        }, status=429)


class RequestValidationMiddleware(MiddlewareMixin):
    """Validate and sanitize incoming requests"""
    
    def process_request(self, request):
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Check for suspicious patterns
        if self._has_suspicious_patterns(request):
            logger.warning(f"Suspicious request from {self._get_client_ip(request)}: {request.path}")
            return JsonResponse({
                'success': False,
                'message': 'Invalid request',
                'error_code': 'SUSPICIOUS_REQUEST'
            }, status=400)
        
        # Validate request size
        if hasattr(request, 'content_length') and request.content_length:
            max_size = getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024)
            if request.content_length > max_size:
                return JsonResponse({
                    'success': False,
                    'message': 'Request too large',
                    'error_code': 'REQUEST_TOO_LARGE'
                }, status=413)
        
        return None
    
    def _get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _has_suspicious_patterns(self, request):
        """Check for suspicious request patterns"""
        # SQL injection patterns
        sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set',
            r'--',
            r'/\*.*\*/',
            r'xp_cmdshell',
            r'sp_executesql'
        ]
        
        # XSS patterns
        xss_patterns = [
            r'<script',
            r'javascript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
        
        # Path traversal patterns
        path_patterns = [
            r'\.\./',
            r'\.\.\\',
            r'%2e%2e%2f',
            r'%2e%2e%5c'
        ]
        
        # Check URL path
        path = request.path.lower()
        for pattern in sql_patterns + xss_patterns + path_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        
        # Check query parameters
        for key, value in request.GET.items():
            if isinstance(value, str):
                for pattern in sql_patterns + xss_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return True
        
        return False


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """Protect against SQL injection attacks"""
    
    def process_request(self, request):
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Check for SQL injection patterns in request data
        if self._has_sql_injection_patterns(request):
            logger.warning(f"SQL injection attempt from {self._get_client_ip(request)}")
            return JsonResponse({
                'success': False,
                'message': 'Invalid request',
                'error_code': 'SQL_INJECTION_DETECTED'
            }, status=400)
        
        return None
    
    def _get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _has_sql_injection_patterns(self, request):
        """Check for SQL injection patterns"""
        dangerous_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set',
            r'alter\s+table',
            r'create\s+table',
            r'exec\s*\(',
            r'execute\s*\(',
            r'sp_',
            r'xp_',
            r'--',
            r'/\*.*\*/',
            r';\s*drop',
            r';\s*delete',
            r';\s*insert',
            r';\s*update',
            r';\s*alter',
            r';\s*create',
            r';\s*exec',
            r';\s*execute'
        ]
        
        # Check all request data
        for key, value in request.GET.items():
            if isinstance(value, str) and self._check_patterns(value, dangerous_patterns):
                return True
        
        for key, value in request.POST.items():
            if isinstance(value, str) and self._check_patterns(value, dangerous_patterns):
                return True
        
        return False
    
    def _check_patterns(self, text, patterns):
        """Check if text matches any dangerous patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


class InputSanitizationMiddleware(MiddlewareMixin):
    """Sanitize input data"""
    
    def process_request(self, request):
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Sanitize request data
        self._sanitize_request_data(request)
        
        return None
    
    def _sanitize_request_data(self, request):
        """Sanitize request data"""
        # Sanitize GET parameters
        if hasattr(request, 'GET'):
            for key in list(request.GET.keys()):
                value = request.GET[key]
                if isinstance(value, str):
                    sanitized = self._sanitize_string(value)
                    if sanitized != value:
                        request.GET = request.GET.copy()
                        request.GET[key] = sanitized
        
        # Sanitize POST data
        if hasattr(request, 'POST'):
            for key in list(request.POST.keys()):
                value = request.POST[key]
                if isinstance(value, str):
                    sanitized = self._sanitize_string(value)
                    if sanitized != value:
                        request.POST = request.POST.copy()
                        request.POST[key] = sanitized
    
    def _sanitize_string(self, text):
        """Sanitize a string by removing dangerous characters"""
        if not isinstance(text, str):
            return text
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Limit length
        max_length = getattr(settings, 'MAX_INPUT_LENGTH', 10000)
        if len(text) > max_length:
            text = text[:max_length]
        
        return text


class IPWhitelistMiddleware(MiddlewareMixin):
    """IP whitelist middleware for API access"""
    
    def process_request(self, request):
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Skip for admin endpoints
        if request.path.startswith('/api/admin/'):
            return None
        
        # Check IP whitelist
        if not self._is_ip_allowed(request):
            logger.warning(f"Blocked request from unauthorized IP: {self._get_client_ip(request)}")
            return JsonResponse({
                'success': False,
                'message': 'Access denied',
                'error_code': 'IP_NOT_ALLOWED'
            }, status=403)
        
        return None
    
    def _get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_ip_allowed(self, request):
        """Check if IP is in whitelist"""
        ip = self._get_client_ip(request)
        
        # Get whitelist from settings
        allowed_ips = getattr(settings, 'API_IP_WHITELIST', [])
        if not allowed_ips:
            return True  # No whitelist configured
        
        try:
            client_ip = ipaddress.ip_address(ip)
            for allowed_ip in allowed_ips:
                if isinstance(allowed_ip, str):
                    if '/' in allowed_ip:
                        # CIDR notation
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if client_ip in network:
                            return True
                    else:
                        # Single IP
                        if client_ip == ipaddress.ip_address(allowed_ip):
                            return True
        except ValueError:
            # Invalid IP address
            return False
        
        return False


class SecurityAuditMiddleware(MiddlewareMixin):
    """Audit security events"""
    
    def process_request(self, request):
        # Log security-relevant events
        self._audit_request(request)
        return None
    
    def _audit_request(self, request):
        """Audit the request for security events"""
        ip = self._get_client_ip(request)
        user = getattr(request, 'user', None)
        user_id = user.id if user and user.is_authenticated else None
        
        # Log API access
        if request.path.startswith('/api/'):
            logger.info(f"API Access: {request.method} {request.path} from {ip} (User: {user_id})")
        
        # Log admin access
        if request.path.startswith('/admin/'):
            logger.info(f"Admin Access: {request.method} {request.path} from {ip} (User: {user_id})")
    
    def _get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def validate_api_key_security(api_key, request):
    """Validate API key with security checks"""
    from api_keys.models import APIKey
    
    # Get client IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    try:
        # Find the API key
        api_key_obj = APIKey.objects.get(key=api_key, is_active=True)
        
        # Check IP whitelist
        if not api_key_obj.is_ip_allowed(ip):
            logger.warning(f"API key {api_key_obj.id} used from unauthorized IP: {ip}")
            return None
        
        # Verify the key
        if api_key_obj.verify_key(api_key):
            return api_key_obj
        else:
            logger.warning(f"Invalid API key attempt: {api_key[:10]}... from {ip}")
            return None
            
    except APIKey.DoesNotExist:
        logger.warning(f"Non-existent API key attempt: {api_key[:10]}... from {ip}")
        return None


def generate_secure_token():
    """Generate a secure token"""
    import secrets
    return secrets.token_urlsafe(32)


def hash_sensitive_data(data):
    """Hash sensitive data for logging"""
    if not data:
        return None
    
    # Use HMAC with secret key
    secret = settings.SECRET_KEY.encode('utf-8')
    return hmac.new(secret, str(data).encode('utf-8'), hashlib.sha256).hexdigest()[:16]
