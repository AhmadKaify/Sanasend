# SanaSend SaaS - Installation Script for Windows
# Run this script with: .\install.ps1

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "SanaSend SaaS - Installer" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = py --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.10+ from python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "! Virtual environment already exists" -ForegroundColor Yellow
} else {
    py -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Create .env file from template
Write-Host ""
Write-Host "Setting up environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "! .env file already exists" -ForegroundColor Yellow
} else {
    Copy-Item "env.template" ".env"
    Write-Host "✓ .env file created from template" -ForegroundColor Green
    Write-Host "! Please edit .env file with your database credentials" -ForegroundColor Yellow
}

# Create logs directory
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "✓ Logs directory created" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Make sure PostgreSQL is running" -ForegroundColor White
Write-Host "3. Make sure Redis is running" -ForegroundColor White
Write-Host "4. Run migrations: py manage.py makemigrations" -ForegroundColor White
Write-Host "5. Run migrations: py manage.py migrate" -ForegroundColor White
Write-Host "6. Create superuser: py manage.py createsuperuser" -ForegroundColor White
Write-Host "7. Run server: py manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "See SETUP.md for detailed instructions" -ForegroundColor Cyan

