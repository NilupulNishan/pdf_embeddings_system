#!/usr/bin/env bash
set -e

# Azure provides PORT environment variable
PORT="${PORT:-8080}"

echo "Starting container on port: $PORT"

# Update nginx to listen on Azure-provided port
# (Your nginx.conf must contain: listen 8080;)
sed -i "s/listen 8080;/listen ${PORT};/g" /etc/nginx/conf.d/default.conf || true

# Start Streamlit (internal only, nginx proxies to it)
echo "Starting Streamlit..."
streamlit run streamlit_app.py \
    --server.port 8501 \
    --server.address 127.0.0.1 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false &

# Give Streamlit a moment to start (optional but safe)
sleep 3

# Start Nginx in foreground (required for Docker)
echo "Starting Nginx..."
nginx -g "daemon off;"