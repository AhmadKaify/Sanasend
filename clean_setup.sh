#!/bin/bash
# Clean Setup Script for Linux/Mac
# This script will clean all cache, temporary files, database, and perform a fresh setup

echo -e "\033[0;32mStarting clean setup process...\033[0m"

# Step 1: Remove Python cache files
echo -e "\n\033[0;33m[1/8] Removing Python cache files...\033[0m"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Step 2: Remove database
echo -e "\033[0;33m[2/8] Removing database...\033[0m"
if [ -f "db.sqlite3" ]; then
    rm -f db.sqlite3
    echo -e "\033[0;32mDatabase removed successfully\033[0m"
fi

# Step 3: Remove migration files (keeping __init__.py)
echo -e "\033[0;33m[3/8] Removing migration files...\033[0m"
apps=("analytics" "api_keys" "messages" "sessions" "users")
for app in "${apps[@]}"; do
    migration_path="${app}/migrations"
    if [ -d "$migration_path" ]; then
        find "$migration_path" -type f ! -name "__init__.py" -delete
        find "$migration_path" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
        echo -e "\033[0;37mCleaned migrations for $app\033[0m"
    fi
done

# Step 4: Remove log files
echo -e "\033[0;33m[4/8] Clearing log files...\033[0m"
if [ -f "logs/django.log" ]; then
    > logs/django.log
fi
if [ -d "whatsapp-service/logs" ]; then
    rm -rf whatsapp-service/logs/*
fi

# Step 5: Remove staticfiles
echo -e "\033[0;33m[5/8] Removing collected static files...\033[0m"
if [ -d "staticfiles" ]; then
    rm -rf staticfiles
fi

# Step 6: Remove WhatsApp session data
echo -e "\033[0;33m[6/8] Removing WhatsApp session data...\033[0m"
if [ -d "whatsapp-service/.wwebjs_auth" ]; then
    rm -rf whatsapp-service/.wwebjs_auth
fi
if [ -d "whatsapp-service/.wwebjs_cache" ]; then
    rm -rf whatsapp-service/.wwebjs_cache
fi

# Step 7: Remove node_modules (optional - uncomment if you want to reinstall)
# echo -e "\033[0;33m[7/8] Removing node_modules...\033[0m"
# if [ -d "whatsapp-service/node_modules" ]; then
#     rm -rf whatsapp-service/node_modules
# fi

echo -e "\033[0;37m[7/8] Skipping node_modules removal (uncomment in script to remove)\033[0m"

# Step 8: Remove Django session files and cache
echo -e "\033[0;33m[8/8] Removing Django cache...\033[0m"
if [ -d ".django_cache" ]; then
    rm -rf .django_cache
fi

echo -e "\n\033[0;32mCleanup completed successfully!\033[0m"

# Now perform fresh setup
echo -e "\n\033[0;36m========================================\033[0m"
echo -e "\033[0;36mStarting Fresh Setup...\033[0m"
echo -e "\033[0;36m========================================\033[0m\n"

# Activate virtual environment
echo -e "\033[0;33m[1/5] Activating virtual environment...\033[0m"
source venv/bin/activate

# Create fresh migrations
echo -e "\033[0;33m[2/5] Creating fresh migrations...\033[0m"
python manage.py makemigrations

# Run migrations
echo -e "\033[0;33m[3/5] Running migrations...\033[0m"
python manage.py migrate

# Create superuser (you'll need to provide credentials)
echo -e "\033[0;33m[4/5] Creating superuser...\033[0m"
echo -e "\033[0;37mYou will be prompted to create an admin user...\033[0m"
python manage.py createsuperuser

# Collect static files
echo -e "\033[0;33m[5/5] Collecting static files...\033[0m"
python manage.py collectstatic --noinput

echo -e "\n\033[0;36m========================================\033[0m"
echo -e "\033[0;32mFresh Setup Complete!\033[0m"
echo -e "\033[0;36m========================================\033[0m\n"

echo -e "\033[0;33mNext steps:\033[0m"
echo -e "\033[0;37m1. Start the Django server: python manage.py runserver\033[0m"
echo -e "\033[0;37m2. Start WhatsApp service: cd whatsapp-service && npm start\033[0m"
echo -e "\033[0;37m3. Access admin at: http://localhost:8000/admin/\033[0m"
echo -e "\033[0;37m4. Access dashboard at: http://localhost:8000/dashboard/\033[0m"

