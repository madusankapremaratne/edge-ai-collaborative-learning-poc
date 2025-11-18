# Production Deployment Guide

This guide covers deploying the Edge AI Collaborative Learning Platform to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start with Docker](#quick-start-with-docker)
3. [Manual Deployment](#manual-deployment)
4. [Configuration](#configuration)
5. [Database Setup](#database-setup)
6. [LLM Setup](#llm-setup)
7. [Security Hardening](#security-hardening)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **CPU**: 4+ cores (8+ recommended for LLM)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 50GB+ available
- **OS**: Ubuntu 20.04+, Debian 11+, or compatible Linux distribution

### Software Requirements

- Docker 24.0+ and Docker Compose 2.0+
- Python 3.11+ (for manual deployment)
- PostgreSQL 15+ (for manual deployment)
- Nginx (optional, for reverse proxy)

## Quick Start with Docker

### 1. Clone and Configure

```bash
git clone <repository-url>
cd edge-ai-collaborative-learning-poc
git checkout dev

# Copy and configure environment file
cp .env.example .env
nano .env  # Edit configuration
```

### 2. Configure Environment Variables

Edit `.env` and update critical settings:

```bash
# Security (REQUIRED for production)
APP_ENV=production
SECRET_KEY=<generate-strong-random-key>
JWT_SECRET_KEY=<generate-strong-random-key>

# Database
POSTGRES_USER=edgeai
POSTGRES_PASSWORD=<strong-database-password>
POSTGRES_DB=edge_ai_learning

# LLM Provider (choose one)
LLM_PROVIDER=ollama  # or openai, huggingface
OLLAMA_MODEL=qwen2.5-coder:latest

# LMS Integration (optional)
LMS_PROVIDER=canvas  # or moodle
LMS_API_URL=https://your-lms.example.com/api/v1
LMS_API_KEY=<your-lms-api-key>
```

### 3. Generate Secret Keys

```bash
# Generate secure random keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 5. Initialize Database

```bash
# Run database migrations
docker-compose exec api python database.py

# Create sample data (optional, for testing)
docker-compose exec api python scripts/init_db.py
```

### 6. Pull LLM Model (if using Ollama)

```bash
# Pull the model
docker-compose exec ollama ollama pull qwen2.5-coder:latest

# Verify model is available
docker-compose exec ollama ollama list
```

### 7. Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

### 8. Create Admin User

```bash
# Using the API
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@your-domain.com",
    "password": "change-this-password",
    "full_name": "System Administrator",
    "role": "admin"
  }'
```

## Manual Deployment

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
  postgresql-15 postgresql-client-15 nginx certbot \
  python3-certbot-nginx build-essential libpq-dev
```

### 2. Setup Python Environment

```bash
cd /opt
sudo git clone <repository-url> edge-ai-learning
cd edge-ai-learning
git checkout dev

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Setup PostgreSQL

```bash
# Create database user and database
sudo -u postgres psql << EOF
CREATE USER edgeai WITH PASSWORD 'your-password';
CREATE DATABASE edge_ai_learning OWNER edgeai;
GRANT ALL PRIVILEGES ON DATABASE edge_ai_learning TO edgeai;
EOF
```

### 4. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit configuration

# Set database URL
DATABASE_URL=postgresql://edgeai:your-password@localhost:5432/edge_ai_learning
```

### 5. Initialize Database

```bash
source venv/bin/activate
python database.py
python scripts/init_db.py  # Optional: sample data
```

### 6. Setup Systemd Services

Create `/etc/systemd/system/edge-ai-api.service`:

```ini
[Unit]
Description=Edge AI Learning Platform API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/edge-ai-learning
Environment="PATH=/opt/edge-ai-learning/venv/bin"
ExecStart=/opt/edge-ai-learning/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/edge-ai-streamlit.service`:

```ini
[Unit]
Description=Edge AI Learning Platform UI
After=network.target edge-ai-api.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/edge-ai-learning
Environment="PATH=/opt/edge-ai-learning/venv/bin"
ExecStart=/opt/edge-ai-learning/venv/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable edge-ai-api edge-ai-streamlit
sudo systemctl start edge-ai-api edge-ai-streamlit
sudo systemctl status edge-ai-api edge-ai-streamlit
```

### 7. Setup Nginx Reverse Proxy

Create `/etc/nginx/sites-available/edge-ai-learning`:

```nginx
upstream api_backend {
    server localhost:8000;
}

upstream streamlit_backend {
    server localhost:8501;
}

server {
    listen 80;
    server_name your-domain.com;

    # API
    location /api {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Streamlit UI
    location / {
        proxy_pass http://streamlit_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site and get SSL certificate:

```bash
sudo ln -s /etc/nginx/sites-available/edge-ai-learning /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## LLM Setup

### Option 1: Ollama (Local)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull recommended models
ollama pull qwen2.5-coder:latest  # Recommended for code/learning
ollama pull llama3.2:3b           # Lightweight alternative
ollama pull phi3:mini             # Efficient small model

# Verify
ollama list
```

### Option 2: OpenAI API

```bash
# Set environment variables
OPENAI_API_KEY=<your-api-key>
OPENAI_MODEL=gpt-4
LLM_PROVIDER=openai
```

### Option 3: Self-Hosted with vLLM

```bash
# Install vLLM
pip install vllm

# Run model server
vllm serve Qwen/Qwen2.5-Coder-7B-Instruct \
  --host 0.0.0.0 \
  --port 8080

# Configure
OPENAI_BASE_URL=http://localhost:8080/v1
OPENAI_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
```

## Security Hardening

### 1. Firewall Configuration

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. SSL/TLS Configuration

Use Let's Encrypt for free SSL certificates (see Nginx setup above).

### 3. Database Security

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Only allow local connections
# host  edge_ai_learning  edgeai  127.0.0.1/32  md5
```

### 4. Application Security

- Change all default passwords
- Use strong secret keys (minimum 32 characters)
- Enable audit logging: `ENABLE_AUDIT_LOG=true`
- Enable encryption: `ENABLE_ENCRYPTION=true`
- Set FERPA compliant mode: `FERPA_COMPLIANT_MODE=true`

### 5. Regular Updates

```bash
# Create update script
cat > /opt/edge-ai-learning/update.sh << 'EOF'
#!/bin/bash
cd /opt/edge-ai-learning
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart edge-ai-api edge-ai-streamlit
EOF

chmod +x /opt/edge-ai-learning/update.sh
```

## Monitoring

### 1. Application Logs

```bash
# View API logs
sudo journalctl -u edge-ai-api -f

# View Streamlit logs
sudo journalctl -u edge-ai-streamlit -f

# View application logs
tail -f /opt/edge-ai-learning/logs/edge_ai_learning.log
```

### 2. Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics  # If enabled
```

### 3. Database Monitoring

```bash
# Check database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='edge_ai_learning';"

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('edge_ai_learning'));"
```

## Backup and Recovery

### Database Backup

```bash
# Create backup script
cat > /opt/edge-ai-learning/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/opt/backups/edge-ai-learning
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -U edgeai edge_ai_learning | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /opt/edge-ai-learning/backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /opt/edge-ai-learning/backup.sh" | sudo crontab -
```

### Database Restore

```bash
# Restore from backup
gunzip -c /opt/backups/edge-ai-learning/db_backup_YYYYMMDD_HHMMSS.sql.gz | \
  sudo -u postgres psql edge_ai_learning
```

## Troubleshooting

### API Won't Start

```bash
# Check logs
sudo journalctl -u edge-ai-api -n 50

# Check port availability
sudo netstat -tulpn | grep 8000

# Test manually
cd /opt/edge-ai-learning
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Database Connection Issues

```bash
# Test database connection
psql -U edgeai -d edge_ai_learning -h localhost

# Check PostgreSQL status
sudo systemctl status postgresql
```

### LLM Not Responding

```bash
# Check Ollama status
systemctl status ollama
ollama list

# Test LLM directly
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder:latest",
  "prompt": "Hello, test message"
}'
```

## Performance Tuning

### PostgreSQL Optimization

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/15/main/postgresql.conf

# Recommended settings (adjust based on RAM)
# shared_buffers = 256MB
# effective_cache_size = 1GB
# maintenance_work_mem = 64MB
# checkpoint_completion_target = 0.9
# wal_buffers = 16MB
# default_statistics_target = 100
# random_page_cost = 1.1
# effective_io_concurrency = 200
# work_mem = 4MB
# min_wal_size = 1GB
# max_wal_size = 4GB
# max_worker_processes = 4
# max_parallel_workers_per_gather = 2
# max_parallel_workers = 4

sudo systemctl restart postgresql
```

### Application Optimization

- Enable Redis caching: `ENABLE_REDIS=true`
- Increase API workers (in systemd service)
- Use connection pooling for database
- Monitor slow queries in logs

## Support

For issues or questions:
- Check logs in `/opt/edge-ai-learning/logs/`
- Review documentation in `/opt/edge-ai-learning/documentation/`
- Check GitHub issues

## License

See LICENSE file for details.
