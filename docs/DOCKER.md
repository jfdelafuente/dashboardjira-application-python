# Docker Setup Guide

This guide explains how to run the Support Team Dashboard using Docker and Docker Compose.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Common Commands](#common-commands)
- [Development Mode](#development-mode)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker 20.10 or higher
- Docker Compose 2.0 or higher
- 2GB RAM available for containers
- 5GB disk space

### Installation

**Linux/macOS:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose (if not included)
sudo apt-get install docker-compose-plugin
```

**Windows:**
- Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

### Verify Installation

```bash
docker --version
docker-compose --version
```

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-org/support-dashboard.git
cd support-dashboard
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.docker .env

# Edit .env with your settings (optional for development)
nano .env
```

**Important Variables:**
```env
POSTGRES_PASSWORD=your-strong-password
SECRET_KEY=your-random-secret-key
USE_MOCK_DATA=true  # Use mock data for testing
```

### 3. Start Services

Using Make (recommended):
```bash
make quick-start
```

Or manually:
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Wait for database to be ready
sleep 10

# Run migrations
docker-compose exec app flask db upgrade

# Seed with sample data
docker-compose exec app python scripts/seed_data.py --issues 50
```

### 4. Access Dashboard

Open your browser and navigate to:
- **Application**: http://localhost:5000
- **API Endpoints**:
  - http://localhost:5000/api/kpis
  - http://localhost:5000/api/charts/status
  - http://localhost:5000/api/issues

### 5. Check Status

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f app
```

---

## Configuration

### Environment Variables

Edit `.env` file to configure:

```env
# Flask
FLASK_ENV=production          # development | production
SECRET_KEY=random-secret-key  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# Database
POSTGRES_DB=support_dashboard
POSTGRES_USER=dashboard_user
POSTGRES_PASSWORD=strong-password-here

# Jira (optional)
JIRA_SERVER=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
USE_MOCK_DATA=false  # Set to false to use real Jira

# Redis
REDIS_PASSWORD=redis-password-here
```

### Ports

Default ports (can be changed in `docker-compose.yml`):
- **5000** - Flask application
- **5432** - PostgreSQL database
- **6379** - Redis cache
- **80** - Nginx (production profile only)

---

## Common Commands

### Using Make (Recommended)

```bash
# Start services
make up

# Stop services
make down

# View logs
make logs

# Run tests
make test

# Run migrations
make migrate

# Seed database
make seed

# Open shell in app container
make shell

# Open bash in app container
make bash

# See all available commands
make help
```

### Using Docker Compose Directly

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Execute command in app container
docker-compose exec app <command>

# Restart specific service
docker-compose restart app
```

---

## Development Mode

Development mode includes:
- **Hot reload** - Code changes automatically reload
- **Debug mode** - Detailed error messages
- **Source code mounting** - Edit files on host, reflected in container

### Start Development Environment

```bash
# Using Make
make up-dev

# Or using docker-compose
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Development Workflow

1. **Make code changes** on your host machine
2. **Changes auto-reload** in the container
3. **View logs** with `make logs`
4. **Run tests** with `make test`

### Running Tests in Development

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# With coverage
make test-coverage
```

---

## Production Deployment

### 1. Configure Production Settings

Update `.env`:
```env
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>
POSTGRES_PASSWORD=<strong-database-password>
REDIS_PASSWORD=<strong-redis-password>
USE_MOCK_DATA=false
```

### 2. Start with Nginx Reverse Proxy

```bash
# Start production stack with Nginx
docker-compose --profile production up -d

# Or using Make
make prod-up
```

### 3. SSL/TLS Setup

1. **Add SSL certificates** to `nginx/ssl/`:
   ```
   nginx/ssl/fullchain.pem
   nginx/ssl/privkey.pem
   ```

2. **Uncomment HTTPS section** in `nginx/conf.d/dashboard.conf`

3. **Restart Nginx**:
   ```bash
   docker-compose restart nginx
   ```

### 4. Production Checklist

- [ ] Strong `SECRET_KEY` set (32+ random characters)
- [ ] Strong database password set
- [ ] Strong Redis password set
- [ ] `USE_MOCK_DATA=false` if using real Jira
- [ ] SSL certificates installed
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] Backups automated (see below)
- [ ] Monitoring configured

---

## Database Management

### Migrations

```bash
# Create new migration after model changes
make migrate-create MSG="Add new column"

# Apply migrations
make migrate

# Rollback last migration
make migrate-downgrade
```

### Backups

```bash
# Manual backup
make backup-db

# Restore from backup
make restore-db FILE=backup_20251221_120000.sql
```

### Automated Backups (Production)

Add to crontab on host:
```cron
# Daily backup at 2 AM
0 2 * * * cd /path/to/project && make backup-db
```

---

## Monitoring

### View Resource Usage

```bash
# Show container stats (CPU, memory, network)
make stats

# Or directly
docker stats
```

### Health Checks

```bash
# Check service health
make health

# Manual health check
curl http://localhost:5000/api/kpis
```

### Logs

```bash
# All logs
make logs

# App logs only
make logs-app

# Follow logs in real-time
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

---

## Troubleshooting

### Container Won't Start

1. **Check logs**:
   ```bash
   docker-compose logs app
   ```

2. **Verify environment variables**:
   ```bash
   docker-compose config
   ```

3. **Check port conflicts**:
   ```bash
   netstat -tulpn | grep -E '5000|5432|6379'
   ```

### Database Connection Issues

1. **Verify database is running**:
   ```bash
   docker-compose ps db
   ```

2. **Check database logs**:
   ```bash
   docker-compose logs db
   ```

3. **Test connection**:
   ```bash
   make db-shell
   ```

### Permission Denied Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or run with sudo (not recommended)
sudo docker-compose up
```

### Out of Disk Space

```bash
# Remove unused images, containers, volumes
docker system prune -a

# Remove volumes (WARNING: deletes data)
make clean-volumes
```

### Port Already in Use

Edit `docker-compose.yml` to change ports:
```yaml
services:
  app:
    ports:
      - "8080:8000"  # Changed from 5000 to 8080
```

### Reset Everything

```bash
# Nuclear option - removes everything
make clean
make dev-setup
```

---

## Advanced Usage

### Custom Docker Compose File

Create `docker-compose.override.yml` for local customizations:
```yaml
version: '3.8'
services:
  app:
    environment:
      - DEBUG=true
    volumes:
      - ./custom-data:/data
```

### Multi-Stage Deployments

```bash
# Staging environment
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Scaling Services

```bash
# Run 3 instances of app service
docker-compose up -d --scale app=3
```

---

## Clean Up

### Stop and Remove Containers

```bash
# Stop services
make down

# Stop and remove volumes
make clean-volumes

# Remove everything (images, containers, volumes)
make clean
```

### Remove Specific Service Data

```bash
# Remove only database volume
docker volume rm support-dashboard_postgres_data

# Remove only Redis volume
docker volume rm support-dashboard_redis_data
```

---

## Performance Tuning

### Increase Worker Count

Edit `docker-compose.yml`:
```yaml
services:
  app:
    command: gunicorn --bind 0.0.0.0:8000 --workers 8 run:app
```

### Enable Redis Caching

1. Uncomment Redis configuration in `app/config.py`
2. Set `REDIS_URL` in `.env`
3. Restart services

---

## Security Best Practices

1. **Never commit `.env`** with real credentials
2. **Use secrets management** in production (Docker Swarm, Kubernetes)
3. **Run as non-root** (already configured in Dockerfile)
4. **Keep images updated**: `docker-compose pull`
5. **Scan for vulnerabilities**: `docker scan dashboard-app`
6. **Use SSL/TLS** in production
7. **Limit exposed ports** (only expose what's necessary)

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Docker Best Practices](https://flask.palletsprojects.com/en/latest/deploying/)
- [PostgreSQL Docker Official Image](https://hub.docker.com/_/postgres)

---

## Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting) section
- Review [GitHub Issues](https://github.com/your-org/support-dashboard/issues)
- Open a new issue with `docker` label

---

**Last Updated**: 2025-12-21
