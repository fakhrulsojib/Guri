# Environment Setup Guide

## Overview

Pulse AI supports two distinct environments:

1. **Development Environment** - For local development (localhost, proxy-based)
2. **Production Environment** - For production deployment (domain-based, SSL)

## File Structure

```
├── docker-compose.dev.yml      # Development services (localhost)
├── docker-compose.yml          # Production services (with nginx/SSL)
├── nginx.conf                  # Production nginx config (SSL)
├── nginx.conf.dev             # Development nginx config (no SSL)
├── .env                       # Production environment variables
├── .env.development           # Development environment variables
├── frontend/.env              # Frontend production config
├── frontend/.env.development  # Frontend development config
├── dev.sh                     # Development startup script
└── run.sh                    # Production startup script
```

## Quick Start

### For Developers (Local Development)

```bash
# 1. Start development environment
./dev.sh

# 2. Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Kafka UI: http://localhost:8080
# Nginx Proxy: http://localhost:8081

# 3. Stop services
docker compose -f docker-compose.dev.yml down
```

### For Production Deployment

```bash
# 1. Ensure production environment files are in place
# .env (production backend config)
# frontend/.env (production frontend config)

# 2. Start production environment
./run.sh

# 3. Setup SSL (first run only)
# See README.md for SSL certificate setup

# 4. Stop services
docker compose down
```

## Troubleshooting

### Development Issues
- Check if ports 3000, 8000, 8080 are available
- Ensure Docker and Docker Compose are running
- Check logs: `docker compose -f docker-compose.dev.yml logs -f`

### Production Issues
- Verify domain DNS settings
- Check SSL certificate validity
- Ensure ports 80/443 are open
- Check logs: `docker compose logs -f`

## Environment Configuration

### Development Environment
- **Backend**: Uses `.env.development` (if exists) or defaults
- **Frontend**: Uses `frontend/.env.development` 
- **Database**: PostgreSQL with persistent volumes
- **Kafka**: Local instance with persistent topics
- **Proxy**: Vite dev server proxies `/api/*` to backend

### Production Environment  
- **Backend**: Uses `.env` (production defaults)
- **Frontend**: Uses `frontend/.env`
- **Database**: PostgreSQL with persistent volumes
- **Kafka**: Production instance
- **SSL**: Nginx with Let's Encrypt certificates