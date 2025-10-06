# Fix Installation Error - DB_PASSWORD Not Found

## The Problem

The installation script created `.env.production` file but Django couldn't read it because `python-decouple` looks for `.env` by default.

## Immediate Fix (Continue Your Installation)

Run these commands on your server:

```bash
# 1. Navigate to project directory
cd /home/sanasend/public_html

# 2. Activate virtual environment
source venv/bin/activate

# 3. Load environment variables from .env.production
export DJANGO_SETTINGS_MODULE=config.settings.production
export $(grep -v '^#' .env.production | xargs)

# 4. Run migrations
python manage.py migrate --noinput

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Create superuser
python manage.py createsuperuser

# 7. Install Node.js dependencies
cd whatsapp-service
npm install --production

# 8. Start services
sudo systemctl start whatsapp-django
sudo systemctl start whatsapp-node

# 9. Check service status
sudo systemctl status whatsapp-django
sudo systemctl status whatsapp-node
```

## Verify Installation

After running the above commands, check that services are running:

```bash
# Check Django service
sudo systemctl status whatsapp-django

# Check Node.js service
sudo systemctl status whatsapp-node

# View logs if needed
sudo journalctl -u whatsapp-django -n 50
sudo journalctl -u whatsapp-node -n 50
```

## Next Steps

1. **Configure Nginx/Apache** - See `AUTOMATED_INSTALL_README.md` Step 5
2. **Setup SSL Certificate** - See `AUTOMATED_INSTALL_README.md` Step 6
3. **Test Installation** - Visit your domain

## Future Installations

The installation script has been updated to fix this issue. If you run it again, this error won't occur.

## Alternative: Use .env Instead

If you prefer, you can use `.env` instead of `.env.production`:

```bash
cd /home/sanasend/public_html
cp .env.production .env
```

Then Django will automatically read from `.env` without needing to export variables.

