# Utiliser une image officielle de PostgreSQL comme base
FROM postgres:latest

# Installer les outils nécessaires
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /backup

# Copier le script de gestion des bases de données dans le conteneur
COPY backup_and_restore.sh /usr/local/bin/backup_and_restore.sh
RUN chmod +x /usr/local/bin/backup_and_restore.sh

# Définir le point d'entrée
ENTRYPOINT ["/usr/local/bin/backup_and_restore.sh"]

# Documentation des variables d'environnement
ENV SOURCE_DB_URL=""
ENV TARGET_DB_URL=""
