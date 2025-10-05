from django.contrib import admin
from django.contrib import messages
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(ModelAdmin):
    """API Key admin with Unfold styling"""
    
    list_display = ['user', 'name', 'display_status', 'last_used_at', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['key', 'created_at', 'last_used_at']
    list_filter_submit = True
    
    fieldsets = [
        ('User', {
            'fields': ['user', 'name']
        }),
        ('Key Info', {
            'fields': ['key', 'is_active']
        }),
        ('Timestamps', {
            'fields': ['last_used_at', 'created_at']
        }),
    ]
    
    actions = ['activate_keys', 'deactivate_keys']
    
    @display(description="Status", label=True)
    def display_status(self, obj):
        return "Active" if obj.is_active else "Inactive", "success" if obj.is_active else "danger"
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if hasattr(obj, '_raw_key'):
            messages.success(
                request,
                f'API Key created successfully. Key: {obj._raw_key} (save this, it won\'t be shown again)'
            )
    
    def activate_keys(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} API keys activated.')
    activate_keys.short_description = 'Activate selected API keys'
    
    def deactivate_keys(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} API keys deactivated.')
    deactivate_keys.short_description = 'Deactivate selected API keys'

