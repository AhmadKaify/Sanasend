"""
Django management command to monitor application performance
"""
import time
import psutil
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection
from django.conf import settings
from core.performance import PerformanceMonitor, ConnectionPoolOptimizer


class Command(BaseCommand):
    help = 'Monitor application performance metrics'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Monitoring interval in seconds (default: 60)',
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once and exit',
        )
    
    def handle(self, *args, **options):
        if options['once']:
            self.monitor_once()
        else:
            self.monitor_continuous(options['interval'])
    
    def monitor_once(self):
        """Run performance monitoring once"""
        self.stdout.write('Performance Monitoring Report')
        self.stdout.write('=' * 50)
        
        # System metrics
        self.print_system_metrics()
        
        # Database metrics
        self.print_database_metrics()
        
        # Cache metrics
        self.print_cache_metrics()
        
        # Application metrics
        self.print_application_metrics()
    
    def monitor_continuous(self, interval):
        """Run continuous performance monitoring"""
        self.stdout.write(f'Starting continuous monitoring (interval: {interval}s)')
        self.stdout.write('Press Ctrl+C to stop')
        
        try:
            while True:
                self.monitor_once()
                self.stdout.write(f'\nWaiting {interval} seconds...\n')
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write('\nMonitoring stopped.')
    
    def print_system_metrics(self):
        """Print system performance metrics"""
        self.stdout.write('\nSystem Metrics:')
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.stdout.write(f'  CPU Usage: {cpu_percent}%')
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.stdout.write(f'  Memory Usage: {memory.percent}% ({memory.used / 1024 / 1024 / 1024:.1f}GB / {memory.total / 1024 / 1024 / 1024:.1f}GB)')
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.stdout.write(f'  Disk Usage: {disk.percent}% ({disk.used / 1024 / 1024 / 1024:.1f}GB / {disk.total / 1024 / 1024 / 1024:.1f}GB)')
        
        # Load average
        load_avg = psutil.getloadavg()
        self.stdout.write(f'  Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}')
    
    def print_database_metrics(self):
        """Print database performance metrics"""
        self.stdout.write('\nDatabase Metrics:')
        
        # Connection stats
        conn_stats = ConnectionPoolOptimizer.get_connection_stats()
        for alias, stats in conn_stats.items():
            self.stdout.write(f'  {alias}: Usable={stats["is_usable"]}, Queries={stats["queries"]}')
        
        # Query count
        query_count = len(connection.queries)
        self.stdout.write(f'  Total Queries: {query_count}')
        
        # Slow queries
        slow_queries = [q for q in connection.queries if float(q['time']) > 0.1]
        if slow_queries:
            self.stdout.write(f'  Slow Queries (>0.1s): {len(slow_queries)}')
            for query in slow_queries[:5]:  # Show first 5 slow queries
                self.stdout.write(f'    {query["time"]}s: {query["sql"][:100]}...')
    
    def print_cache_metrics(self):
        """Print cache performance metrics"""
        self.stdout.write('\nCache Metrics:')
        
        # Test cache operations
        test_key = 'performance_test'
        start_time = time.time()
        
        try:
            cache.set(test_key, 'test_value', 60)
            cache.get(test_key)
            cache.delete(test_key)
            
            operation_time = time.time() - start_time
            self.stdout.write(f'  Cache Operations: {operation_time:.3f}s')
            
            # Get cache stats if available
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_stats'):
                stats = cache._cache.get_stats()
                self.stdout.write(f'  Cache Stats: {stats}')
            
        except Exception as e:
            self.stdout.write(f'  Cache Error: {e}')
    
    def print_application_metrics(self):
        """Print application-specific metrics"""
        self.stdout.write('\nApplication Metrics:')
        
        # Get performance data from cache
        performance_keys = [
            'performance:user_list',
            'performance:session_list',
            'performance:message_list',
            'performance:analytics_dashboard',
        ]
        
        for key in performance_keys:
            perf_data = cache.get(key)
            if perf_data:
                self.stdout.write(f'  {key}: {perf_data["execution_time"]:.3f}s, {perf_data["query_count"]} queries')
        
        # Get rate limiting stats
        rate_limit_keys = cache.keys('rate_limit:*')
        if rate_limit_keys:
            self.stdout.write(f'  Rate Limit Keys: {len(rate_limit_keys)}')
        
        # Get usage tracking stats
        usage_keys = cache.keys('usage:*')
        if usage_keys:
            self.stdout.write(f'  Usage Tracking Keys: {len(usage_keys)}')
