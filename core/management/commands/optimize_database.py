"""
Django management command to optimize database performance
"""
from django.core.management.base import BaseCommand
from django.db import connection
from core.performance import DatabaseOptimizer


class Command(BaseCommand):
    help = 'Optimize database performance by adding indexes and analyzing queries'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Analyze database performance',
        )
        parser.add_argument(
            '--indexes',
            action='store_true',
            help='Add performance indexes',
        )
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Vacuum database tables',
        )
    
    def handle(self, *args, **options):
        if options['analyze']:
            self.analyze_database()
        
        if options['indexes']:
            self.add_indexes()
        
        if options['vacuum']:
            self.vacuum_database()
        
        if not any(options.values()):
            self.stdout.write(
                self.style.WARNING('No options specified. Use --help for available options.')
            )
    
    def analyze_database(self):
        """Analyze database performance"""
        self.stdout.write('Analyzing database performance...')
        
        with connection.cursor() as cursor:
            # Get table sizes
            cursor.execute("""
                SELECT schemaname, tablename, 
                       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """)
            
            self.stdout.write('\nTable Sizes:')
            for row in cursor.fetchall():
                self.stdout.write(f"  {row[1]}: {row[2]}")
            
            # Get index usage
            cursor.execute("""
                SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes 
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC;
            """)
            
            self.stdout.write('\nIndex Usage:')
            for row in cursor.fetchall():
                self.stdout.write(f"  {row[2]} on {row[1]}: {row[3]} scans")
    
    def add_indexes(self):
        """Add performance indexes"""
        self.stdout.write('Adding performance indexes...')
        
        with connection.cursor() as cursor:
            # Add indexes for common queries
            indexes = [
                # User indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username ON users (username);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active ON users (is_active);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created ON users (created_at);",
                
                # API Key indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_user_active ON api_keys (user_id, is_active);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_key ON api_keys (key);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_expires ON api_keys (expires_at);",
                
                # Session indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_status ON whatsapp_sessions (user_id, status);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_primary ON whatsapp_sessions (user_id, is_primary);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_status_active ON whatsapp_sessions (status, last_active_at);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_created ON whatsapp_sessions (created_at);",
                
                # Message indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_user_sent ON messages (user_id, sent_at);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_status_sent ON messages (status, sent_at);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_recipient ON messages (recipient);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_type ON messages (message_type);",
                
                # Analytics indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usage_stats_user_date ON usage_stats (user_id, date);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usage_stats_date ON usage_stats (date);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_logs_user_timestamp ON api_logs (user_id, timestamp);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_logs_timestamp ON api_logs (timestamp);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_logs_status ON api_logs (status_code);",
            ]
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    self.stdout.write(f"  ✓ Added index: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Failed to add index: {e}")
                    )
    
    def vacuum_database(self):
        """Vacuum database tables"""
        self.stdout.write('Vacuuming database tables...')
        
        with connection.cursor() as cursor:
            # Get all tables
            cursor.execute("""
                SELECT tablename FROM pg_tables WHERE schemaname = 'public';
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                try:
                    cursor.execute(f"VACUUM ANALYZE {table};")
                    self.stdout.write(f"  ✓ Vacuumed {table}")
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Failed to vacuum {table}: {e}")
                    )
