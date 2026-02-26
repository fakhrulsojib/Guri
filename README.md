# 🚀 Pulse AI 
> **Goal:** A smart log analytics platform built with FastAPI, Kafka, and AI-powered insights.

## ⚡ Quick Start & Environments

### 💻 Local Development (No SSL/Domain required)
Perfect for developers who want to run the app locally.
1. Copy `.env.dev` to `.env` and configure credentials.
2. Start services:
```bash
./dev.sh
# or 
make dev
```
3. **Access Services:**
   - Frontend: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`
   - Kafka UI: `http://localhost:8080`
4. Stop services: `make dev-down`

### 🌐 Production Deployment (Domain + SSL)
For production deployment with SSL certificates and domain setup.
1. Copy `.env.prod` to `.env` and configure production settings.
2. Generate the Kafka-UI auth file:
```bash
sudo apt-get install -y apache2-utils
htpasswd -cb .htpasswd YOUR_USERNAME YOUR_PASSWORD
```
3. Start services:
```bash
./prod.sh
# or 
make prod
```
4. Stop services: `make prod-down`

## 🔒 SSL Certificate Setup (First Run Production)
1. DNS A record points your domain to this server.
2. Ensure containers are up and `nginx_proxy` is serving `/.well-known`:
   `docker compose up -d nginx`
3. Issue the certificate using Certbot:
   ```bash
   docker run --rm -it \
     -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
     -v "$(pwd)/certbot/www:/var/www/certbot" \
     certbot/certbot certonly --webroot \
     -w /var/www/certbot \
     -d your-domain.com \
     --email your-email@example.com --agree-tos --no-eff-email
   ```
4. Reload nginx: `docker compose exec nginx nginx -s reload`

## 🔄 Production Deployment & Maintenance
### Deploying Updates
```bash
docker compose pull            # Pull latest base images
docker compose build --pull    # Rebuild with latest deps
docker compose up -d --remove-orphans
```

### Docker Cleanup (Image Management)
Old images can consume significant disk space. Use the included cleanup script:
```bash
./scripts/docker-cleanup.sh    # Prune images/containers older than 7 days
```
**Automate on production** (optional cron — runs every Sunday at 2 AM):
```bash
0 2 * * 0 /path/to/scripts/docker-cleanup.sh >> /var/log/docker-cleanup.log 2>&1
```

> 💡 **Local machines too:** Run `docker system prune -f` locally every couple of weeks to reclaim disk space.

## 🛠️ Tech Stack & Components
| Component | Technology | Description |
|---|---|---|
| **Backend API** | FastAPI, asyncpg, Python | RESTful API with Google OAuth. |
| **Frontend UI** | React, Vite, TS | Modern web interface (multi-stage Docker build for production). |
| **Database** | PostgreSQL | User management and log storage. |
| **Streaming** | Apache Kafka | Real-time log streaming. |
| **Vector DB** | ChromaDB | Database for AI-powered insights. |
| **Reverse Proxy** | Nginx | SSL termination, security headers, rate limiting, Kafka-UI auth. |

## 🚫 Constraints (AI Rules)
- Do NOT assume the SSL environment uses the same compose file. Production uses specific `nginx` routes and `docker-compose.yml`.
- Do NOT suggest modifying the `dev.sh` and `prod.sh` wrapper scripts lightly; rely on `.env` variable overrides instead.
- Do NOT commit `.htpasswd` or `.env` files to source control.