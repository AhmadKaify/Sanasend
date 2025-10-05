#!/bin/bash
# WhatsApp Web API SaaS - Installation Script for Linux/Mac
# Run this script with: bash install.sh

echo "=================================="
echo "WhatsApp Web API SaaS - Installer"
echo "=================================="
echo ""

# Check Python installation
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python found: $PYTHON_VERSION"
else
    echo "✗ Python not found. Please install Python 3.10+"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "! Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment and install dependencies
echo ""
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create .env file from template
echo ""
echo "Setting up environment file..."
if [ -f ".env" ]; then
    echo "! .env file already exists"
else
    cp env.template .env
    echo "✓ .env file created from template"
    echo "! Please edit .env file with your database credentials"
fi

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "✓ Logs directory created"
fi

echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Make sure PostgreSQL is running"
echo "3. Make sure Redis is running"
echo "4. Run migrations: python manage.py makemigrations"
echo "5. Run migrations: python manage.py migrate"
echo "6. Create superuser: python manage.py createsuperuser"
echo "7. Run server: python manage.py runserver"
echo ""
echo "See SETUP.md for detailed instructions"

