from django.db import models
from django.conf import settings
from core.validators import validate_phone_number


class Message(models.Model):
    """Message model for logging sent messages"""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    recipient = models.CharField(
        max_length=20,
        validators=[validate_phone_number]
    )
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='text'
    )
    content = models.TextField(
        help_text='Text content or file path for media'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', '-sent_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f'{self.user.username} -> {self.recipient} ({self.status})'

