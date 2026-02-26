#!/bin/bash
set -e

check_prerequisites(){
  echo "🔍 Checking prerequisites..."

  # 1. Check .env file
  if [ ! -f .env ]; then
    echo "❌ .env file not found."
    echo "   Copy .env.prod or .env.example to .env and configure it."
    exit 1
  fi
  echo "  ✅ .env file found"

  # 2. Check .htpasswd for Kafka-UI basic auth
  if [ ! -f .htpasswd ]; then
    echo ""
    echo "⚠️  .htpasswd file not found (required for Kafka-UI authentication)."
    read -p "   Would you like to create it now? (y/n): " CREATE_HTPASSWD
    if [ "$CREATE_HTPASSWD" = "y" ] || [ "$CREATE_HTPASSWD" = "Y" ]; then
      read -p "   Enter username for Kafka-UI: " KAFKAUI_USER
      read -s -p "   Enter password for Kafka-UI: " KAFKAUI_PASS
      echo ""

      if command -v htpasswd &> /dev/null; then
        htpasswd -cb .htpasswd "$KAFKAUI_USER" "$KAFKAUI_PASS"
      else
        # Fallback: use Docker to generate the htpasswd file
        echo "   htpasswd not found locally, using Docker to generate..."
        docker run --rm httpd:alpine htpasswd -cb /dev/stdout "$KAFKAUI_USER" "$KAFKAUI_PASS" > .htpasswd
      fi
      echo "  ✅ .htpasswd created"
    else
      echo "❌ .htpasswd is required. Aborting."
      exit 1
    fi
  else
    echo "  ✅ .htpasswd file found"
  fi

  # 3. Check SSL certificates
  CERT_PATH="./certbot/conf/live"
  if [ ! -d "$CERT_PATH" ] || [ -z "$(ls -A "$CERT_PATH" 2>/dev/null)" ]; then
    echo ""
    echo "⚠️  SSL certificates not found in $CERT_PATH"
    echo "   Nginx will fail to start without them."
    echo ""
    echo "   To issue certificates:"
    echo "   1. Ensure your domain DNS points to this server"
    echo "   2. Start Nginx in HTTP-only mode first:"
    echo "      docker compose up -d nginx"
    echo "   3. Run Certbot:"
    echo "      docker run --rm -it \\"
    echo "        -v \"\$(pwd)/certbot/conf:/etc/letsencrypt\" \\"
    echo "        -v \"\$(pwd)/certbot/www:/var/www/certbot\" \\"
    echo "        certbot/certbot certonly --webroot \\"
    echo "        -w /var/www/certbot \\"
    echo "        -d your-domain.com \\"
    echo "        --email your-email@example.com --agree-tos --no-eff-email"
    echo ""
    read -p "   Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
      exit 1
    fi
  else
    echo "  ✅ SSL certificates found"
  fi

  echo ""
  echo "✅ All prerequisites checked."
  echo ""
}

startup(){
  check_prerequisites

  echo "EXECUTING: docker compose build --pull"
  docker compose build --pull

  echo "EXECUTING: docker compose up -d --remove-orphans"
  docker compose up -d --remove-orphans

  echo "EXECUTING: docker compose logs -f"
  docker compose logs -f
}

cleanup(){
  echo "EXECUTING: docker compose down"
  docker compose down
}

trap cleanup INT TERM
startup