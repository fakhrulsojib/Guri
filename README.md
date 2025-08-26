# Pulse AI

A smart log analytics platform built with FastAPI, Kafka, and AI-powered insights.

## 🚀 Quick Start

### Prerequisites
- Latest Docker and Docker Compose
- Executable permissions for scripts

### Environment Selection

**For Local Development (No SSL/Domain required):**
```bash
./dev.sh
# or
make dev
```

**For Production (SSL/Domain required):**
```bash
./prod.sh
# or
make prod
```

## 🛠️ Setup Instructions

### Development Environment (Local)

Perfect for developers who want to run the app locally without SSL setup.

1. **Environment Configuration**
```bash
# Copy development environment file
cp .env.dev .env

# Edit with your Google OAuth credentials
nano .env
```

2. **Start Development Services**
```bash
./dev.sh
# or
make dev
```

3. **Access Services**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Kafka UI: http://localhost:8080
- PostgreSQL: localhost:5432
- ChromaDB: localhost:8001

4. **Stop Services**
```bash
docker compose -f docker-compose.dev.yml down
# or
make dev-down
```

### Production Environment (Domain + SSL)

For production deployment with SSL certificates and domain setup.

1. **Environment Configuration**
```bash
# Copy production environment file
cp .env.prod .env

# Edit with your production settings
nano .env
```

2. **Start Production Services**
```bash
./prod.sh
# or
make prod
```

3. **SSL Certificate Setup (First Run)**
Prereqs: DNS A record points your domain to this server. Update `nginx.conf` `server_name` if needed.

1) Ensure containers are up and `nginx_proxy` is serving `/.well-known` from `certbot/www` (already configured):
```bash
docker compose -f docker-compose.prod.yml up -d nginx
```

2) Issue the certificate using Certbot Docker (webroot):
```bash
docker run --rm -it \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d your-domain.com \
  --email your-email@example.com --agree-tos --no-eff-email
```

3) Reload nginx to pick up the certs:
```bash
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

4) Auto-renew (cron):
```bash
# Edit root crontab
sudo crontab -e
# Add (runs daily at 3:15am; reloads nginx if renewed):
15 3 * * * docker run --rm \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot renew --quiet && docker compose -f $(pwd)/docker-compose.prod.yml exec nginx nginx -s reload
```

4. **Stop Services**
```bash
docker compose -f docker-compose.prod.yml down
# or
make prod-down
```

## 🎯 Quick Commands

**Development:**
- `make dev` - Start development environment
- `make dev-down` - Stop development environment  
- `make logs-dev` - View development logs

**Production:**
- `make prod` - Start production environment
- `make prod-down` - Stop production environment
- `make logs-prod` - View production logs

**Utility:**
- `make clean` - Remove all containers and volumes
- `make help` - Show available commands

## 📋 What's Included

- **FastAPI Backend** - RESTful API with Google OAuth authentication
- **React TypeScript Frontend** - Modern web interface built with Vite
- **PostgreSQL Database** - User management and log storage
- **Apache Kafka** - Real-time log streaming and processing
- **ChromaDB** - Vector database for AI-powered insights
- **JWT Authentication** - Secure token-based authentication system

## 🌐 Live Demo

A live site available at: https://fakhrulsojib.mooo.com