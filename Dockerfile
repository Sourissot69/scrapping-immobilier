FROM python:3.11-slim-bullseye   # ← clé du problème
…
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        chromium-driver chromium \
        libnss3 libatk-bridge2.0-0 libgtk-3-0 fonts-liberation && \
    rm -rf /var/lib/apt/lists/*
…
