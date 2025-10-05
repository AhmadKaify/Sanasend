"""
Django management command to create performance indexes
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create database indexes for performance optimization'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating performance indexes...')
        
        with connection.cursor() as cursor:
            # Define indexes for better performance
            indexes = [
                # User indexes
                {
                    'name': 'idx_users_username',
                    'table': 'users',
                    'columns': ['username'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username ON users (username);'
                },
                {
                    'name': 'idx_users_email',
                    'table': 'users',
                    'columns': ['email'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);'
                },
                {
                    'name': 'idx_users_active',
                    'table': 'users',
                    'columns': ['is_active'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active ON users (is_active);'
                },
                {
                    'name': 'idx_users_created',
                    'table': 'users',
                    'columns': ['created_at'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created ON users (created_at);'
                },
                
                # API Key indexes
                {
                    'name': 'idx_api_keys_user_active',
                    'table': 'api_keys',
                    'columns': ['user_id', 'is_active'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_user_active ON api_keys (user_id, is_active);'
                },
                {
                    'name': 'idx_api_keys_key',
                    'table': 'api_keys',
                    'columns': ['key'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_key ON api_keys (key);'
                },
                {
                    'name': 'idx_api_keys_expires',
                    'table': 'api_keys',
                    'columns': ['expires_at'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_expires ON api_keys (expires_at);'
                },
                
                # Session indexes
                {
                    'name': 'idx_sessions_user_status',
                    'table': 'whatsapp_sessions',
                    'columns': ['user_id', 'status'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_status ON whatsapp_sessions (user_id, status);'
                },
                {
                    'name': 'idx_sessions_user_primary',
                    'table': 'whatsapp_sessions',
                    'columns': ['user_id', 'is_primary'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_primary ON whatsapp_sessions (user_id, is_primary);'
                },
                {
                    'name': 'idx_sessions_status_active',
                    'table': 'whatsapp_sessions',
                    'columns': ['status', 'last_active_at'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_status_active ON whatsapp_sessions (status, last_active_at);'
                },
                {
                    'name': 'idx_sessions_created',
                    'table': 'whatsapp_sessions',
                    'columns': ['created_at'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_created ON whatsapp_sessions (created_at);'
                },
                
                # Message indexes
                {
                    'name': 'idx_messages_user_sent',
                    'table': 'messages',
                    'columns': ['user_id', 'sent_at'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_user_sent ON messages (user_id, sent_at);'
                },
                {
                    'name': 'idx_messages_status_sent',
                    'table': 'messages',
                    'columns': ['status', 'sent_at'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_status_sent ON messages (status, sent_at);'
                },
                {
                    'name': 'idx_messages_recipient',
                    'table': 'messages',
                    'columns': ['recipient'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_recipient ON messages (recipient);'
                },
                {
                    'name': 'idx_messages_type',
                    'table': 'messages',
                    'columns': ['message_type'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_type ON messages (message_type);'
                },
                
                # Analytics indexes
                {
                    'name': 'idx_usage_stats_user_date',
                    'table': 'usage_stats',
                    'columns': ['user_id', 'date'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usage_stats_user_date ON usage_stats (user_id, date);'
                },
                {
                    'name': 'idx_usage_stats_date',
                    'table': 'usage_stats',
                    'columns': ['date'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usage_stats_date ON usage_stats (date);'
                },
                {
                    'name': 'idx_api_logs_user_timestamp',
                    'table': 'api_logs',
                    'columns': ['user_id', 'timestamp'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_logs_user_timestamp ON api_logs (user_id, timestamp);'
                },
                {
                    'name': 'idx_api_logs_timestamp',
                    'table': 'api_logs',
                    'columns': ['timestamp'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_logs_timestamp ON api_logs (timestamp);'
                },
                {
                    'name': 'idx_api_logs_status',
                    'table': 'api_logs',
                    'columns': ['status_code'],
                    'sql': 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_logs_status ON api_logs (status_code);'
                },
            ]
            
            # Create indexes
            created_count = 0
            failed_count = 0
            
            for index in indexes:
                try:
                    cursor.execute(index['sql'])
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Created index: {index['name']}")
                    )
                    created_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"✗ Failed to create index {index['name']}: {e}")
                    )
                    failed_count += 1
            
            # Summary
            self.stdout.write(f"\nIndex Creation Summary:")
            self.stdout.write(f"  Created: {created_count}")
            self.stdout.write(f"  Failed: {failed_count}")
            self.stdout.write(f"  Total: {len(indexes)}")
            
            if failed_count > 0:
                self.stdout.write(
                    self.style.WARNING("Some indexes failed to create. Check the errors above.")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("All indexes created successfully!")
                )
