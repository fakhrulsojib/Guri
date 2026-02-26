# 🌍 Environment Setup Guide
> **Goal:** Standardized setup procedures for Development and Production environments in the Pulse AI monorepo.

## 🏗️ Overview
Pulse AI supports two distinct environments:
- **Development Environment:** For local development (localhost, proxy-based).
- **Production Environment:** For production deployment (domain-based, SSL).

## 📂 File Structure
| File/Directory | Environment | Description |
|---|---|---|
| `docker-compose.dev.yml` | Development | Localhost services. |
| `docker-compose.yml` | Production | Services with Nginx/SSL. |
| `nginx.conf` | Production | Nginx config with SSL. |
| `nginx.conf.dev` | Development | Nginx config without SSL. |
| `.env` / `.env.development` | All | Backend environment variables. |
| `frontend/.env` / `frontend/.env.development` | All | Frontend environment variables. |
| `dev.sh` / `run.sh` | All | Startup scripts. |

## 🚀 Quick Start
### 🛠️ For Developers (Local Development)
```bash
# 1. Start development environment
./dev.sh

# 2. Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Kafka UI: http://localhost:8080

# 3. Stop services
docker compose -f docker-compose.dev.yml down
```

### 🏭 For Production Deployment
```bash
# 1. Ensure production environment files are in place (.env, frontend/.env)
# 2. Start production environment
./run.sh

# 3. Stop services
docker compose down
```

## 🔧 Environment Configuration
### 💻 Development Environment
- **Backend**: Uses `.env.development` or defaults.
- **Frontend**: Uses `frontend/.env.development`.
- **Database**: PostgreSQL (persistent volumes).
- **Kafka**: Local persistent instance.
- **Proxy**: Vite dev server proxies `/api/*` to backend.

### 🌐 Production Environment  
- **Backend**: Uses `.env` (production defaults).
- **Frontend**: Uses `frontend/.env`.
- **Database**: PostgreSQL (persistent volumes).
- **SSL**: Nginx with Let's Encrypt certificates.

## 🚫 Constraints (AI Rules)
- Do NOT assume development and production share the same environment variables. Verify both `.env` and `.env.development` exist.
- Do NOT expose `docker-compose.yml` ports directly to the host without checking `nginx.conf` routing in production.
- Do NOT override SSL configuration paths dynamically in scripts without maintaining Certbot webroot compatibility.