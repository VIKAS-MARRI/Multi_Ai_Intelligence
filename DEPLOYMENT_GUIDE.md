# 🚀 Deployment Guide - Jarvis Multi-AI Voice Assistant

## Production Deployment Guide

This guide covers deploying the Jarvis Multi-AI Assistant to production environments.

---

## 📋 Pre-Deployment Checklist

- [ ] All API keys are valid and have sufficient quota
- [ ] Requirements.txt is updated
- [ ] Configuration is environment-specific
- [ ] Dependencies are tested
- [ ] Tests pass (if applicable)
- [ ] Security review completed
- [ ] Logging is configured
- [ ] Error handling is in place

---

## 1️⃣ Local Development Setup

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Create .env from example
cp .env.example .env

# Edit .env with your credentials
# Add all required API keys
```

### Testing

```bash
# Run the development server
python run.py

# Access http://localhost:5000
# Test all features:
# - Text queries
# - Voice input
# - Response fusion
# - Audio playback
```

---

## 2️⃣ Production Environment Setup

### Environment Variables

Create production `.env`:

```env
# Flask Production Settings
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=your-secure-random-key-here-min-32-chars

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true

# API Keys (use secure storage in production)
OPENAI_API_KEY=sk-prod-key-here
GEMINI_API_KEY=prod-key-here
DEEPSEEK_API_KEY=prod-key-here

# Voice
VOICE_ENGINE=edge-tts
VOICE_RATE=150
VOICE_VOLUME=1.0

# Logging
LOG_LEVEL=INFO
LOG_DIR=/var/log/jarvis

# API Timeouts
API_TIMEOUT=30
OPENAI_TIMEOUT=30
GEMINI_TIMEOUT=30
DEEPSEEK_TIMEOUT=30

# Fusion Engine
FUSION_ENABLE_DEDUPLICATION=true
FUSION_MAX_LENGTH=2000
```

### Generate Secure Secret Key

```python
import secrets
print(secrets.token_hex(32))
```

---

## 3️⃣ Gunicorn Setup (Recommended for Production)

### Install Gunicorn

```bash
pip install gunicorn
```

### Create Gunicorn Configuration

Create `gunicorn_config.py`:

```python
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2

# Logging
accesslog = "/var/log/jarvis/access.log"
errorlog = "/var/log/jarvis/error.log"
loglevel = "info"

# Process naming
proc_name = "jarvis-assistant"

# Server mechanics
daemon = False
pidfile = "/var/run/jarvis.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Application
max_requests = 1000
max_requests_jitter = 50
reload_extra_files = []
```

### Run with Gunicorn

```bash
gunicorn --config gunicorn_config.py run:app
```

---

## 4️⃣ Nginx Reverse Proxy Setup

### Install Nginx

```bash
# Ubuntu/Debian
sudo apt-get install nginx

# macOS
brew install nginx

# RHEL/CentOS
sudo yum install nginx
```

### Configure Nginx

Create `/etc/nginx/sites-available/jarvis`:

```nginx
upstream jarvis_app {
    server 127.0.0.1:5000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Configuration
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Certificates
    ssl_certificate /etc/ssl/certs/your_cert.crt;
    ssl_certificate_key /etc/ssl/private/your_key.key;

    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logging
    access_log /var/log/nginx/jarvis_access.log;
    error_log /var/log/nginx/jarvis_error.log;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
    gzip_min_length 1000;

    # Main proxy
    location / {
        proxy_pass http://jarvis_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Static files (optional)
    location /static/ {
        alias /path/to/jarvis/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/jarvis /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

---

## 5️⃣ Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 5000

# Environment
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  jarvis:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Build and Run

```bash
# Build image
docker build -t jarvis:latest .

# Run container
docker run -d \
  --name jarvis \
  -p 5000:5000 \
  --env-file .env \
  jarvis:latest

# Using docker-compose
docker-compose up -d
```

---

## 6️⃣ Systemd Service Setup (Linux)

### Create Service File

Create `/etc/systemd/system/jarvis.service`:

```ini
[Unit]
Description=Jarvis Multi-AI Voice Assistant
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/jarvis
Environment="PATH=/path/to/jarvis/venv/bin"
ExecStart=/path/to/jarvis/venv/bin/gunicorn \
    --config gunicorn_config.py \
    --chdir /path/to/jarvis \
    run:app

# Restart policy
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable jarvis
sudo systemctl start jarvis
sudo systemctl status jarvis
```

### Monitor Service

```bash
# View logs
sudo journalctl -u jarvis -f

# Check status
sudo systemctl status jarvis

# Restart
sudo systemctl restart jarvis
```

---

## 7️⃣ Cloud Platform Deployment

### AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB Application**
   ```bash
   eb init -p python-3.11 jarvis
   ```

3. **Create Application**
   ```bash
   eb create jarvis-env
   ```

4. **Deploy**
   ```bash
   eb deploy
   ```

### AWS EC2

1. Launch Ubuntu 22.04 instance
2. SSH into instance
3. Follow Linux installation steps
4. Use Nginx + Gunicorn setup

### Heroku

1. **Install Heroku CLI**
   ```bash
   brew tap heroku/brew && brew install heroku
   ```

2. **Create Procfile**
   ```
   web: gunicorn -w 4 run:app
   ```

3. **Deploy**
   ```bash
   heroku create jarvis-app
   heroku config:set FLASK_ENV=production
   heroku config:set OPENAI_API_KEY=...
   git push heroku main
   ```

### Google Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/jarvis

# Deploy
gcloud run deploy jarvis \
  --image gcr.io/PROJECT_ID/jarvis \
  --platform managed \
  --region us-central1 \
  --set-env-vars FLASK_ENV=production
```

---

## 8️⃣ Security Hardening

### Environment Variables Secure Storage

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name jarvis/prod/openai-key \
  --secret-string "sk-..."
```

**Azure Key Vault:**
```bash
az keyvault secret set \
  --vault-name jarvis-kv \
  --name openai-api-key \
  --value "sk-..."
```

**Google Cloud Secret Manager:**
```bash
gcloud secrets create openai-api-key \
  --data-file=- <<< "sk-..."
```

### SSL/TLS Certificate

**Let's Encrypt with Certbot:**
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
```

### Firewall Configuration

```bash
# Ubuntu UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

---

## 9️⃣ Monitoring & Logging

### Application Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/jarvis/app.log'),
        logging.StreamHandler()
    ]
)
```

### Monitoring Tools

- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **ELK Stack** - Logging
- **Datadog** - APM
- **New Relic** - Performance monitoring

### Health Check Endpoint

```bash
# Regular health checks
curl http://localhost:5000/health
```

---

## 🔟 Scaling Considerations

### Horizontal Scaling

1. Use load balancer (Nginx, HAProxy, AWS ELB)
2. Run multiple Gunicorn instances
3. Use shared session storage (Redis)
4. Cache responses (Redis/Memcached)

### Vertical Scaling

- Increase CPU/RAM
- Optimize worker processes
- Increase worker timeouts if needed

---

## 🔄 Deployment Checklist

- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Logging configured
- [ ] Backups enabled
- [ ] Monitoring enabled
- [ ] Health checks configured
- [ ] Load balancer configured
- [ ] DNS records updated
- [ ] Domain SSL configured
- [ ] Application tested
- [ ] Error alerts configured

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
lsof -i :5000
kill -9 <PID>
```

### Permission Denied
```bash
sudo chown -R www-data:www-data /path/to/jarvis
sudo chmod -R 755 /path/to/jarvis
```

### Memory Issues
```bash
# Reduce workers in gunicorn_config.py
workers = 2  # Reduce from default
```

### Timeout Issues
```python
# In .env or config.py
API_TIMEOUT=60
OPENAI_TIMEOUT=60
```

---

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test API connectivity
4. Review security groups/firewall rules
5. Check resource utilization

---

**Happy Deployment!** 🚀

For questions or issues, refer to documentation or contact support.
