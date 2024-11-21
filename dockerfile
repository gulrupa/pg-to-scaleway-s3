# Utiliser une image de base Alpine
FROM python:3.9-alpine

# Installer les dépendances nécessaires : PostgreSQL client, curl, unzip et AWS CLI
RUN apk add --no-cache \
    postgresql-client \
    curl \
    unzip \
    bash && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && ./aws/install && \
    rm -rf awscliv2.zip aws && \
    apk del unzip && \
    rm -rf /var/cache/apk/*

RUN pip install --no-cache-dir boto3

# Créer un répertoire pour le script et les exports
WORKDIR /app
VOLUME /backup

# Copier le script dans l'image
COPY backup_script.py /app/backup_script.py

# Commande par défaut
CMD ["python", "backup_script.py"]