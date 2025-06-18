FROM python:3.11-slim-bullseye   # ✔ reste sur bullseye

# 1. Ajoute le dépôt sécurité bullseye (contient chromium)
RUN echo "deb http://deb.debian.org/debian-security bullseye-security main" \
        > /etc/apt/sources.list.d/bullseye-security.list

# 2. Install
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        chromium chromium-driver \
        libnss3 libatk-bridge2.0-0 libgtk-3-0 fonts-liberation && \
    rm -rf /var/lib/apt/lists/*
