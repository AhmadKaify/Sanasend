from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class WhatsAppSession(models.Model):
    """WhatsApp session model - supports multiple instances per user"""
    
    STATUS_CHOICES = [
        ('initializing', 'Initializing'),
        ('qr_pending', 'QR Code Pending'),
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('auth_failed', 'Authentication Failed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='whatsapp_sessions'
    )
    instance_name = models.CharField(
        max_length=100,
        default='Primary Instance',
        help_text='Friendly name for this WhatsApp instance'
    )
    session_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='disconnected'
    )
    qr_code = models.TextField(blank=True, null=True)
    qr_expires_at = models.DateTimeField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    connected_at = models.DateTimeField(blank=True, null=True)
    last_active_at = models.DateTimeField(blank=True, null=True)
    is_primary = models.BooleanField(
        default=False,
        help_text='Primary instance for this user'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'whatsapp_sessions'
        verbose_name = 'WhatsApp Session'
        verbose_name_plural = 'WhatsApp Sessions'
        unique_together = [['user', 'instance_name']]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'is_primary']),
        ]
    
    def clean(self):
        """Validate instance limits and primary instance"""
        if self.pk is None:  # New instance
            # Check max instances per user (10)
            existing_count = WhatsAppSession.objects.filter(user=self.user).count()
            if existing_count >= 10:
                raise ValidationError('Maximum 10 WhatsApp instances allowed per user.')
        
        # Ensure only one primary instance per user
        if self.is_primary:
            existing_primary = WhatsAppSession.objects.filter(
                user=self.user, 
                is_primary=True
            ).exclude(pk=self.pk).exists()
            if existing_primary:
                raise ValidationError('Only one primary instance allowed per user.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.user.username} - {self.instance_name} ({self.status})'

