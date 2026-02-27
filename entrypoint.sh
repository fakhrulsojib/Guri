#!/bin/sh
set -e

# Fix ownership of volume-mounted directories (Docker volumes mount as root)
chown -R appuser:appgroup /app/logs 2>/dev/null || true

# Drop to non-root user and exec the main command
exec gosu appuser "$@"
