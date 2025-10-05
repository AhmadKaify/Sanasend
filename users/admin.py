from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Custom User admin with Unfold styling"""
    
    list_display = ['username', 'email', 'display_status', 'is_staff', 'max_messages_per_day', 'created_at']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    list_filter_submit = True
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('max_messages_per_day', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['activate_users', 'deactivate_users']
    
    @display(description="Status", label=True)
    def display_status(self, obj):
        return "Active" if obj.is_active else "Inactive", "success" if obj.is_active else "danger"
    
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} users activated successfully.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} users deactivated successfully.')
    deactivate_users.short_description = 'Deactivate selected users'

