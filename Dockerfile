# Multi-stage Dockerfile for WhatsApp Web API SaaS

# Stage 1: Build stage
FROM node:18-alpine AS node-builder

# Install Node.js dependencies for WhatsApp service
WORKDIR /app/whatsapp-service
COPY whatsapp-service/package*.json ./
RUN npm ci --only=production

# Stage 2: Python application
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        redis-tools \
        curl \
        build-essential \
        libpq-dev \
        gcc \
        && rm -rf /var/lib/apt/lists/*

# Create app user
RUN adduser --disabled-password --gecos '' appuser

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional production dependencies
RUN pip install --no-cache-dir \
    gunicorn \
    whitenoise \
    psycopg2-binary \
    django-redis \
    sentry-sdk

# Copy project
COPY . .

# Copy Node.js service from builder stage
COPY --from=node-builder /app/whatsapp-service ./whatsapp-service

# Create necessary directories
RUN mkdir -p /app/logs /app/staticfiles /app/media

# Set permissions
RUN chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
