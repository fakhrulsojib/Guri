# 🌍 Environment Setup Guide
> **Goal:** Standardized setup procedures for Development and Production environments in the Pulse AI monorepo.

## 🏗️ Overview
Pulse AI supports two distinct environments:
- **Development Environment:** For local development (localhost, proxy-based).
- **Production Environment:** For production deployment (domain-based, SSL, hardened).

## 📂 File Structure
| File/Directory | Environment | Description |
|---|---|---|
| `docker-compose.dev.yml` | Development | Localhost services with exposed ports for debugging. |
| `docker-compose.yml` | Production | Hardened services with Nginx/SSL, no exposed internal ports. |
| `Dockerfile` | All | Backend image (Python 3.11, non-root user). |
| `frontend/Dockerfile` | Production | Multi-stage frontend build (Vite build → Nginx static serving). |
| `.dockerignore` | All | Excludes secrets, logs, and dev files from build context. |
| `nginx.conf` | Production | Nginx with SSL, security headers, rate limiting, Kafka-UI auth. |
| `nginx.conf.dev` | Development | Nginx config without SSL. |
| `.env` / `.env.development` | All | Backend environment variables. |
| `frontend/.env` / `frontend/.env.development` | All | Frontend environment variables. |
| `.htpasswd` | Production | HTTP Basic Auth credentials for Kafka-UI (not committed). |
| `dev.sh` / `run.sh` | All | Startup scripts. |
| `scripts/docker-cleanup.sh` | All | Prune unused Docker images, containers, and build cache. |

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
# 2. Generate Kafka-UI auth file (first time only):
htpasswd -cb .htpasswd YOUR_USERNAME YOUR_PASSWORD

# 3. Start production environment
./run.sh

# 4. Stop services
docker compose down
```

## 🔧 Environment Configuration
### 💻 Development Environment
- **Backend**: Uses `.env.development` or defaults. Runs with `--reload`.
- **Frontend**: Uses `frontend/.env.development`. Runs Vite dev server.
- **Database**: PostgreSQL with ports exposed to host for direct querying.
- **Kafka**: Local persistent instance with ports exposed.
- **Proxy**: Nginx dev config or direct Vite dev server proxy.

### 🌐 Production Environment  
- **Backend**: Uses `.env`. Baked into Docker image (no live volume mounts). Non-root user.
- **Frontend**: Multi-stage build → static files served by Nginx.
- **Database**: PostgreSQL (internal only, access via `docker exec`).
- **SSL**: Nginx with Let's Encrypt certificates.
- **Security**: `server_tokens off`, security headers, API rate limiting, Kafka-UI behind basic auth.

## 🔄 Maintenance
### Database Access (Production)
```bash
# No ports are exposed — use docker exec
docker exec -it postgres_db psql -U user -d fastapi_db
docker exec -it redis_cache redis-cli
```

### Docker Cleanup
```bash
./scripts/docker-cleanup.sh          # Weekly cleanup
docker system prune -a --volumes     # Nuclear option (deletes everything including DB volumes!)
```

## 🚫 Constraints (AI Rules)
- Do NOT assume development and production share the same environment variables. Verify both `.env` and `.env.development` exist.
- Do NOT expose `docker-compose.yml` ports directly to the host without checking `nginx.conf` routing in production.
- Do NOT override SSL configuration paths dynamically in scripts without maintaining Certbot webroot compatibility.
- Do NOT commit `.htpasswd` or `.env` files to source control.