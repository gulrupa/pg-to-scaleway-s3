Voici un README adapté pour votre projet GitHub :

---

# PostgreSQL Database Backup and Upload to Scaleway S3

Ce projet permet de créer une sauvegarde d'une base de données PostgreSQL en utilisant `pg_dump`, puis de télécharger le fichier exporté dans un bucket S3 Scaleway. Ce processus est automatisé via Docker et un script Python qui gère l'export et le téléversement du fichier.

## Prérequis

- **Docker** : Pour construire et exécuter l'application dans un environnement isolé.
- **Scaleway S3 Bucket** : Un compte Scaleway avec un bucket S3 configuré pour le stockage des sauvegardes.
- **PostgreSQL** : Base de données PostgreSQL accessible à partir du conteneur Docker.

## Fonctionnalités

- **Export PostgreSQL** : Utilise `pg_dump` pour exporter une base de données PostgreSQL au format `.tar`.
- **Téléversement vers Scaleway S3** : Le fichier de sauvegarde est téléchargé vers un bucket Scaleway S3.
- **Variables d'environnement** : Les paramètres nécessaires sont configurés via des variables d'environnement pour la flexibilité et la sécurité.

## Structure du projet

```
.
├── Dockerfile
├── backup_script.py
└── README.md
```

- **Dockerfile** : Définit l'image Docker utilisée pour créer l'environnement d'exécution, installer les dépendances et exécuter le script Python.
- **backup_script.py** : Le script Python qui effectue la sauvegarde de la base de données et télécharge le fichier vers S3.

## Variables d'Environnement

Pour que le programme fonctionne correctement, vous devez définir les variables d'environnement suivantes lors de l'exécution du conteneur Docker.

### Variables PostgreSQL

- `PG_HOST` : Adresse de l'hôte PostgreSQL.
- `PG_PORT` : Port du serveur PostgreSQL (par défaut 5432).
- `PG_USER` : Nom d'utilisateur pour se connecter à PostgreSQL.
- `PG_PASSWORD` : Mot de passe pour l'utilisateur PostgreSQL.
- `PG_DB` : Nom de la base de données à sauvegarder.

### Variables Scaleway S3

- `S3_BUCKET` : Nom du bucket Scaleway S3 où le fichier sera téléchargé.
- `S3_REGION` : Région de votre bucket Scaleway S3 (par exemple, "fr-par").
- `S3_PREFIX` : (Optionnel) Préfixe pour organiser les fichiers dans le bucket.
- `S3_ACCESS_KEY` : Clé d'accès AWS pour interagir avec Scaleway S3.
- `S3_SECRET_KEY` : Clé secrète d'accès AWS pour interagir avec Scaleway S3.

### Autres Variables

- `ARCHIVE_NAME` : (Optionnel) Nom de base pour le fichier de sauvegarde. Par défaut, il est défini sur `backup`.
  
## Utilisation

### Étape 1 : Créer l'image Docker

Clonez ce dépôt et naviguez dans le répertoire contenant le `Dockerfile`.

```bash
git clone <URL-du-dépôt>
cd <nom-du-dossier>
```

Ensuite, construisez l'image Docker :

```bash
docker build -t pg-backup-s3 .
```

### Étape 2 : Exécuter le conteneur Docker

Avant d'exécuter le conteneur, assurez-vous de définir les variables d'environnement nécessaires (comme expliqué dans la section précédente). Vous pouvez passer ces variables directement lors de l'exécution du conteneur avec la commande suivante :

```bash
docker run -e PG_HOST=<your-db-host> \
           -e PG_PORT=<your-db-port> \
           -e PG_USER=<your-db-user> \
           -e PG_PASSWORD=<your-db-password> \
           -e PG_DB=<your-db-name> \
           -e S3_BUCKET=<your-bucket-name> \
           -e S3_REGION=<your-region> \
           -e S3_ACCESS_KEY=<your-access-key> \
           -e S3_SECRET_KEY=<your-secret-key> \
           -v /path/to/local/backup/directory:/backup \
           pg-backup-s3
```

### Description des options :

- **-e** : Définit les variables d'environnement nécessaires pour la connexion à PostgreSQL et à Scaleway S3.
- **-v /path/to/local/backup/directory:/backup** : Monte un volume pour stocker la sauvegarde PostgreSQL exportée sur votre machine locale.
  
Le fichier de sauvegarde sera nommé sous la forme `<ARCHIVE_NAME>_<DATE_TIME>.tar`, et sera stocké à la fois localement dans le volume monté et dans le bucket S3.

### Étape 3 : Vérifier la sauvegarde

Une fois l'exécution terminée, vous pouvez vérifier :

1. **La sauvegarde locale** : Le fichier `.tar` de la base de données sera stocké dans le répertoire local monté.
2. **Le téléversement sur Scaleway S3** : Connectez-vous à votre compte Scaleway et vérifiez que le fichier a bien été téléchargé dans le bucket S3.

## Personnalisation

- **Nom de fichier de sauvegarde** : Vous pouvez personnaliser le nom du fichier de sauvegarde en définissant la variable `ARCHIVE_NAME` via les variables d'environnement.
- **Préfixe S3** : Utilisez `S3_PREFIX` pour organiser les fichiers dans le bucket.

## Dépannage

- **Problèmes de connexion PostgreSQL** : Vérifiez que les informations de connexion sont correctes et que le serveur PostgreSQL est accessible depuis le conteneur.
- **Problèmes avec S3** : Si le téléchargement échoue, assurez-vous que les clés d'accès S3 sont correctes et que le conteneur a bien accès à Internet.

---

### Contribuer

Les contributions sont les bienvenues ! Si vous souhaitez améliorer ce projet, vous pouvez soumettre une demande de tirage (pull request).
