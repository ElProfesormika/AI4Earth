#!/usr/bin/env bash
# Detect docker compose command (plugin or standalone v2)
if docker compose version >/dev/null 2>&1; then
  echo "docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  echo "docker-compose"
else
  echo ""
fi
