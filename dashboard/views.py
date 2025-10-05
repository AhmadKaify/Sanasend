"""
Dashboard views for WhatsApp Web API SaaS project.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

def landing_page(request):
    """
    Landing page for SanaSend - Auto Sender Provider
    """
    context = {
        'title': 'SanaSend - Auto Sender Provider',
        'description': 'Professional auto sender services for WhatsApp, SMS, Email, Telegram, and Facebook Messenger',
        'keywords': 'auto sender, WhatsApp API, SMS API, Email API, Telegram API, Facebook Messenger API, bulk messaging, automated messaging',
    }
    return render(request, 'dashboard/landing.html', context)

@login_required
def home(request):
    """User dashboard home page"""
    try:
        # Get user's sessions
        user_sessions = request.user.whatsapp_sessions.all()
        
        # Get recent messages
        recent_messages = request.user.messages.all().order_by('-sent_at')[:10]
        
        # Get usage statistics for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        usage_stats = request.user.usage_stats.filter(
            date__gte=thirty_days_ago
        ).aggregate(
            total_messages=Sum('messages_sent'),
            total_sessions=Count('id')
        )
        
        context = {
            'sessions': user_sessions,
            'recent_messages': recent_messages,
            'usage_stats': usage_stats,
            'active_sessions_count': user_sessions.filter(status='active').count(),
        }
        
        return render(request, 'dashboard/home.html', context)
        
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}")
        django_messages.error(request, 'An error occurred while loading the dashboard.')
        return render(request, 'dashboard/home.html', {'sessions': [], 'recent_messages': [], 'usage_stats': {}})

@login_required
def sessions(request):
    """WhatsApp sessions management page"""
    try:
        user_sessions = request.user.whatsapp_sessions.all().order_by('-created_at')
        return render(request, 'dashboard/session.html', {'sessions': user_sessions})
    except Exception as e:
        logger.error(f"Error in sessions view: {str(e)}")
        django_messages.error(request, 'An error occurred while loading sessions.')
        return render(request, 'dashboard/session.html', {'sessions': []})

@login_required
def messages_view(request):
    """Messages management page"""
    try:
        user_messages = request.user.messages.all().order_by('-sent_at')
        return render(request, 'dashboard/messages.html', {'messages': user_messages})
    except Exception as e:
        logger.error(f"Error in messages view: {str(e)}")
        django_messages.error(request, 'An error occurred while loading messages.')
        return render(request, 'dashboard/messages.html', {'messages': []})

@login_required
def api_keys(request):
    """API keys management page"""
    try:
        user_api_keys = request.user.api_keys.all().order_by('-created_at')
        return render(request, 'dashboard/api_keys.html', {'api_keys': user_api_keys})
    except Exception as e:
        logger.error(f"Error in api_keys view: {str(e)}")
        django_messages.error(request, 'An error occurred while loading API keys.')
        return render(request, 'dashboard/api_keys.html', {'api_keys': []})

@login_required
def profile(request):
    """User profile page"""
    return render(request, 'dashboard/profile.html')

@login_required
def analytics(request):
    """User analytics page"""
    try:
        # Get usage statistics for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        usage_stats = request.user.usage_stats.filter(
            date__gte=thirty_days_ago
        ).order_by('date')
        
        # Get daily message counts
        daily_stats = []
        for stat in usage_stats:
            daily_stats.append({
                'date': stat.date.strftime('%Y-%m-%d'),
                'messages_sent': stat.messages_sent,
                'sessions_active': stat.sessions_active,
            })
        
        context = {
            'daily_stats': daily_stats,
            'total_messages': sum(stat.messages_sent for stat in usage_stats),
            'total_sessions': usage_stats.count(),
        }
        
        return render(request, 'dashboard/user_analytics.html', context)
        
    except Exception as e:
        logger.error(f"Error in analytics view: {str(e)}")
        django_messages.error(request, 'An error occurred while loading analytics.')
        return render(request, 'dashboard/user_analytics.html', {'daily_stats': [], 'total_messages': 0, 'total_sessions': 0})

def login_view(request):
    """User login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard:home')
            else:
                django_messages.error(request, 'Invalid username or password.')
        else:
            django_messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'dashboard/login.html')

def logout_view(request):
    """User logout"""
    logout(request)
    return redirect('dashboard:login')

# Admin Dashboard Views
@login_required
def admin_dashboard(request):
    """Admin dashboard for system overview"""
    if not request.user.is_staff:
        django_messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard:home')
    
    try:
        from users.models import User
        from sessions.models import WhatsAppSession
        from messages.models import Message
        from analytics.models import UsageStats
        
        # Get system statistics
        total_users = User.objects.count()
        total_sessions = WhatsAppSession.objects.count()
        total_messages = Message.objects.count()
        active_sessions = WhatsAppSession.objects.filter(status='active').count()
        
        # Get recent activity
        recent_users = User.objects.order_by('-date_joined')[:5]
        recent_sessions = WhatsAppSession.objects.order_by('-created_at')[:5]
        recent_messages = Message.objects.order_by('-created_at')[:5]
        
        # Get usage statistics for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_usage = UsageStats.objects.filter(
            date__gte=thirty_days_ago
        ).order_by('date')
        
        context = {
            'total_users': total_users,
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'active_sessions': active_sessions,
            'recent_users': recent_users,
            'recent_sessions': recent_sessions,
            'recent_messages': recent_messages,
            'daily_usage': daily_usage,
        }
        
        return render(request, 'dashboard/admin_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in admin_dashboard view: {str(e)}")
        django_messages.error(request, 'An error occurred while loading the admin dashboard.')
        return render(request, 'dashboard/admin_dashboard.html', {
            'total_users': 0, 'total_sessions': 0, 'total_messages': 0, 'active_sessions': 0,
            'recent_users': [], 'recent_sessions': [], 'recent_messages': [], 'daily_usage': []
        })

# API Views for AJAX requests
@login_required
@require_http_methods(["POST"])
def test_message(request):
    """Test message sending via AJAX"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        phone_number = data.get('phone_number')
        message_text = data.get('message')
        
        if not all([session_id, phone_number, message_text]):
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        # Here you would integrate with your WhatsApp service
        # For now, we'll just return a success response
        return JsonResponse({
            'success': True,
            'message': 'Test message sent successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in test_message: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An error occurred'})

@login_required
@require_http_methods(["POST"])
def create_session(request):
    """Create new WhatsApp session via AJAX"""
    try:
        data = json.loads(request.body)
        session_name = data.get('session_name')
        
        if not session_name:
            return JsonResponse({'success': False, 'error': 'Session name is required'})
        
        # Here you would create a new session
        # For now, we'll just return a success response
        return JsonResponse({
            'success': True,
            'message': 'Session created successfully',
            'session_id': 'new_session_id'
        })
        
    except Exception as e:
        logger.error(f"Error in create_session: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An error occurred'})