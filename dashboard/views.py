"""
Dashboard views for SanaSend SaaS project.
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
        
        # Get the first session for display (or None if no sessions)
        session = user_sessions.first() if user_sessions.exists() else None
        
        # Get recent messages
        recent_messages = request.user.messages.all().order_by('-sent_at')[:10]
        
        # Get total message count
        total_messages = request.user.messages.count()
        
        # Get today's message count
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_messages = request.user.messages.filter(sent_at__gte=today_start).count()
        
        # Calculate rate limits (example: 1000 messages per day)
        max_messages = 1000
        rate_limit_remaining = max_messages - daily_messages
        rate_limit_percentage = (daily_messages / max_messages * 100) if max_messages > 0 else 0
        
        # Get API keys count
        api_keys_count = request.user.api_keys.filter(is_active=True).count()
        
        # Get usage statistics for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        usage_stats = request.user.usage_stats.filter(
            date__gte=thirty_days_ago
        ).aggregate(
            total_messages=Sum('messages_sent'),
            total_sessions=Count('id')
        )
        
        # Get Node.js service status (for admins)
        node_service_status = None
        if request.user.is_staff:
            try:
                from core.service_manager import ServiceManager
                service_manager = ServiceManager()
                node_service_status = service_manager.get_service_status()
            except Exception as e:
                logger.warning(f"Could not check Node.js service status: {str(e)}")
        
        context = {
            'session': session,
            'sessions': user_sessions,
            'recent_messages': recent_messages,
            'total_messages': total_messages,
            'daily_messages': daily_messages,
            'max_messages': max_messages,
            'rate_limit_remaining': rate_limit_remaining,
            'rate_limit_percentage': rate_limit_percentage,
            'api_keys_count': api_keys_count,
            'usage_stats': usage_stats,
            'active_sessions_count': user_sessions.filter(status='active').count(),
            'node_service_status': node_service_status,
        }
        
        return render(request, 'dashboard/home.html', context)
        
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}")
        django_messages.error(request, 'An error occurred while loading the dashboard.')
        return render(request, 'dashboard/home.html', {
            'session': None,
            'sessions': [],
            'recent_messages': [],
            'total_messages': 0,
            'daily_messages': 0,
            'max_messages': 1000,
            'rate_limit_remaining': 1000,
            'rate_limit_percentage': 0,
            'api_keys_count': 0,
            'usage_stats': {},
            'active_sessions_count': 0,
        })

@login_required
def sessions(request):
    """WhatsApp sessions management page"""
    try:
        # Handle POST actions
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'add_instance':
                # Add new WhatsApp instance
                from sessions.services import WhatsAppService
                from sessions.models import WhatsAppSession
                
                try:
                    instance_name = request.POST.get('instance_name', '').strip()
                    
                    if not instance_name:
                        django_messages.error(request, 'Instance name is required.')
                        return redirect('dashboard:sessions')
                    
                    # Check if instance name already exists
                    existing = WhatsAppSession.objects.filter(
                        user=request.user,
                        instance_name=instance_name
                    ).first()
                    
                    if existing:
                        django_messages.error(request, f'Instance "{instance_name}" already exists.')
                        return redirect('dashboard:sessions')
                    
                    # Check max instances limit
                    existing_count = WhatsAppSession.objects.filter(user=request.user).count()
                    if existing_count >= 10:
                        django_messages.error(request, 'Maximum 10 instances allowed per user.')
                        return redirect('dashboard:sessions')
                    
                    # Generate session ID
                    session_id = f"user_{request.user.id}_instance_{instance_name.lower().replace(' ', '_')}"
                    
                    # Call Node.js service
                    whatsapp_service = WhatsAppService()
                    result = whatsapp_service.init_session(request.user.id, session_id)
                    
                    if result.get('success'):
                        # Create session in database
                        is_primary = existing_count == 0
                        
                        WhatsAppSession.objects.create(
                            user=request.user,
                            instance_name=instance_name,
                            session_id=session_id,
                            status=result.get('status', 'qr_pending'),
                            qr_code=result.get('qrCode'),
                            qr_expires_at=timezone.now() + timedelta(seconds=60),
                            is_primary=is_primary
                        )
                        
                        django_messages.success(request, f'Instance "{instance_name}" created! Please scan the QR code.')
                    else:
                        django_messages.error(request, f'Failed to create instance: {result.get("error", "Unknown error")}')
                        
                except Exception as e:
                    logger.error(f"Error adding instance: {str(e)}")
                    django_messages.error(request, f'Error: {str(e)}')
                
                return redirect('dashboard:sessions')
            
            elif action == 'reconnect':
                # Reconnect a disconnected session
                from sessions.services import WhatsAppService
                from sessions.models import WhatsAppSession
                
                try:
                    session_id = request.POST.get('session_id')
                    session = WhatsAppSession.objects.filter(user=request.user, id=session_id).first()
                    
                    if not session:
                        django_messages.error(request, 'Session not found.')
                        return redirect('dashboard:sessions')
                    
                    # Generate new session ID for Node.js
                    import time
                    timestamp = int(time.time())
                    new_session_id = f"user_{request.user.id}_instance_{session.instance_name.lower().replace(' ', '_')}_{timestamp}"
                    
                    # Call Node.js service
                    whatsapp_service = WhatsAppService()
                    result = whatsapp_service.init_session(request.user.id, new_session_id)
                    
                    if result.get('success'):
                        session.session_id = new_session_id
                        session.status = result.get('status', 'qr_pending')
                        session.qr_code = result.get('qrCode')
                        session.qr_expires_at = timezone.now() + timedelta(seconds=60)
                        session.save()
                        
                        django_messages.success(request, f'Reconnecting "{session.instance_name}". Please scan the QR code.')
                    else:
                        django_messages.error(request, f'Failed to reconnect: {result.get("error", "Unknown error")}')
                        
                except Exception as e:
                    logger.error(f"Error reconnecting session: {str(e)}")
                    django_messages.error(request, f'Error: {str(e)}')
                
                return redirect('dashboard:sessions')
            
            elif action == 'refresh':
                # Fetch fresh status from Node.js service
                from sessions.services import WhatsAppService
                
                try:
                    session = request.user.whatsapp_sessions.first()
                    if session and session.status in ['qr_pending', 'initializing']:
                        # Query Node.js for current status
                        whatsapp_service = WhatsAppService()
                        result = whatsapp_service.get_session_status(session.session_id)
                        
                        # Update database with fresh status
                        if result.get('status'):
                            old_status = session.status
                            session.status = result['status']
                            session.last_active_at = timezone.now()
                            
                            if result['status'] == 'connected' and result.get('phoneNumber'):
                                session.phone_number = result['phoneNumber']
                                if not session.connected_at:
                                    session.connected_at = timezone.now()
                                # Clear QR code on connection
                                session.qr_code = None
                                session.qr_expires_at = None
                            
                            session.save()
                            
                            # Log status change
                            if old_status != result['status']:
                                logger.info(f"Session {session.session_id} status changed: {old_status} -> {result['status']}")
                except Exception as e:
                    logger.error(f"Error refreshing session status: {str(e)}")
                
                # Return to sessions page
                return redirect('dashboard:sessions')
            
            elif action == 'disconnect':
                # Disconnect session
                from sessions.services import WhatsAppService
                from sessions.models import WhatsAppSession
                
                try:
                    session_id = request.POST.get('session_id')
                    session = WhatsAppSession.objects.filter(user=request.user, id=session_id).first()
                    
                    if session:
                        whatsapp_service = WhatsAppService()
                        whatsapp_service.disconnect_session(session.session_id)
                        session.status = 'disconnected'
                        session.qr_code = None
                        session.qr_expires_at = None
                        session.save()
                        django_messages.success(request, f'"{session.instance_name}" disconnected successfully.')
                    else:
                        django_messages.warning(request, 'Session not found.')
                except Exception as e:
                    logger.error(f"Error disconnecting session: {str(e)}")
                    django_messages.error(request, 'Failed to disconnect session.')
                
                return redirect('dashboard:sessions')
            
            elif action == 'refresh_qr':
                # Refresh QR code
                from sessions.services import WhatsAppService
                from sessions.models import WhatsAppSession
                
                try:
                    session_id = request.POST.get('session_id')
                    session = WhatsAppSession.objects.filter(user=request.user, id=session_id).first()
                    
                    if session:
                        # Disconnect old session
                        whatsapp_service = WhatsAppService()
                        try:
                            whatsapp_service.disconnect_session(session.session_id)
                        except:
                            pass
                        
                        # Generate new session ID with timestamp
                        import time
                        timestamp = int(time.time())
                        new_session_id = f"user_{request.user.id}_instance_{session.instance_name.lower().replace(' ', '_')}_{timestamp}"
                        
                        # Initialize new session
                        result = whatsapp_service.init_session(request.user.id, new_session_id)
                        
                        if result.get('success'):
                            session.session_id = new_session_id
                            session.status = result.get('status', 'qr_pending')
                            session.qr_code = result.get('qrCode')
                            session.qr_expires_at = timezone.now() + timedelta(seconds=60)
                            session.save()
                            django_messages.success(request, f'QR code refreshed for "{session.instance_name}".')
                        else:
                            django_messages.error(request, 'Failed to refresh QR code.')
                    else:
                        django_messages.warning(request, 'Session not found.')
                except Exception as e:
                    logger.error(f"Error refreshing QR: {str(e)}")
                    django_messages.error(request, f'Error: {str(e)}')
                
                return redirect('dashboard:sessions')
            
            elif action == 'set_primary':
                # Set primary session
                from sessions.models import WhatsAppSession
                
                try:
                    session_id = request.POST.get('session_id')
                    target_session = WhatsAppSession.objects.filter(user=request.user, id=session_id).first()
                    
                    if not target_session:
                        django_messages.error(request, 'Session not found.')
                        return redirect('dashboard:sessions')
                    
                    if target_session.status != 'connected':
                        django_messages.error(request, 'Only connected sessions can be set as primary.')
                        return redirect('dashboard:sessions')
                    
                    # Remove primary from all other sessions
                    WhatsAppSession.objects.filter(user=request.user).update(is_primary=False)
                    
                    # Set as primary
                    target_session.is_primary = True
                    target_session.save()
                    
                    django_messages.success(request, f'"{target_session.instance_name}" set as primary instance.')
                except Exception as e:
                    logger.error(f"Error setting primary session: {str(e)}")
                    django_messages.error(request, 'Failed to set primary session.')
                
                return redirect('dashboard:sessions')
            
            elif action == 'delete':
                # Delete session
                from sessions.services import WhatsAppService
                from sessions.models import WhatsAppSession
                
                try:
                    session_id = request.POST.get('session_id')
                    session = WhatsAppSession.objects.filter(user=request.user, id=session_id).first()
                    
                    if not session:
                        django_messages.error(request, 'Session not found.')
                        return redirect('dashboard:sessions')
                    
                    # Disconnect from Node.js if connected
                    if session.status == 'connected':
                        try:
                            whatsapp_service = WhatsAppService()
                            whatsapp_service.disconnect_session(session.session_id)
                        except Exception as e:
                            logger.warning(f'Failed to disconnect before delete: {e}')
                    
                    instance_name = session.instance_name
                    session.delete()
                    
                    django_messages.success(request, f'Instance "{instance_name}" deleted successfully.')
                except Exception as e:
                    logger.error(f"Error deleting session: {str(e)}")
                    django_messages.error(request, 'Failed to delete session.')
                
                return redirect('dashboard:sessions')
        
        # GET request - display sessions
        user_sessions = request.user.whatsapp_sessions.all().order_by('-created_at')
        session = user_sessions.first() if user_sessions.exists() else None
        
        return render(request, 'dashboard/session.html', {
            'sessions': user_sessions,
            'session': session
        })
        
    except Exception as e:
        logger.error(f"Error in sessions view: {str(e)}")
        django_messages.error(request, 'An error occurred while loading sessions.')
        return render(request, 'dashboard/session.html', {'sessions': [], 'session': None})

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
        # Handle POST actions
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'generate':
                # Generate new API key
                from api_keys.models import APIKey
                
                try:
                    key_name = request.POST.get('name', '').strip()
                    
                    # Create new API key
                    api_key = APIKey(
                        user=request.user,
                        name=key_name
                    )
                    api_key.save()
                    
                    # Get the raw key (should be available after save)
                    raw_key = getattr(api_key, '_raw_key', None)
                    
                    if raw_key:
                        django_messages.success(
                            request, 
                            f'API Key generated successfully! Your key: {raw_key} (Save it now - it won\'t be shown again!)'
                        )
                    else:
                        django_messages.success(request, 'API Key generated successfully!')
                        
                except Exception as e:
                    logger.error(f"Error generating API key: {str(e)}")
                    django_messages.error(request, f'Failed to generate API key: {str(e)}')
                
                return redirect('dashboard:api_keys')
            
            elif action == 'deactivate':
                # Deactivate API key
                from api_keys.models import APIKey
                
                try:
                    key_id = request.POST.get('key_id')
                    api_key = APIKey.objects.filter(user=request.user, id=key_id).first()
                    
                    if api_key:
                        api_key.is_active = False
                        api_key.save()
                        django_messages.success(request, 'API key deactivated successfully.')
                    else:
                        django_messages.warning(request, 'API key not found.')
                        
                except Exception as e:
                    logger.error(f"Error deactivating API key: {str(e)}")
                    django_messages.error(request, 'Failed to deactivate API key.')
                
                return redirect('dashboard:api_keys')
        
        # GET request - display API keys
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
def test_sample(request):
    """Test sample page for API testing"""
    api_base_url = request.build_absolute_uri('/api/v1')
    return render(request, 'dashboard/test_sample.html', {'api_base_url': api_base_url})

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
        recent_sessions = WhatsAppSession.objects.select_related('user').order_by('-created_at')[:5]
        recent_messages = Message.objects.select_related('user').order_by('-created_at')[:5]
        
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

# Service Management Views
@login_required
def service_status(request):
    """Service monitoring page"""
    if not request.user.is_staff:
        django_messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard:home')
    
    try:
        from core.service_manager import ServiceManager
        from sessions.models import WhatsAppSession
        
        service_manager = ServiceManager()
        status = service_manager.get_service_status()
        processes = service_manager.get_process_info()
        logs = service_manager.get_service_logs(lines=100)
        
        # Get active sessions that would be affected by restart
        active_sessions = WhatsAppSession.objects.filter(
            status__in=['connected', 'qr_pending']
        ).select_related('user').order_by('-last_active_at')[:20]
        
        context = {
            'status': status,
            'processes': processes,
            'logs': logs,
            'log_count': len(logs),
            'active_sessions': active_sessions,
            'active_sessions_count': active_sessions.count()
        }
        
        return render(request, 'dashboard/service_status.html', context)
        
    except Exception as e:
        logger.error(f"Error in service_status view: {str(e)}")
        django_messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'dashboard/service_status.html', {
            'status': {'running': False, 'healthy': False, 'message': str(e)},
            'processes': [],
            'logs': [],
            'active_sessions': [],
            'active_sessions_count': 0
        })

@login_required
@require_http_methods(["POST"])
def service_action(request):
    """Handle service management actions via AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    try:
        from core.service_manager import ServiceManager
        
        data = json.loads(request.body)
        action = data.get('action')
        
        service_manager = ServiceManager()
        
        if action == 'restart':
            result = service_manager.restart_service()
        elif action == 'start':
            result = service_manager.start_service()
        elif action == 'stop':
            result = service_manager.stop_service()
        elif action == 'status':
            result = service_manager.get_service_status()
            result['success'] = result.get('running', False)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error in service_action: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})