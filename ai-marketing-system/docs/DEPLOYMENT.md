# Deployment Guide

This guide covers deploying your AI Marketing Automation System to production.

## Deployment Options

### Option 1: DigitalOcean App Platform (Recommended - Easiest)

**Cost**: ~$12-20/month

**Steps:**

1. **Prepare Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create App on DigitalOcean**
   - Go to DigitalOcean App Platform
   - Connect your GitHub/GitLab repository
   - Configure two components:
     - Backend (Python): Port 8000
     - Frontend (Node): Port 3000

3. **Set Environment Variables**
   - In App Platform dashboard
   - Add all variables from `.env`
   - Use DigitalOcean managed database for PostgreSQL

4. **Deploy**
   - Click "Deploy"
   - Wait 5-10 minutes
   - Your app is live!

### Option 2: Railway (Modern & Simple)

**Cost**: $5-15/month

**Steps:**

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Initialize Project**
   ```bash
   railway init
   railway link
   ```

3. **Deploy Backend**
   ```bash
   cd backend
   railway up
   ```

4. **Deploy Frontend**
   ```bash
   cd frontend
   railway up
   ```

5. **Set Environment Variables**
   ```bash
   railway variables set OPENROUTER_API_KEY=your-key
   # Set all other variables
   ```

### Option 3: AWS (Most Flexible)

**Cost**: ~$20-50/month

**Backend on AWS Elastic Beanstalk:**

1. **Install AWS CLI & EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**
   ```bash
   cd backend
   eb init -p python-3.9 ai-marketing-backend
   eb create ai-marketing-env
   ```

3. **Configure Environment**
   ```bash
   eb setenv OPENROUTER_API_KEY=your-key
   # Set all environment variables
   ```

**Frontend on AWS Amplify:**

1. Connect repository to AWS Amplify
2. Configure build settings:
   ```yaml
   version: 1
   frontend:
     phases:
       build:
         commands:
           - cd frontend
           - npm install
           - npm run build
     artifacts:
       baseDirectory: frontend/dist
       files:
         - '**/*'
   ```

### Option 4: Heroku (Classic Choice)

**Cost**: ~$14-30/month

**Backend:**
```bash
cd backend
heroku create ai-marketing-backend
heroku addons:create heroku-postgresql:mini
git push heroku main
heroku config:set OPENROUTER_API_KEY=your-key
```

**Frontend:**
```bash
cd frontend
heroku create ai-marketing-frontend
heroku buildpacks:set heroku/nodejs
git push heroku main
```

### Option 5: VPS (Most Control)

**Providers**: DigitalOcean Droplet, Linode, Vultr
**Cost**: $6-12/month

**Steps:**

1. **Setup Server**
   ```bash
   # SSH into server
   ssh root@your-server-ip

   # Update system
   apt update && apt upgrade -y

   # Install dependencies
   apt install python3-pip python3-venv nginx nodejs npm -y
   ```

2. **Deploy Backend**
   ```bash
   cd /var/www
   git clone your-repo ai-marketing
   cd ai-marketing/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn

   # Create systemd service
   nano /etc/systemd/system/ai-marketing.service
   ```

   Service file content:
   ```ini
   [Unit]
   Description=AI Marketing Backend
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/ai-marketing/backend
   Environment="PATH=/var/www/ai-marketing/backend/venv/bin"
   ExecStart=/var/www/ai-marketing/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   systemctl enable ai-marketing
   systemctl start ai-marketing
   ```

3. **Deploy Frontend**
   ```bash
   cd /var/www/ai-marketing/frontend
   npm install
   npm run build
   ```

4. **Configure Nginx**
   ```bash
   nano /etc/nginx/sites-available/ai-marketing
   ```

   Nginx config:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       # Frontend
       location / {
           root /var/www/ai-marketing/frontend/dist;
           try_files $uri $uri/ /index.html;
       }

       # Backend API
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   ```bash
   ln -s /etc/nginx/sites-available/ai-marketing /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

5. **Setup SSL with Let's Encrypt**
   ```bash
   apt install certbot python3-certbot-nginx -y
   certbot --nginx -d yourdomain.com
   ```

## Database Configuration

### Production Database

**PostgreSQL (Recommended):**

Update `.env`:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

**Managed Options:**
- DigitalOcean Managed Database: $15/month
- AWS RDS: $15-30/month
- Heroku Postgres: $9/month
- Railway Postgres: Included

### Database Migration

```bash
# Backup SQLite data
python scripts/export_data.py

# Switch to PostgreSQL in .env
# Import data
python scripts/import_data.py
```

## Environment Variables for Production

**Required:**
```env
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=<production-database-url>
OPENROUTER_API_KEY=<your-api-key>

SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
SMTP_FROM_EMAIL=noreply@yourdomain.com

FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com
CORS_ORIGINS=["https://yourdomain.com"]
```

## Security Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Use HTTPS (SSL certificate)
- [ ] Set secure CORS_ORIGINS
- [ ] Use managed database with backups
- [ ] Enable firewall (only ports 80, 443, 22)
- [ ] Use strong database passwords
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Regular backups
- [ ] Keep dependencies updated

## Performance Optimization

### Backend

1. **Use Production Server**
   ```bash
   # Instead of uvicorn directly, use gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

2. **Enable Gzip**
   ```python
   # In main.py
   from fastapi.middleware.gzip import GZipMiddleware
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

3. **Database Connection Pooling**
   Already configured in SQLAlchemy

### Frontend

1. **Build for Production**
   ```bash
   npm run build
   ```

2. **Enable Caching**
   Configure in Nginx or CDN

3. **Use CDN**
   CloudFlare (free), AWS CloudFront

## Monitoring

### Application Monitoring

**Sentry (Error Tracking):**
```bash
pip install sentry-sdk[fastapi]
```

```python
# In main.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### Uptime Monitoring

- UptimeRobot (free)
- Pingdom
- AWS CloudWatch

### Analytics

- Google Analytics for frontend
- Custom analytics via API

## Backup Strategy

### Automated Backups

**Database:**
```bash
# Daily backup script
#!/bin/bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
# Upload to S3 or backup service
```

**Files:**
```bash
# Backup uploads directory
tar -czf uploads_backup.tar.gz data/uploads/
```

### Backup Services

- AWS S3
- DigitalOcean Spaces
- Backblaze B2

## Scaling

### Horizontal Scaling

1. **Load Balancer**
   - AWS ALB
   - DigitalOcean Load Balancer
   - Nginx

2. **Multiple Backend Instances**
   ```bash
   # Run 4 workers per instance
   gunicorn -w 4 main:app
   ```

3. **Database Read Replicas**
   For high traffic

### Caching

**Redis for Session & Cache:**
```bash
pip install redis
```

```python
# Configure Redis caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
```

## Cost Optimization

### Development vs Production

**Development:**
- Free tier options
- SQLite database
- Single server

**Production (Small):** $20-40/month
- DigitalOcean Droplet ($6)
- Managed Database ($15)
- OpenRouter API ($10-20)

**Production (Medium):** $50-100/month
- App Platform/Railway ($20)
- Managed Database ($30)
- CDN ($5)
- OpenRouter API ($20-50)

**Production (Large):** $200+/month
- Multiple servers
- Load balancer
- Redis caching
- Higher API usage

## Maintenance

### Regular Tasks

**Weekly:**
- Review error logs
- Check API usage/costs
- Monitor performance

**Monthly:**
- Update dependencies
- Review security patches
- Backup verification
- Performance optimization

**Quarterly:**
- Security audit
- Database optimization
- Cost review
- Feature updates

### Update Commands

```bash
# Backend dependencies
pip install --upgrade -r requirements.txt

# Frontend dependencies
npm update

# Security audit
npm audit
pip-audit
```

## Troubleshooting Production

### Common Issues

**High Memory Usage:**
```bash
# Reduce worker count
gunicorn -w 2 main:app
```

**Slow API Responses:**
- Enable database indexing
- Add caching layer
- Optimize queries

**Email Delivery Issues:**
- Check SMTP credentials
- Verify SPF/DKIM records
- Use dedicated email service

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Database connection
python -c "from app.db.session import engine; engine.connect()"
```

## Support & Resources

- [FastAPI Deployment Docs](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://reactjs.org/docs/optimizing-performance.html)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance-tips.html)

---

**Ready to deploy? Start with DigitalOcean App Platform for the easiest experience!**
