from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import WhatsAppSession


@admin.register(WhatsAppSession)
class WhatsAppSessionAdmin(ModelAdmin):
    """WhatsApp Session admin with Unfold styling"""
    
    list_display = ['user', 'display_status', 'phone_number', 'connected_at', 'last_active_at']
    list_filter = ['status', 'connected_at']
    search_fields = ['user__username', 'phone_number', 'session_id']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'connected_at']
    list_filter_submit = True
    
    fieldsets = [
        ('User', {
            'fields': ['user']
        }),
        ('Session Info', {
            'fields': ['session_id', 'status', 'phone_number']
        }),
        ('QR Code', {
            'fields': ['qr_code'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['connected_at', 'last_active_at', 'created_at', 'updated_at']
        }),
    ]
    
    actions = ['disconnect_sessions']
    
    @display(description="Session Status", label=True)
    def display_status(self, obj):
        status_map = {
            'connected': ('Connected', 'success'),
            'disconnected': ('Disconnected', 'danger'),
            'qr_pending': ('QR Pending', 'warning'),
        }
        label, color = status_map.get(obj.status, ('Unknown', 'info'))
        return label, color
    
    def disconnect_sessions(self, request, queryset):
        queryset.update(status='disconnected')
        self.message_user(request, f'{queryset.count()} sessions disconnected.')
    disconnect_sessions.short_description = 'Disconnect selected sessions'

