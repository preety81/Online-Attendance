# Deployment Guide - Online Attendance App

Production-ready deployment instructions for multiple platforms.

---

## Table of Contents

1. [Quick Start (Streamlit Cloud)](#quick-start-streamlit-cloud)
2. [Docker Deployment](#docker-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Azure Deployment](#azure-deployment)
5. [GCP Deployment](#gcp-deployment)
6. [Self-Hosted VPS](#self-hosted-vps)
7. [Post-Deployment Checklist](#post-deployment-checklist)

---

## Quick Start: Streamlit Cloud

**Pros**: Free tier, easiest setup, auto-scaling  
**Cons**: Limited to Streamlit platform, slower for CPU-heavy tasks

### 1. Prepare Repository

```bash
# Ensure secrets.toml is in .gitignore (NEVER commit!)
echo ".streamlit/secrets.toml" >> .gitignore
echo ".env" >> .gitignore
echo ".logs/" >> .gitignore

# Create secrets.toml.example for reference
cat > .streamlit/secrets.toml.example << 'EOF'
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key-here"
EOF
```

### 2. Create Streamlit Secrets

In Streamlit Cloud dashboard:
1. Go to your app > Settings > Secrets
2. Copy and paste your `.streamlit/secrets.toml` content:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Deploy

```bash
# Push to GitHub (public or private repo)
git push origin main

# In Streamlit Cloud:
# - New app → GitHub repo → Branch: main → File: app.py
# - Wait for deployment (~2-3 minutes)
```

### 4. Verify

Open `https://your-username-attendanceapp-[hash].streamlit.app`

---

## Docker Deployment

**Pros**: Reproducible, works anywhere, easy scaling  
**Cons**: Requires Docker knowledge

### 1. Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create logs directory
RUN mkdir -p .logs

# Set environment
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app.py"]
```

### 2. Create docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  attendance-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - APP_DOMAIN=${APP_DOMAIN:-http://localhost:8501}
      - LOG_LEVEL=INFO
      - DEBUG=false
    volumes:
      - ./shared_data:/app/shared_data
      - ./logs:/app/.logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - attendance-app
```

### 3. Build & Run

```bash
# Build image
docker build -t attendance-app:latest .

# Run with environment variables
docker run -p 8501:8501 \
  -e SUPABASE_URL="https://your-project.supabase.co" \
  -e SUPABASE_ANON_KEY="your-key" \
  -e APP_ENV="production" \
  attendance-app:latest

# Or use docker-compose
docker-compose up -d
```

### 4. Verify

```bash
# Check logs
docker logs <container-id>

# Health check
curl http://localhost:8501/_stcore/health
```

---

## AWS Deployment

### Option 1: AWS App Runner (Easiest)

```bash
# 1. Push Docker image to ECR
aws ecr create-repository --repository-name attendance-app --region us-east-1

docker tag attendance-app:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/attendance-app:latest
aws ecr get-login-password | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/attendance-app:latest

# 2. Create App Runner service
aws apprunner create-service \
  --service-name attendance-app \
  --source-configuration ImageRepository="{RepositoryUrl=YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/attendance-app,ImageIdentifier=latest,ImageRepositoryType=ECR}",AutoDeploymentsEnabled=true \
  --instance-configuration Cpu=1 Vcpu,Memory=2Gb \
  --region us-east-1

# 3. Set environment variables in AWS Console
#    App Runner > attendance-app > Configuration > Environment variables
```

### Option 2: ECS + Load Balancer

See AWS ECS documentation for container orchestration.

---

## Azure Deployment

### 1. Create Container Instance

```bash
# Login to Azure
az login

# Create resource group
az group create --name attendance-app --location eastus

# Create ACR (Azure Container Registry)
az acr create --resource-group attendance-app \
  --name attendanceacr --sku Basic

# Push image
az acr build --registry attendanceacr --image attendance-app:latest .

# Create Container Instance
az container create \
  --resource-group attendance-app \
  --name attendance-app \
  --image attendanceacr.azurecr.io/attendance-app:latest \
  --ports 8501 \
  --environment-variables \
    SUPABASE_URL=https://your-project.supabase.co \
    SUPABASE_ANON_KEY=your-key \
  --registry-login-server attendanceacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password>
```

---

## GCP Deployment

### 1. Cloud Run (Simplest)

```bash
# Login
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build & push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/attendance-app

# Deploy to Cloud Run
gcloud run deploy attendance-app \
  --image gcr.io/YOUR_PROJECT_ID/attendance-app \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars SUPABASE_URL=https://your-project.supabase.co,SUPABASE_ANON_KEY=your-key \
  --allow-unauthenticated

# Get URL
gcloud run services describe attendance-app --region us-central1
```

---

## Self-Hosted VPS

### 1. Server Setup (Ubuntu 22.04)

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
sudo mkdir -p /opt/attendance-app
sudo chown $USER:$USER /opt/attendance-app
cd /opt/attendance-app
```

### 2. Deploy App

```bash
# Clone repo
git clone https://github.com/your-repo/online-attendance.git .

# Create .env file
cat > .env << 'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-key
APP_ENV=production
DEBUG=False
LOG_LEVEL=WARNING
EOF

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### 3. Configure Nginx (Reverse Proxy + SSL)

```nginx
# /etc/nginx/sites-available/attendance-app
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/attendance-app /etc/nginx/sites-enabled/

# Get SSL cert (Let's Encrypt)
sudo certbot certonly --nginx -d your-domain.com

# Test & reload
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Enable Auto-Updates

```bash
# Create systemd service
sudo tee /etc/systemd/system/attendance-app.service << 'EOF'
[Unit]
Description=Attendance App Docker Compose
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/attendance-app
ExecStart=/usr/local/bin/docker-compose up -d

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable attendance-app
sudo systemctl start attendance-app

# Monitor
sudo journalctl -u attendance-app -f
```

---

## Post-Deployment Checklist

### Security
- [ ] HTTPS enforced (redirect HTTP → HTTPS)
- [ ] Security headers set (X-Frame-Options, CSP, etc.)
- [ ] Database backups automated (daily)
- [ ] Secrets stored in environment (not in code)
- [ ] Rate limiting configured
- [ ] Database RLS policies tested
- [ ] CORS properly configured

### Monitoring
- [ ] Error tracking enabled (Sentry)
- [ ] Uptime monitoring enabled (UptimeRobot)
- [ ] Logs aggregated (ELK, Datadog, etc.)
- [ ] Alerts configured for errors/downtime
- [ ] Performance metrics tracked
- [ ] Database query times monitored

### Performance
- [ ] Cache enabled (Redis for embeddings)
- [ ] CDN configured for static assets
- [ ] Database indexed appropriately
- [ ] Compression enabled (gzip)
- [ ] Load balancer configured (if needed)

### Maintenance
- [ ] Backup schedule documented
- [ ] Disaster recovery plan in place
- [ ] Update schedule for dependencies
- [ ] Security scanning enabled (Dependabot)
- [ ] Documentation up-to-date

### Testing
- [ ] Smoke tests passing
- [ ] End-to-end tests passing
- [ ] Load testing completed (expected throughput verified)
- [ ] Failover tested

---

## Health Check Endpoint

```python
# Add to app.py:
import streamlit as st

@st.cache_resource
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "environment": os.getenv("APP_ENV", "development")
    }

# Access via: https://your-app.com/_stcore/health
```

---

## Troubleshooting

### App won't start

```bash
# Check logs
docker logs <container-id>

# Verify environment variables
docker exec <container-id> env | grep SUPABASE

# Rebuild image
docker-compose build --no-cache
```

### High CPU/Memory

```bash
# Profile app
streamlit run app.py --logger.level=debug

# Check for memory leaks
# See: src/constants.py MAX_UPLOAD_SIZE_MB

# Reduce concurrent users
# Configure Streamlit: maxSessionsPerUser
```

### Database connection errors

```bash
# Verify Supabase connectivity
curl https://your-project.supabase.co/rest/v1/

# Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'teachers';

# Test from container
docker exec <container-id> python -c "
from src.database.config import supabase
print(supabase.table('teachers').select('*').limit(1).execute())
"
```

---

## References

- [Streamlit Cloud Deployment](https://docs.streamlit.io/cloud/general-experience)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [AWS App Runner](https://docs.aws.amazon.com/apprunner/)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [Nginx Best Practices](https://nginx.org/en/docs/)
