from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Message


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    """Message admin with Unfold styling"""
    
    list_display = ['user', 'recipient', 'message_type', 'display_status', 'sent_at']
    list_filter = ['status', 'message_type', 'sent_at']
    search_fields = ['user__username', 'recipient', 'content']
    readonly_fields = ['sent_at']
    date_hierarchy = 'sent_at'
    list_filter_submit = True
    
    fieldsets = [
        ('Message Info', {
            'fields': ['user', 'recipient', 'message_type', 'content']
        }),
        ('Status', {
            'fields': ['status', 'error_message']
        }),
        ('Timestamp', {
            'fields': ['sent_at']
        }),
    ]
    
    @display(description="Message Status", label=True)
    def display_status(self, obj):
        status_map = {
            'sent': ('Sent', 'success'),
            'pending': ('Pending', 'warning'),
            'failed': ('Failed', 'danger'),
        }
        label, color = status_map.get(obj.status, ('Unknown', 'info'))
        return label, color
    
    def has_add_permission(self, request):
        # Messages should only be created via API
        return False

