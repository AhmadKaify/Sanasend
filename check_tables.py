import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE 'whatsapp_%' OR name LIKE 'sessions_%' OR name LIKE 'messages_%')")
tables = cursor.fetchall()

print("Current tables:")
for table in tables:
    print(f"  - {table[0]}")

