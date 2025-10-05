# Clean Setup Script for Windows PowerShell
# This script will clean all cache, temporary files, database, and perform a fresh setup

Write-Host "Starting clean setup process..." -ForegroundColor Green

# Step 1: Remove Python cache files
Write-Host "`n[1/8] Removing Python cache files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File | Remove-Item -Force
Get-ChildItem -Path . -Filter "*.pyo" -Recurse -File | Remove-Item -Force

# Step 2: Remove database
Write-Host "[2/8] Removing database..." -ForegroundColor Yellow
if (Test-Path "db.sqlite3") {
    Remove-Item "db.sqlite3" -Force
    Write-Host "Database removed successfully" -ForegroundColor Green
}

# Step 3: Remove migration files (keeping __init__.py)
Write-Host "[3/8] Removing migration files..." -ForegroundColor Yellow
$apps = @("analytics", "api_keys", "messages", "sessions", "users")
foreach ($app in $apps) {
    $migrationPath = "$app\migrations"
    if (Test-Path $migrationPath) {
        Get-ChildItem -Path $migrationPath -Exclude "__init__.py" | Remove-Item -Recurse -Force
        Write-Host "Cleaned migrations for $app" -ForegroundColor Gray
    }
}

# Step 4: Remove log files
Write-Host "[4/8] Clearing log files..." -ForegroundColor Yellow
if (Test-Path "logs\django.log") {
    Clear-Content "logs\django.log"
}
if (Test-Path "whatsapp-service\logs") {
    Get-ChildItem -Path "whatsapp-service\logs" -File | Remove-Item -Force
}

# Step 5: Remove staticfiles
Write-Host "[5/8] Removing collected static files..." -ForegroundColor Yellow
if (Test-Path "staticfiles") {
    Remove-Item "staticfiles" -Recurse -Force
}

# Step 6: Remove WhatsApp session data
Write-Host "[6/8] Removing WhatsApp session data..." -ForegroundColor Yellow
if (Test-Path "whatsapp-service\.wwebjs_auth") {
    Remove-Item "whatsapp-service\.wwebjs_auth" -Recurse -Force
}
if (Test-Path "whatsapp-service\.wwebjs_cache") {
    Remove-Item "whatsapp-service\.wwebjs_cache" -Recurse -Force
}

# Step 7: Remove node_modules (optional - uncomment if you want to reinstall)
# Write-Host "[7/8] Removing node_modules..." -ForegroundColor Yellow
# if (Test-Path "whatsapp-service\node_modules") {
#     Remove-Item "whatsapp-service\node_modules" -Recurse -Force
# }

Write-Host "[7/8] Skipping node_modules removal (uncomment in script to remove)" -ForegroundColor Gray

# Step 8: Remove Django session files and cache
Write-Host "[8/8] Removing Django cache..." -ForegroundColor Yellow
if (Test-Path ".django_cache") {
    Remove-Item ".django_cache" -Recurse -Force
}

Write-Host "`nCleanup completed successfully!" -ForegroundColor Green

# Now perform fresh setup
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Starting Fresh Setup..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Activate virtual environment
Write-Host "[1/5] Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Create fresh migrations
Write-Host "[2/5] Creating fresh migrations..." -ForegroundColor Yellow
python manage.py makemigrations

# Run migrations
Write-Host "[3/5] Running migrations..." -ForegroundColor Yellow
python manage.py migrate

# Create superuser (you'll need to provide credentials)
Write-Host "[4/5] Creating superuser..." -ForegroundColor Yellow
Write-Host "You will be prompted to create an admin user..." -ForegroundColor Gray
python manage.py createsuperuser

# Collect static files
Write-Host "[5/5] Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Fresh Setup Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start the Django server: python manage.py runserver" -ForegroundColor White
Write-Host "2. Start WhatsApp service: cd whatsapp-service && npm start" -ForegroundColor White
Write-Host "3. Access admin at: http://localhost:8000/admin/" -ForegroundColor White
Write-Host "4. Access dashboard at: http://localhost:8000/dashboard/" -ForegroundColor White

