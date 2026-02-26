#!/bin/bash
# docker-cleanup.sh
# Remove unused Docker images, containers, and build cache.
# Safe to run: only removes resources not used by running containers.

set -euo pipefail

echo "=== Docker Cleanup ==="
echo ""

echo "1/3 Pruning stopped containers..."
docker container prune -f

echo ""
echo "2/3 Pruning unused images (older than 7 days)..."
docker image prune -a -f --filter "until=168h"

echo ""
echo "3/3 Pruning build cache (older than 7 days)..."
docker builder prune -f --filter "until=168h"

echo ""
echo "=== Done. Current disk usage ==="
docker system df
