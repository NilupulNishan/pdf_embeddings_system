# Dockerfile (Azure App Service - Docker container)
# Nginx (public) listens on $PORT (Azure sets it, commonly 8080)
# Streamlit (internal) listens on 127.0.0.1:8501
# Nginx serves PDFs from /app/data/pdfs at /pdfs/ and proxies "/" to Streamlit

FROM python:3.11-slim

WORKDIR /app

# -----------------------------
# System deps
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Python deps
# -----------------------------
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# -----------------------------
# App code
# -----------------------------
COPY . /app

# -----------------------------
# Ensure data directories exist
# -----------------------------
RUN mkdir -p /app/data/pdfs /app/data/chroma_db /app/data/docstore

# -----------------------------
# Nginx config
# -----------------------------
# Put nginx.conf in the SAME folder as this Dockerfile
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Remove default site config if present (depends on nginx package)
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default || true

# -----------------------------
# Azure App Service uses PORT env var
# -----------------------------
ENV PORT=8080

# Streamlit defaults
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# -----------------------------
# Startup script
# -----------------------------
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080

CMD ["/start.sh"]