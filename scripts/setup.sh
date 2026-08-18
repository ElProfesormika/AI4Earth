#!/usr/bin/env bash
set -e
cp -n .env.example .env 2>/dev/null || true
if ! bash scripts/compose.sh | grep -q .; then
  echo "Docker Compose not found."
  echo "Install on Ubuntu 24.04: sudo apt install -y docker-compose-v2"
  echo "Or run: make install-compose"
  exit 1
fi
echo "SmartWasteAI setup complete."
echo "Run: make up"
