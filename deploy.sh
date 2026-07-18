#!/bin/bash

set -e

APP_DIR="$HOME/project/TOMO-Financial-Buddy"

echo "==> Masuk ke project"
cd "$APP_DIR"

echo "==> Git pull"
git pull

echo "==> Stop containers"
docker compose down

echo "==> Build & Start containers"
docker compose up -d --build

echo ""
echo "=================================="
echo "Deploy selesai!"
echo "=================================="

docker compose ps
