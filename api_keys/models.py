import secrets
import hashlib
import hmac
from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class APIKey(models.Model):
    """API Key model for authentication with enhanced security"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Optional label for the API key'
    )
    key = models.CharField(max_length=128, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True, help_text='Optional expiration date')
    failed_attempts = models.IntegerField(default=0)
    last_failed_attempt = models.DateTimeField(blank=True, null=True)
    ip_whitelist = models.TextField(
        blank=True, 
        null=True,
        help_text='Comma-separated list of allowed IP addresses (optional)'
    )
    
    class Meta:
        db_table = 'api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['key']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.name or "Unnamed"}'
    
    @staticmethod
    def generate_key():
        """Generate a secure API key with timestamp"""
        timestamp = str(int(timezone.now().timestamp()))
        random_part = secrets.token_urlsafe(32)
        return f"wsk_{timestamp}_{random_part}"
    
    def save(self, *args, **kwargs):
        if not self.key:
            # Generate new key on creation
            raw_key = self.generate_key()
            # Use HMAC for additional security
            self.key = self._hash_key(raw_key)
            # Store raw key temporarily for display
            self._raw_key = raw_key
        super().save(*args, **kwargs)
    
    def _hash_key(self, raw_key):
        """Hash the API key using HMAC with secret key"""
        secret = settings.SECRET_KEY.encode('utf-8')
        return hmac.new(secret, raw_key.encode('utf-8'), hashlib.sha256).hexdigest()
    
    def verify_key(self, raw_key):
        """Verify a raw API key against the hashed version"""
        if not self.is_active:
            return False
        
        # Check if key is expired
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        
        # Check if key is locked due to too many failed attempts
        if self.failed_attempts >= 5:
            # Check if 15 minutes have passed since last failed attempt
            if (self.last_failed_attempt and 
                timezone.now() - self.last_failed_attempt < timedelta(minutes=15)):
                return False
        
        # Verify the key
        expected_hash = self._hash_key(raw_key)
        is_valid = hmac.compare_digest(self.key, expected_hash)
        
        if is_valid:
            # Reset failed attempts on successful verification
            self.failed_attempts = 0
            self.last_used_at = timezone.now()
            self.save(update_fields=['failed_attempts', 'last_used_at'])
        else:
            # Increment failed attempts
            self.failed_attempts += 1
            self.last_failed_attempt = timezone.now()
            self.save(update_fields=['failed_attempts', 'last_failed_attempt'])
        
        return is_valid
    
    def is_ip_allowed(self, ip_address):
        """Check if IP address is in whitelist"""
        if not self.ip_whitelist:
            return True
        
        allowed_ips = [ip.strip() for ip in self.ip_whitelist.split(',')]
        return ip_address in allowed_ips
    
    def clean(self):
        """Validate the API key"""
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError('Expiration date must be in the future.')
        
        if self.ip_whitelist:
            # Validate IP addresses
            import ipaddress
            try:
                for ip in self.ip_whitelist.split(','):
                    ipaddress.ip_address(ip.strip())
            except ValueError:
                raise ValidationError('Invalid IP address in whitelist.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

