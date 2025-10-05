# Production Cleanup Script for Windows
# This script cleans all development artifacts and prepares the project for production deployment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Production Cleanup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$itemsToRemove = @()

# Check for __pycache__ directories
Write-Host "Scanning for __pycache__ directories..." -ForegroundColor Yellow
$pycacheDirs = Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
$itemsToRemove += $pycacheDirs
Write-Host "Found $($pycacheDirs.Count) __pycache__ directories" -ForegroundColor Gray

# Check for .pyc and .pyo files
Write-Host "Scanning for .pyc and .pyo files..." -ForegroundColor Yellow
$pycFiles = Get-ChildItem -Path . -Recurse -Include "*.pyc", "*.pyo" -File -ErrorAction SilentlyContinue
$itemsToRemove += $pycFiles
Write-Host "Found $($pycFiles.Count) .pyc/.pyo files" -ForegroundColor Gray

# Check for database
Write-Host "Checking for database file..." -ForegroundColor Yellow
if (Test-Path "db.sqlite3") {
    $itemsToRemove += Get-Item "db.sqlite3"
    Write-Host "Found db.sqlite3" -ForegroundColor Gray
}
if (Test-Path "db.sqlite3-journal") {
    $itemsToRemove += Get-Item "db.sqlite3-journal"
    Write-Host "Found db.sqlite3-journal" -ForegroundColor Gray
}

# Check for logs
Write-Host "Checking for log files..." -ForegroundColor Yellow
if (Test-Path "logs") {
    $logFiles = Get-ChildItem -Path "logs" -Recurse -File -ErrorAction SilentlyContinue
    $itemsToRemove += $logFiles
    Write-Host "Found $($logFiles.Count) log files" -ForegroundColor Gray
}

# Check for staticfiles (collected static)
Write-Host "Checking for staticfiles directory..." -ForegroundColor Yellow
if (Test-Path "staticfiles") {
    $itemsToRemove += Get-Item "staticfiles"
    Write-Host "Found staticfiles directory" -ForegroundColor Gray
}

# Check for migration files (except __init__.py)
Write-Host "Checking for migration files..." -ForegroundColor Yellow
$migrationFiles = Get-ChildItem -Path . -Recurse -Filter "migrations" -Directory -ErrorAction SilentlyContinue | 
    ForEach-Object { Get-ChildItem -Path $_.FullName -Filter "*.py" -File } | 
    Where-Object { $_.Name -ne "__init__.py" }
$itemsToRemove += $migrationFiles
Write-Host "Found $($migrationFiles.Count) migration files" -ForegroundColor Gray

# Check for .env file
Write-Host "Checking for .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "Found .env file (will be backed up as .env.backup)" -ForegroundColor Yellow
}

# Check for node_modules in whatsapp-service
Write-Host "Checking for node_modules..." -ForegroundColor Yellow
if (Test-Path "whatsapp-service\node_modules") {
    $itemsToRemove += Get-Item "whatsapp-service\node_modules"
    Write-Host "Found whatsapp-service\node_modules" -ForegroundColor Gray
}

# Check for WhatsApp session data
Write-Host "Checking for WhatsApp session data..." -ForegroundColor Yellow
if (Test-Path "whatsapp-service\.wwebjs_auth") {
    $itemsToRemove += Get-Item "whatsapp-service\.wwebjs_auth"
    Write-Host "Found whatsapp-service\.wwebjs_auth" -ForegroundColor Gray
}
if (Test-Path "whatsapp-service\.wwebjs_cache") {
    $itemsToRemove += Get-Item "whatsapp-service\.wwebjs_cache"
    Write-Host "Found whatsapp-service\.wwebjs_cache" -ForegroundColor Gray
}

# Check for test files
Write-Host "Checking for test coverage files..." -ForegroundColor Yellow
$testFiles = Get-ChildItem -Path . -Include ".coverage", "coverage.xml", ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
$itemsToRemove += $testFiles
Write-Host "Found $($testFiles.Count) test coverage files/directories" -ForegroundColor Gray

# Check for Redis dump
Write-Host "Checking for Redis dump..." -ForegroundColor Yellow
if (Test-Path "dump.rdb") {
    $itemsToRemove += Get-Item "dump.rdb"
    Write-Host "Found dump.rdb" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total items to remove: $($itemsToRemove.Count)" -ForegroundColor Yellow
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Do you want to proceed with cleanup? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "Cleanup cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Starting cleanup..." -ForegroundColor Green

# Backup .env if it exists
if (Test-Path ".env") {
    Copy-Item ".env" ".env.backup" -Force
    Write-Host "✓ Backed up .env to .env.backup" -ForegroundColor Green
}

# Remove items
$removedCount = 0
foreach ($item in $itemsToRemove) {
    try {
        if ($item.PSIsContainer) {
            Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction Stop
        } else {
            Remove-Item -Path $item.FullName -Force -ErrorAction Stop
        }
        $removedCount++
    } catch {
        Write-Host "✗ Failed to remove: $($item.FullName)" -ForegroundColor Red
    }
}

Write-Host "✓ Removed $removedCount items" -ForegroundColor Green

# Create fresh logs directory
if (-not (Test-Path "logs")) {
    New-Item -Path "logs" -ItemType Directory -Force | Out-Null
    Write-Host "✓ Created fresh logs directory" -ForegroundColor Green
}

# Create .gitkeep in logs
New-Item -Path "logs\.gitkeep" -ItemType File -Force | Out-Null
Write-Host "✓ Created logs\.gitkeep" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps for production deployment:" -ForegroundColor Yellow
Write-Host "1. Update .env file with production settings" -ForegroundColor White
Write-Host "2. Set DEBUG=False" -ForegroundColor White
Write-Host "3. Update ALLOWED_HOSTS with your domain" -ForegroundColor White
Write-Host "4. Generate a strong SECRET_KEY" -ForegroundColor White
Write-Host "5. Configure production database (PostgreSQL recommended)" -ForegroundColor White
Write-Host "6. Set up Redis for production" -ForegroundColor White
Write-Host "7. Run migrations on production server" -ForegroundColor White
Write-Host "8. Collect static files: python manage.py collectstatic" -ForegroundColor White
Write-Host "9. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host ""
Write-Host "Your .env file has been backed up to .env.backup" -ForegroundColor Cyan

