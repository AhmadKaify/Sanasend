from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import UsageStats, APILog


@admin.register(UsageStats)
class UsageStatsAdmin(ModelAdmin):
    """Usage Statistics admin with Unfold styling"""
    
    list_display = ['user', 'date', 'messages_sent', 'api_requests', 'media_sent']
    list_filter = ['date']
    search_fields = ['user__username']
    date_hierarchy = 'date'
    readonly_fields = ['user', 'date']
    list_filter_submit = True
    
    def has_add_permission(self, request):
        return False


@admin.register(APILog)
class APILogAdmin(ModelAdmin):
    """API Log admin with Unfold styling"""
    
    list_display = ['user', 'method', 'endpoint', 'display_status', 'ip_address', 'timestamp']
    list_filter = ['method', 'status_code', 'timestamp']
    search_fields = ['user__username', 'endpoint', 'ip_address']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'endpoint', 'method', 'status_code', 'ip_address', 'timestamp']
    list_filter_submit = True
    
    @display(description="Status Code", label=True)
    def display_status(self, obj):
        if 200 <= obj.status_code < 300:
            return str(obj.status_code), "success"
        elif 400 <= obj.status_code < 500:
            return str(obj.status_code), "warning"
        elif obj.status_code >= 500:
            return str(obj.status_code), "danger"
        return str(obj.status_code), "info"
    
    def has_add_permission(self, request):
        return False

