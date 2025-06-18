FROM python:3.11-slim-bullseye

# 1. Dépendances système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        chromium-driver \
        chromium \
        wget unzip \
        libnss3 libatk-bridge2.0-0 libgtk-3-0 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BINARY=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 2. Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Code
COPY . .

# 4. Flask : déclare l’appli et écoute le port Railway
ENV FLASK_APP=app.py          # ← ton mini-serveur ajouté
ENV PORT=3000                 # Railway l’écrase au déploiement, mais ça fixe le local

# 5. Démarrage
CMD ["flask", "run", "--host=0.0.0.0", "--port", "3000"]
