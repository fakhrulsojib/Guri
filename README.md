# Pulse AI

A smart log analytics platform built with FastAPI, Kafka, and AI-powered insights.

## 🚀 Quick Start

### Prerequisites
- Latest Docker and Docker Compose
- Executable permissions for `run.sh`

### Basic Usage
1. Configure your `.env` file with your own settings
2. Run `bash run.sh` to start all services

## 🛠️ First Time Setup

### 1. Environment Configuration

Create a `.env` file with your Google OAuth credentials:

```bash
# Copy example environment file
cp example.env .env

# Edit with your actual Google OAuth credentials
nano .env
```

**Required Environment Variables:**
- `GOOGLE_CLIENT_ID` - Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Your Google OAuth client secret  
- `JWT_SECRET` - A secure random string for JWT signing

### 2. Start Services

```bash
# Start all services (FastAPI, PostgreSQL, Kafka, ChromaDB, Frontend)
bash run.sh
```

### 3. Kafka Topic & Database Setup

```bash
# Create Kafka topic
docker exec kafka kafka-topics --create --topic raw_logs \
  --bootstrap-server kafka:9093 \
  --partitions 1 \
  --replication-factor 1

# Create database tables
docker exec -i postgres_db psql -U postgres -d fastapi_db < resources/database/ddl/users.sql
docker exec -i postgres_db psql -U postgres -d fastapi_db < resources/database/ddl/refresh_tokens.sql
docker exec -i postgres_db psql -U postgres -d fastapi_db < resources/database/ddl/log_sources.sql
docker exec -i postgres_db psql -U postgres -d fastapi_db < resources/database/ddl/raw_logs.sql
```

### 4. Verify Setup

```bash
# Check services status
docker compose ps

# Verify Kafka topic
docker exec kafka kafka-topics --list --bootstrap-server kafka:9093

# Verify database tables
docker exec postgres_db psql -U postgres -d fastapi_db -c "\dt"
```

## 📋 What's Included

- **FastAPI Backend** - RESTful API with Google OAuth authentication
- **React TypeScript Frontend** - Modern web interface built with Vite
- **PostgreSQL Database** - User management and log storage
- **Apache Kafka** - Real-time log streaming and processing
- **ChromaDB** - Vector database for AI-powered insights
- **JWT Authentication** - Secure token-based authentication system

## 🌐 Frontend Development

The frontend is a React TypeScript application built with Vite that runs entirely through Docker.

**Tech Stack:**
- React 18
- TypeScript
- Vite
- Minimal dependencies

**Access:**
- Development: http://localhost:3000
- Hot reload enabled for development

**Build for Production:**
```bash
docker compose exec frontend npm run build
```

## 🔧 Service Ports

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Kafka UI**: http://localhost:8080
- **PostgreSQL**: localhost:5432
- **ChromaDB**: http://localhost:8001