#!/bin/bash
set -e

echo "🚀 Starting Pulse AI Development Environment..."

startup(){
  echo "📦 Starting development services..."
  docker compose -f docker-compose.dev.yml up -d

  echo "⏳ Waiting for services to be ready..."
  sleep 10

  echo "🗄️ Setting up database tables..."
  
  # Check if tables exist before creating them
  if ! docker exec -i postgres_db_dev psql -U postgres -d fastapi_db -c "SELECT 1 FROM users LIMIT 1;" >/dev/null 2>&1; then
    echo "Creating users table..."
    docker exec -i postgres_db_dev psql -U postgres -d fastapi_db < resources/database/ddl/users.sql
  else
    echo "Users table already exists"
  fi
  
  if ! docker exec -i postgres_db_dev psql -U postgres -d fastapi_db -c "SELECT 1 FROM refresh_tokens LIMIT 1;" >/dev/null 2>&1; then
    echo "Creating refresh_tokens table..."
    docker exec -i postgres_db_dev psql -U postgres -d fastapi_db < resources/database/ddl/refresh_tokens.sql
  else
    echo "Refresh tokens table already exists"
  fi
  
  if ! docker exec -i postgres_db_dev psql -U postgres -d fastapi_db -c "SELECT 1 FROM log_sources LIMIT 1;" >/dev/null 2>&1; then
    echo "Creating log_sources table..."
    docker exec -i postgres_db_dev psql -U postgres -d fastapi_db < resources/database/ddl/log_sources.sql
  else
    echo "Log sources table already exists"
  fi
  
  if ! docker exec -i postgres_db_dev psql -U postgres -d fastapi_db -c "SELECT 1 FROM raw_logs LIMIT 1;" >/dev/null 2>&1; then
    echo "Creating raw_logs table..."
    docker exec -i postgres_db_dev psql -U postgres -d fastapi_db < resources/database/ddl/raw_logs.sql
  else
    echo "Raw logs table already exists"
  fi

  echo "📊 Ensuring Kafka topic exists..."
  if docker exec kafka_dev sh -c "kafka-topics --bootstrap-server localhost:9092 --list | grep -qx raw_logs" >/dev/null 2>&1; then
    echo "Kafka topic raw_logs already exists"
  else
    echo "Creating Kafka topic raw_logs..."
    docker exec kafka_dev kafka-topics --create --topic raw_logs \
      --bootstrap-server localhost:9092 \
      --partitions 1 \
      --replication-factor 1
  fi

  echo "✅ Development environment is ready!"
  echo ""
  echo "🌐 Frontend: http://localhost:3000"
  echo "🔧 Backend API: http://localhost:8000"
  echo "📚 API Docs: http://localhost:8000/docs"
  echo "🗄️ Kafka UI: http://localhost:8080"
  echo "🌐 Nginx Proxy: http://localhost:8081"
  echo "🐘 PostgreSQL: localhost:5432"
  echo "🔍 ChromaDB: localhost:8001"
  echo ""
  echo "📋 View logs: docker compose -f docker-compose.dev.yml logs -f"
  echo "🛑 Stop services: docker compose -f docker-compose.dev.yml down"
}

cleanup(){
  echo "🛑 Stopping development services..."
  docker compose -f docker-compose.dev.yml down
}

trap cleanup INT TERM
startup 