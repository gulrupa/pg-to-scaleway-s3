#!/bin/bash

set -e

# Vérification des variables d'environnement
if [ -z "$SOURCE_DB_URL" ]; then
  echo "Erreur : SOURCE_DB_URL n'est pas défini."
  exit 1
fi

if [ -z "$TARGET_DB_URL" ]; then
  echo "Erreur : TARGET_DB_URL n'est pas défini."
  exit 1
fi

# Fichier de sauvegarde
EXPORT_FILE="/backup/db_backup.tar"

echo "Début de l'exportation de la base de données source..."
pg_dump --format=tar --no-owner --file="$EXPORT_FILE" "$SOURCE_DB_URL"
echo "Export terminé. Fichier sauvegardé : $EXPORT_FILE"

echo "Début de la restauration dans la base de données cible..."
pg_restore --clean --no-owner --dbname="$TARGET_DB_URL" "$EXPORT_FILE"
echo "Restauration terminée."   