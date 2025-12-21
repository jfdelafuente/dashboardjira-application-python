# Deployment Guide

This guide explains how to deploy the Support Team Dashboard to a production environment using Gunicorn + nginx + PostgreSQL.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Server Setup](#server-setup)
- [PostgreSQL Setup](#postgresql-setup)
- [Application Deployment](#application-deployment)
- [Nginx Configuration](#nginx-configuration)
- [Systemd Service](#systemd-service)
- [SSL/TLS Setup](#ssltls-setup)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Prerequisites

- Ubuntu 20.04/22.04 LTS server (or similar Linux distribution)
- Root or sudo access
- Domain name pointing to your server (for SSL)
- PostgreSQL 12+
- Python 3.10+

---

## Server Setup

### 1. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Required Packages

```bash
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib
```

### 3. Create Application User

```bash
sudo useradd -m -s /bin/bash dashboard
sudo su - dashboard
```

---

## PostgreSQL Setup

### 1. Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE support_dashboard;
CREATE USER dashboard_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE support_dashboard TO dashboard_user;
\q
```

### 2. Configure PostgreSQL Authentication

Edit `/etc/postgresql/14/main/pg_hba.conf` and add:

```
# TYPE  DATABASE            USER            ADDRESS         METHOD
local   support_dashboard   dashboard_user                  md5
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

---

## Application Deployment

### 1. Clone Repository

```bash
# As dashboard user
cd /home/dashboard
git clone https://github.com/your-org/support-dashboard.git
cd support-dashboard
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements/base.txt
pip install gunicorn psycopg2-binary
```

### 4. Configure Environment Variables

Create `.env` file:

```bash
cp .env.example .env
nano .env
```

Set production values:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-very-long-random-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://dashboard_user:your-secure-password@localhost/support_dashboard

# Jira Configuration
JIRA_SERVER=https://your-company.atlassian.net
JIRA_EMAIL=service-account@your-company.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT_KEY=SUP
USE_MOCK_DATA=false

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### 5. Initialize Database

```bash
# Activate virtual environment
source venv/bin/activate

# Initialize migrations
flask db init  # Only if migrations/ doesn't exist

# Run migrations
flask db upgrade

# Seed initial data (optional)
python scripts/seed_data.py --issues 100
```

### 6. Test Application

```bash
# Run with Gunicorn
gunicorn --bind 127.0.0.1:8000 --workers 4 run:app
```

Test in another terminal:

```bash
curl http://127.0.0.1:8000
```

---

## Nginx Configuration

### 1. Create Nginx Site Configuration

Create `/etc/nginx/sites-available/dashboard`:

```nginx
server {
    listen 80;
    server_name dashboard.your-company.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dashboard.your-company.com;

    # SSL Configuration (we'll set this up later)
    ssl_certificate /etc/letsencrypt/live/dashboard.your-company.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dashboard.your-company.com/privkey.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/dashboard_access.log;
    error_log /var/log/nginx/dashboard_error.log;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if serving directly via nginx for better performance)
    location /static {
        alias /home/dashboard/support-dashboard/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Deny access to .env and other sensitive files
    location ~ /\. {
        deny all;
    }
}
```

### 2. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Systemd Service

### 1. Create Systemd Service File

Create `/etc/systemd/system/dashboard.service`:

```ini
[Unit]
Description=Support Team Dashboard (Gunicorn)
After=network.target postgresql.service

[Service]
Type=notify
User=dashboard
Group=dashboard
WorkingDirectory=/home/dashboard/support-dashboard
Environment="PATH=/home/dashboard/support-dashboard/venv/bin"
EnvironmentFile=/home/dashboard/support-dashboard/.env

ExecStart=/home/dashboard/support-dashboard/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile /var/log/dashboard/access.log \
    --error-logfile /var/log/dashboard/error.log \
    --log-level info \
    run:app

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Create Log Directory

```bash
sudo mkdir -p /var/log/dashboard
sudo chown dashboard:dashboard /var/log/dashboard
```

### 3. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable dashboard
sudo systemctl start dashboard
sudo systemctl status dashboard
```

---

## SSL/TLS Setup

### 1. Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate

```bash
# This will automatically configure nginx
sudo certbot --nginx -d dashboard.your-company.com

# Test renewal
sudo certbot renew --dry-run
```

---

## Monitoring and Maintenance

### Check Application Status

```bash
sudo systemctl status dashboard
sudo journalctl -u dashboard -f
```

### Check Nginx Status

```bash
sudo systemctl status nginx
sudo tail -f /var/log/nginx/dashboard_error.log
```

### Database Backup

```bash
# Manual backup
pg_dump -U dashboard_user support_dashboard > backup_$(date +%Y%m%d).sql

# Automated daily backup (add to cron)
sudo crontab -e
# Add: 0 2 * * * pg_dump -U dashboard_user support_dashboard > /backups/dashboard_$(date +\%Y\%m\%d).sql
```

### Application Updates

```bash
# As dashboard user
cd /home/dashboard/support-dashboard
git pull origin main
source venv/bin/activate
pip install -r requirements/base.txt
flask db upgrade
sudo systemctl restart dashboard
```

### Performance Monitoring

```bash
# Monitor resource usage
htop

# Check Gunicorn workers
ps aux | grep gunicorn

# Monitor database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='support_dashboard';"
```

---

## Troubleshooting

### Application Won't Start

1. Check logs: `sudo journalctl -u dashboard -n 100`
2. Verify database connection: `psql -U dashboard_user -d support_dashboard -h localhost`
3. Check environment variables: `sudo systemctl show dashboard | grep Environment`

### 502 Bad Gateway

1. Verify Gunicorn is running: `sudo systemctl status dashboard`
2. Check nginx configuration: `sudo nginx -t`
3. Verify proxy_pass port matches Gunicorn bind address

### High Memory Usage

1. Reduce Gunicorn workers
2. Monitor with: `ps aux --sort=-%mem | head`
3. Consider using gunicorn worker class: `gevent` or `eventlet`

---

## Security Checklist

- [ ] Strong SECRET_KEY set (32+ random characters)
- [ ] Database password is strong and unique
- [ ] SSL/TLS certificate installed and auto-renewing
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] SSH key authentication enabled (password auth disabled)
- [ ] Application runs as non-root user
- [ ] Sensitive files (.env) not in web root
- [ ] Security headers configured in nginx
- [ ] Regular system updates scheduled
- [ ] Database backups automated
- [ ] Jira API token rotated regularly

---

## Performance Optimization

### Database Indexing

```sql
-- Add indexes for common queries
CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_priority ON issues(priority);
CREATE INDEX idx_issues_assignee_id ON issues(assignee_id);
CREATE INDEX idx_issues_created_at ON issues(created_at);
CREATE INDEX idx_issues_sla_deadline ON issues(sla_deadline);
```

### Gunicorn Configuration

```bash
# For CPU-bound tasks
--workers $(nproc)  # One worker per CPU core

# For I/O-bound tasks (database queries)
--workers $((2 * $(nproc) + 1))

# Use worker timeout for slow requests
--timeout 120
```

### Redis Caching (Optional)

For caching Jira API calls:

```bash
sudo apt install redis-server
pip install redis flask-caching
```

---

## Additional Resources

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/latest/deploying/)

---

## Support

For issues or questions, contact the DevOps team or open an issue in the repository.

**Last Updated**: 2025-12-21
