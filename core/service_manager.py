"""
Service Manager for Node.js WhatsApp Service
Handles monitoring and management of the Node.js service
"""
import subprocess
import requests
import logging
import platform
from django.conf import settings

logger = logging.getLogger(__name__)


class ServiceManager:
    """Manager for the Node.js WhatsApp service"""
    
    def __init__(self):
        self.node_url = getattr(settings, 'NODE_SERVICE_URL', 'http://localhost:3000')
        self.is_windows = platform.system().lower() == 'windows'
    
    def get_service_status(self):
        """
        Get current status of the Node.js service
        Returns dict with status information
        """
        try:
            # Try to reach the health endpoint
            response = requests.get(f"{self.node_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'running': True,
                    'healthy': data.get('status') == 'healthy',
                    'uptime': data.get('uptime', 0),
                    'timestamp': data.get('timestamp'),
                    'message': 'Service is running and healthy',
                    'url': self.node_url
                }
            else:
                return {
                    'running': True,
                    'healthy': False,
                    'message': f'Service responded with status {response.status_code}',
                    'url': self.node_url
                }
        except requests.exceptions.ConnectionError:
            return {
                'running': False,
                'healthy': False,
                'message': 'Cannot connect to service - it may be stopped',
                'url': self.node_url
            }
        except requests.exceptions.Timeout:
            return {
                'running': False,
                'healthy': False,
                'message': 'Service timeout - it may be unresponsive',
                'url': self.node_url
            }
        except Exception as e:
            logger.error(f"Error checking service status: {str(e)}")
            return {
                'running': False,
                'healthy': False,
                'message': f'Error checking status: {str(e)}',
                'url': self.node_url
            }
    
    def get_process_info(self):
        """
        Get process information for Node.js service
        Returns list of matching processes
        """
        try:
            if self.is_windows:
                # Windows: Use tasklist
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq node.exe', '/FO', 'CSV'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:
                # Linux/Mac: Use ps
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            
            if result.returncode == 0:
                processes = []
                lines = result.stdout.strip().split('\n')
                
                for line in lines:
                    # Look for whatsapp-service or node processes
                    if 'whatsapp-service' in line.lower() or 'server.js' in line.lower():
                        processes.append(line.strip())
                
                return processes
            else:
                logger.error(f"Failed to get process info: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout getting process info")
            return []
        except Exception as e:
            logger.error(f"Error getting process info: {str(e)}")
            return []
    
    def restart_service(self):
        """
        Attempt to restart the Node.js service
        This is platform-specific and may require proper setup
        """
        try:
            # First, try to gracefully stop
            try:
                requests.post(f"{self.node_url}/shutdown", timeout=5)
            except:
                pass
            
            # Kill any remaining processes
            if self.is_windows:
                subprocess.run(
                    ['taskkill', '/F', '/IM', 'node.exe', '/FI', 'WINDOWTITLE eq whatsapp-service*'],
                    capture_output=True,
                    timeout=10
                )
            else:
                # On Linux, find and kill the process
                result = subprocess.run(
                    ['pgrep', '-f', 'whatsapp-service'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            subprocess.run(['kill', pid], timeout=5)
            
            # Start the service
            return self.start_service()
            
        except Exception as e:
            logger.error(f"Error restarting service: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to restart: {str(e)}'
            }
    
    def start_service(self):
        """
        Attempt to start the Node.js service
        """
        try:
            import os
            
            # Get the whatsapp-service directory
            service_dir = settings.BASE_DIR / 'whatsapp-service'
            
            if not service_dir.exists():
                return {
                    'success': False,
                    'message': 'WhatsApp service directory not found'
                }
            
            # Check if npm/node is available
            try:
                subprocess.run(['node', '--version'], capture_output=True, timeout=5)
            except:
                return {
                    'success': False,
                    'message': 'Node.js is not installed or not in PATH'
                }
            
            # Start the service in the background
            if self.is_windows:
                # Windows: Start in new window
                subprocess.Popen(
                    ['start', 'cmd', '/c', 'npm', 'start'],
                    cwd=str(service_dir),
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Linux/Mac: Start with nohup
                subprocess.Popen(
                    ['nohup', 'npm', 'start', '&'],
                    cwd=str(service_dir),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setpgrp
                )
            
            return {
                'success': True,
                'message': 'Service start initiated. Please wait a few seconds for it to be ready.'
            }
            
        except Exception as e:
            logger.error(f"Error starting service: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to start: {str(e)}'
            }
    
    def stop_service(self):
        """
        Attempt to stop the Node.js service
        """
        try:
            # Try graceful shutdown first
            try:
                response = requests.post(f"{self.node_url}/shutdown", timeout=5)
                if response.status_code == 200:
                    return {
                        'success': True,
                        'message': 'Service stopped gracefully'
                    }
            except:
                pass
            
            # Force kill
            if self.is_windows:
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', 'node.exe', '/FI', 'WINDOWTITLE eq whatsapp-service*'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    ['pgrep', '-f', 'whatsapp-service'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            subprocess.run(['kill', '-9', pid], timeout=5)
            
            return {
                'success': True,
                'message': 'Service stopped'
            }
            
        except Exception as e:
            logger.error(f"Error stopping service: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to stop: {str(e)}'
            }
    
    def get_service_logs(self, lines=50):
        """
        Get recent logs from the Node.js service
        """
        try:
            log_file = settings.BASE_DIR / 'whatsapp-service' / 'logs' / 'combined.log'
            
            if not log_file.exists():
                return []
            
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
                
        except Exception as e:
            logger.error(f"Error reading service logs: {str(e)}")
            return []

