"""
Dashboard URLs
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, admin_views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard pages
    path('', views.home, name='home'),
    path('sessions/', views.sessions, name='sessions'),
    path('messages/', views.messages_view, name='messages'),
    path('api-keys/', views.api_keys, name='api_keys'),
    path('analytics/', views.analytics, name='analytics'),
    path('profile/', views.profile, name='profile'),
    path('test-sample/', views.test_sample, name='test_sample'),
    
    # Admin dashboard
    path('admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/user/<int:user_id>/', admin_views.user_analytics, name='user_analytics'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Service Management
    path('service-status/', views.service_status, name='service_status'),
    path('service-action/', views.service_action, name='service_action'),
]


