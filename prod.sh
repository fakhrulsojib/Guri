#!/bin/bash
set -e

startup(){
  echo "EXECUTING: docker compose up -d"
  docker compose up -d

  echo "EXECUTING: compose logs -f"
  docker compose logs -f
}

cleanup(){
  echo "EXECUTING: docker compose down"
  docker compose down
}

trap cleanup INT TERM
startup