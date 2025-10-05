#!/usr/bin/env python3
"""
Load testing script for WhatsApp Web API SaaS
"""
import asyncio
import aiohttp
import time
import json
import statistics
from typing import List, Dict, Any
import argparse
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django setup
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from users.models import User
from api_keys.models import APIKey


class LoadTester:
    """Load testing utility for the WhatsApp Web API"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
        self.results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make an HTTP request and measure performance"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url, headers=headers) as response:
                    status_code = response.status
                    response_data = await response.json()
            elif method.upper() == 'POST':
                async with self.session.post(url, headers=headers, json=data) as response:
                    status_code = response.status
                    response_data = await response.json()
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                'method': method,
                'endpoint': endpoint,
                'status_code': status_code,
                'response_time': response_time,
                'success': 200 <= status_code < 300,
                'timestamp': start_time
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                'method': method,
                'endpoint': endpoint,
                'status_code': 0,
                'response_time': response_time,
                'success': False,
                'error': str(e),
                'timestamp': start_time
            }
            
            self.results.append(result)
            return result
    
    async def test_user_list(self, iterations: int = 10):
        """Test user list endpoint"""
        print(f"Testing user list endpoint ({iterations} requests)...")
        
        tasks = []
        for _ in range(iterations):
            task = self.make_request('GET', '/api/v1/users/')
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def test_user_detail(self, user_id: int, iterations: int = 10):
        """Test user detail endpoint"""
        print(f"Testing user detail endpoint ({iterations} requests)...")
        
        tasks = []
        for _ in range(iterations):
            task = self.make_request('GET', f'/api/v1/users/{user_id}/')
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def test_session_status(self, iterations: int = 10):
        """Test session status endpoint"""
        print(f"Testing session status endpoint ({iterations} requests)...")
        
        tasks = []
        for _ in range(iterations):
            task = self.make_request('GET', '/api/v1/sessions/status/')
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def test_message_send(self, iterations: int = 5):
        """Test message sending endpoint"""
        print(f"Testing message send endpoint ({iterations} requests)...")
        
        message_data = {
            'recipient': '1234567890',
            'message': 'Load test message'
        }
        
        tasks = []
        for _ in range(iterations):
            task = self.make_request('POST', '/api/v1/messages/send-text/', message_data)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calculate performance statistics"""
        if not self.results:
            return {}
        
        response_times = [r['response_time'] for r in self.results]
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        stats = {
            'total_requests': len(self.results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.results) * 100,
            'response_times': {
                'min': min(response_times),
                'max': max(response_times),
                'mean': statistics.mean(response_times),
                'median': statistics.median(response_times),
                'p95': self._percentile(response_times, 95),
                'p99': self._percentile(response_times, 99),
            },
            'requests_per_second': len(self.results) / max(response_times) if response_times else 0,
        }
        
        return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def print_results(self):
        """Print test results"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("LOAD TEST RESULTS")
        print("="*60)
        
        print(f"Total Requests: {stats.get('total_requests', 0)}")
        print(f"Successful: {stats.get('successful_requests', 0)}")
        print(f"Failed: {stats.get('failed_requests', 0)}")
        print(f"Success Rate: {stats.get('success_rate', 0):.2f}%")
        
        if 'response_times' in stats:
            rt = stats['response_times']
            print(f"\nResponse Times:")
            print(f"  Min: {rt['min']:.3f}s")
            print(f"  Max: {rt['max']:.3f}s")
            print(f"  Mean: {rt['mean']:.3f}s")
            print(f"  Median: {rt['median']:.3f}s")
            print(f"  95th percentile: {rt['p95']:.3f}s")
            print(f"  99th percentile: {rt['p99']:.3f}s")
        
        print(f"Requests per second: {stats.get('requests_per_second', 0):.2f}")
        
        # Show failed requests
        failed_requests = [r for r in self.results if not r['success']]
        if failed_requests:
            print(f"\nFailed Requests:")
            for req in failed_requests[:5]:  # Show first 5 failures
                print(f"  {req['method']} {req['endpoint']} - {req.get('error', 'Unknown error')}")


async def run_load_test(base_url: str, api_key: str, test_type: str, iterations: int):
    """Run load test"""
    async with LoadTester(base_url, api_key) as tester:
        if test_type == 'all':
            await tester.test_user_list(iterations)
            await tester.test_session_status(iterations)
            await tester.test_message_send(min(iterations, 5))  # Limit message sending
        elif test_type == 'users':
            await tester.test_user_list(iterations)
        elif test_type == 'sessions':
            await tester.test_session_status(iterations)
        elif test_type == 'messages':
            await tester.test_message_send(iterations)
        else:
            print(f"Unknown test type: {test_type}")
            return
        
        tester.print_results()


def get_test_api_key():
    """Get or create a test API key"""
    try:
        # Try to get an existing test user
        user = User.objects.filter(username='test_user').first()
        if not user:
            user = User.objects.create_user(
                username='test_user',
                email='test@example.com',
                password='testpass123'
            )
        
        # Get or create API key
        api_key = APIKey.objects.filter(user=user, is_active=True).first()
        if not api_key:
            api_key = APIKey.objects.create(user=user, name='Load Test Key')
            print(f"Created new API key: {api_key._raw_key}")
            return api_key._raw_key
        else:
            # We need the raw key, but it's hashed in the database
            # For testing purposes, we'll create a new one
            api_key.delete()
            api_key = APIKey.objects.create(user=user, name='Load Test Key')
            print(f"Created new API key: {api_key._raw_key}")
            return api_key._raw_key
    
    except Exception as e:
        print(f"Error creating test API key: {e}")
        return None


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Load test the WhatsApp Web API')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL of the API')
    parser.add_argument('--api-key', help='API key for authentication')
    parser.add_argument('--test-type', choices=['all', 'users', 'sessions', 'messages'], 
                       default='all', help='Type of test to run')
    parser.add_argument('--iterations', type=int, default=50, help='Number of requests to make')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key
    if not api_key:
        api_key = get_test_api_key()
        if not api_key:
            print("Failed to get API key. Please provide one with --api-key")
            return 1
    
    print(f"Running load test on {args.url}")
    print(f"Test type: {args.test_type}")
    print(f"Iterations: {args.iterations}")
    print(f"API Key: {api_key[:10]}...")
    
    # Run the test
    asyncio.run(run_load_test(args.url, api_key, args.test_type, args.iterations))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
