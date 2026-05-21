# Deployment Guide - EEG Emotion Recognition System

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- Python 3.10 or higher
- Node.js 16+ (for frontend build tools)
- PostgreSQL 13+ (for production)
- 8GB RAM minimum
- 20GB disk space

### Required Software
- Git
- Docker & Docker Compose (for containerized deployment)
- pip (Python package manager)
- virtualenv or venv

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd eeg-emotion-recognition
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Set DEBUG=True for development
```

### 5. Run Database Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Access the application at: `http://localhost:8000`

---

## Docker Deployment

### 1. Build Docker Image
```bash
docker build -t eeg-emotion-recognition .
```

### 2. Run with Docker Compose
```bash
docker-compose up -d
```

### 3. Run Migrations in Container
```bash
docker-compose exec web python manage.py migrate
```

### 4. Create Superuser in Container
```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. View Logs
```bash
docker-compose logs -f web
```

### 6. Stop Services
```bash
docker-compose down
```

---

## Production Deployment

### Option 1: Traditional Server Deployment

#### 1. Server Setup (Ubuntu 20.04/22.04)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib -y
```

#### 2. PostgreSQL Setup
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE eeg_emotion_db;
CREATE USER eeg_user WITH PASSWORD 'your_secure_password';
ALTER ROLE eeg_user SET client_encoding TO 'utf8';
ALTER ROLE eeg_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE eeg_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE eeg_emotion_db TO eeg_user;
\q
```

#### 3. Application Setup
```bash
# Clone repository
cd /var/www
sudo git clone <repository-url> eeg-emotion-recognition
cd eeg-emotion-recognition

# Create virtual environment
sudo python3 -m venv venv
sudo chown -R $USER:$USER venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

#### 4. Configure Environment
```bash
# Create production .env file
sudo nano .env

# Add production settings:
DEBUG=False
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=postgresql://eeg_user:your_secure_password@localhost/eeg_emotion_db
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

#### 5. Run Migrations
```bash
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 6. Configure Gunicorn
```bash
# Create gunicorn service file
sudo nano /etc/systemd/system/eeg-emotion.service
```

Add the following content:
```ini
[Unit]
Description=EEG Emotion Recognition Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/eeg-emotion-recognition/backend
Environment="PATH=/var/www/eeg-emotion-recognition/venv/bin"
ExecStart=/var/www/eeg-emotion-recognition/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/eeg-emotion-recognition/eeg-emotion.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 7. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/eeg-emotion
```

Add the following content:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/eeg-emotion-recognition/backend;
    }
    
    location /media/ {
        root /var/www/eeg-emotion-recognition/backend;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/eeg-emotion-recognition/eeg-emotion.sock;
    }
}
```

#### 8. Enable and Start Services
```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/eeg-emotion /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# Enable and start Gunicorn
sudo systemctl start eeg-emotion
sudo systemctl enable eeg-emotion
```

#### 9. Setup SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Option 2: Cloud Platform Deployment

#### AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p python-3.10 eeg-emotion-recognition

# Create environment
eb create eeg-emotion-env

# Deploy
eb deploy
```

#### Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn config.wsgi --log-file -" > Procfile

# Create Heroku app
heroku create eeg-emotion-recognition

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
```

---

## Environment Variables

### Required Variables
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Media and Static Files
MEDIA_ROOT=/path/to/media
STATIC_ROOT=/path/to/static

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## Database Setup

### SQLite (Development)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### PostgreSQL (Production)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'eeg_emotion_db',
        'USER': 'eeg_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Backup Database
```bash
# PostgreSQL backup
pg_dump -U eeg_user eeg_emotion_db > backup.sql

# Restore
psql -U eeg_user eeg_emotion_db < backup.sql
```

---

## Troubleshooting

### Common Issues

#### 1. Static Files Not Loading
```bash
python manage.py collectstatic --noinput
sudo systemctl restart eeg-emotion
sudo systemctl restart nginx
```

#### 2. Database Connection Error
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in .env file
- Check DATABASE_URL format

#### 3. Permission Errors
```bash
sudo chown -R www-data:www-data /var/www/eeg-emotion-recognition
sudo chmod -R 755 /var/www/eeg-emotion-recognition
```

#### 4. Gunicorn Not Starting
```bash
# Check logs
sudo journalctl -u eeg-emotion -n 50

# Restart service
sudo systemctl restart eeg-emotion
```

#### 5. Nginx 502 Bad Gateway
- Check Gunicorn is running
- Verify socket file exists
- Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### Performance Optimization

#### 1. Enable Caching
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

#### 2. Configure Gunicorn Workers
```bash
# Calculate workers: (2 x CPU cores) + 1
--workers 5
```

#### 3. Enable Gzip Compression in Nginx
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
```

---

## Monitoring and Maintenance

### Log Files
- Application logs: `/var/log/eeg-emotion/`
- Nginx logs: `/var/log/nginx/`
- Gunicorn logs: `sudo journalctl -u eeg-emotion`

### Regular Maintenance
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations
python manage.py migrate

# Clear old sessions
python manage.py clearsessions

# Backup database
pg_dump -U eeg_user eeg_emotion_db > backup_$(date +%Y%m%d).sql
```

---

## Security Checklist

- [ ] Set DEBUG=False in production
- [ ] Use strong SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for secrets

---

## Support

For issues and questions:
- Check logs first
- Review this documentation
- Contact system administrator
- Submit issue on GitHub

---

**Last Updated:** 2024
**Version:** 1.0.0