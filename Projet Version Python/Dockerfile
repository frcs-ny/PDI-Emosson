# On part sur une image Python officielle et légère
FROM python:3.11-slim

# Installation des dépendances système nécessaires pour PostgreSQL
# (C'est l'équivalent de votre "apt-get install libpq-dev" en PHP)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# On définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie du fichier des dépendances Python (à créer, voir plus bas)
COPY requirements.txt .

# Installation des bibliothèques Python
RUN pip install --no-cache-dir -r requirements.txt

# Flask écoute par défaut sur le port 5000 (et non plus 80 comme Apache)
EXPOSE 5000

# Lancement du serveur de développement Flask (avec écoute sur toutes les interfaces)
CMD ["flask", "run", "--host=0.0.0.0"]