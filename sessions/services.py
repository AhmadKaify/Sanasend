"""
WhatsApp service integration layer
Communicates with Node.js WhatsApp service
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from core.exceptions import APIException
import logging

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service to communicate with Node.js WhatsApp service"""
    
    # Shared session for connection pooling
    _http_session = None
    
    def __init__(self):
        self.base_url = settings.NODE_SERVICE_URL
        self.api_key = settings.NODE_SERVICE_API_KEY
        self.timeout = 60  # Increased timeout for QR generation
    
    @classmethod
    def get_http_session(cls):
        """Get or create a shared HTTP session with connection pooling"""
        if cls._http_session is None:
            cls._http_session = requests.Session()
            
            # Configure retry strategy
            retry_strategy = Retry(
                total=3,  # Maximum number of retries
                backoff_factor=0.3,  # Wait 0.3, 0.6, 1.2 seconds between retries
                status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
                allowed_methods=["GET", "POST"]  # Retry on these methods
            )
            
            # Configure adapter with connection pooling
            adapter = HTTPAdapter(
                pool_connections=20,  # Number of connection pools to cache
                pool_maxsize=50,  # Max number of connections in the pool
                max_retries=retry_strategy
            )
            
            # Mount adapter for both http and https
            cls._http_session.mount('http://', adapter)
            cls._http_session.mount('https://', adapter)
            
            logger.info('Initialized HTTP session with connection pooling (pool_size=50)')
        
        return cls._http_session
    
    def _make_request(self, method, endpoint, data=None, timeout=None):
        """
        Make HTTP request to Node.js service using connection pooling
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
        
        # Use shared session for connection pooling
        session = self.get_http_session()
        
        try:
            if method == 'GET':
                response = session.get(url, headers=headers, timeout=timeout or self.timeout)
            elif method == 'POST':
                response = session.post(url, json=data, headers=headers, timeout=timeout or self.timeout)
            else:
                raise ValueError(f'Unsupported HTTP method: {method}')
            
            response.raise_for_status()
            return response.json()
        
        except requests.Timeout:
            logger.error(f'Timeout connecting to WhatsApp service: {url}')
            raise APIException('WhatsApp service timeout')
        except requests.ConnectionError:
            logger.error(f'Connection error to WhatsApp service: {url}')
            raise APIException('WhatsApp service unavailable')
        except requests.HTTPError as e:
            logger.error(f'HTTP error from WhatsApp service: {e}')
            raise APIException(f'WhatsApp service error: {e.response.text}')
        except Exception as e:
            logger.error(f'Unexpected error calling WhatsApp service: {e}')
            raise APIException(f'WhatsApp service error: {str(e)}')
    
    def init_session(self, user_id, session_id):
        """
        Initialize WhatsApp session and get QR code
        """
        data = {
            'userId': user_id,
            'sessionId': session_id
        }
        return self._make_request('POST', '/api/session/init', data)
    
    def get_session_status(self, session_id):
        """
        Get current session status
        """
        return self._make_request('GET', f'/api/session/status/{session_id}', timeout=10)
    
    def disconnect_session(self, session_id):
        """
        Disconnect WhatsApp session
        """
        data = {'sessionId': session_id}
        return self._make_request('POST', '/api/session/disconnect', data, timeout=10)
    
    def send_text_message(self, session_id, recipient, message):
        """
        Send text message via WhatsApp
        """
        data = {
            'sessionId': session_id,
            'recipient': recipient,
            'message': message
        }
        return self._make_request('POST', '/api/message/send-text', data, timeout=30)
    
    def send_media_message(self, session_id, recipient, media_url, caption='', media_type='image'):
        """
        Send media message via WhatsApp
        """
        data = {
            'sessionId': session_id,
            'recipient': recipient,
            'mediaUrl': media_url,
            'caption': caption,
            'mediaType': media_type
        }
        return self._make_request('POST', '/api/message/send-media', data, timeout=60)
    
    def check_health(self):
        """
        Check if WhatsApp service is healthy
        """
        try:
            session = self.get_http_session()
            response = session.get(f'{self.base_url}/health', timeout=5)
            return response.status_code == 200
        except:
            return False

