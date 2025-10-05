"""
Health check utilities for the WhatsApp Web API SaaS
"""
import psutil
import redis
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)


def check_database():
    """Check database connectivity"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"


def check_redis():
    """Check Redis connectivity"""
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=getattr(settings, 'REDIS_PASSWORD', None),
            socket_connect_timeout=5
        )
        r.ping()
        return True, "Redis connection successful"
    except Exception as e:
        return False, f"Redis connection failed: {str(e)}"


def check_disk_space():
    """Check available disk space"""
    try:
        disk_usage = psutil.disk_usage('/')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        min_free = getattr(settings, 'HEALTH_CHECK', {}).get('DISK_USAGE_MAX', 90)
        
        if free_percent < (100 - min_free):
            return False, f"Disk space low: {free_percent:.1f}% free"
        return True, f"Disk space OK: {free_percent:.1f}% free"
    except Exception as e:
        return False, f"Disk space check failed: {str(e)}"


def check_memory():
    """Check available memory"""
    try:
        memory = psutil.virtual_memory()
        min_memory = getattr(settings, 'HEALTH_CHECK', {}).get('MEMORY_MIN', 100) * 1024 * 1024  # Convert to bytes
        
        if memory.available < min_memory:
            return False, f"Memory low: {memory.available / 1024 / 1024:.1f}MB available"
        return True, f"Memory OK: {memory.available / 1024 / 1024:.1f}MB available"
    except Exception as e:
        return False, f"Memory check failed: {str(e)}"


def check_node_service():
    """Check Node.js WhatsApp service"""
    try:
        import requests
        node_url = getattr(settings, 'NODE_SERVICE_URL', 'http://localhost:3000')
        response = requests.get(f"{node_url}/health", timeout=5)
        if response.status_code == 200:
            return True, "Node.js service is healthy"
        else:
            return False, f"Node.js service returned status {response.status_code}"
    except Exception as e:
        return False, f"Node.js service check failed: {str(e)}"


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Comprehensive health check endpoint
    Returns the status of all critical services
    """
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'disk_space': check_disk_space(),
        'memory': check_memory(),
        'node_service': check_node_service(),
    }
    
    # Determine overall health
    all_healthy = all(status for status, _ in checks.values())
    overall_status = 'healthy' if all_healthy else 'unhealthy'
    
    # Prepare response
    response_data = {
        'status': overall_status,
        'checks': {
            name: {
                'status': 'healthy' if status else 'unhealthy',
                'message': message
            }
            for name, (status, message) in checks.items()
        },
        'timestamp': str(psutil.boot_time()),
        'version': '1.0.0'
    }
    
    # Log health check
    if not all_healthy:
        logger.warning(f"Health check failed: {response_data}")
    else:
        logger.info("Health check passed")
    
    # Return appropriate HTTP status
    http_status = 200 if all_healthy else 503
    
    return JsonResponse(response_data, status=http_status)


@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check for Kubernetes/Docker
    Checks if the service is ready to accept traffic
    """
    # Only check critical services for readiness
    critical_checks = {
        'database': check_database(),
        'redis': check_redis(),
    }
    
    all_ready = all(status for status, _ in critical_checks.values())
    
    response_data = {
        'status': 'ready' if all_ready else 'not_ready',
        'checks': {
            name: {
                'status': 'ready' if status else 'not_ready',
                'message': message
            }
            for name, (status, message) in critical_checks.items()
        }
    }
    
    http_status = 200 if all_ready else 503
    return JsonResponse(response_data, status=http_status)


@csrf_exempt
@require_http_methods(["GET"])
def liveness_check(request):
    """
    Liveness check for Kubernetes/Docker
    Checks if the service is alive
    """
    # Simple liveness check - if we can respond, we're alive
    return JsonResponse({
        'status': 'alive',
        'timestamp': str(psutil.boot_time())
    })
