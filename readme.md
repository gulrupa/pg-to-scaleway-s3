# Documentation : Docker PostgreSQL Backup and Restore

Cette documentation détaille l'utilisation d'un conteneur Docker pour :  
- Exporter le contenu d'une base de données PostgreSQL source à l'aide de `pg_dump`.  
- Importer ce contenu dans une base de données PostgreSQL cible à l'aide de `pg_restore`.  
- Stocker les fichiers de sauvegarde dans un volume Docker ou un répertoire local.

---

## Prérequis

- **Docker** doit être installé sur votre machine.
- Les bases de données source et cible doivent être accessibles via des URL PostgreSQL au format `postgresql://user:password@host/dbname`.

---

## Configuration

### Dockerfile

Le `Dockerfile` définit l'image Docker utilisée pour exécuter le processus. Il installe les outils nécessaires et configure un script d'entrée.

### Variables d'environnement

Le conteneur nécessite deux variables d'environnement :  

| Variable          | Description                                                             | Exemple                                  | Obligatoire |
|--------------------|-------------------------------------------------------------------------|------------------------------------------|-------------|
| `SOURCE_DB_URL`    | URL de connexion de la base de données source.                         | `postgresql://user:password@source-host/dbname` | Oui         |
| `TARGET_DB_URL`    | URL de connexion de la base de données cible.                          | `postgresql://user:password@target-host/dbname` | Oui         |

### Volumes

Un volume Docker est monté sur `/backup` pour stocker le fichier `.tar` généré par `pg_dump`.  
Vous pouvez utiliser un volume Docker ou un répertoire local pour accéder aux fichiers de sauvegarde.

---

## Instructions d'utilisation

### Étape 1 : Construire l'image Docker

Créez une image Docker à partir du `Dockerfile` :

```bash
docker build -t postgres-backup-restore .
```

### Étape 2 : Préparer un volume ou un répertoire local

- **Option 1 : Utiliser un volume Docker**  
  Créez un volume pour stocker les sauvegardes :
  ```bash
  docker volume create postgres_backup_volume
  ```

- **Option 2 : Utiliser un répertoire local**  
  Créez un répertoire local pour stocker les fichiers de sauvegarde :
  ```bash
  mkdir -p ./postgres_backups
  ```

### Étape 3 : Lancer le conteneur

Exécutez le conteneur avec les variables d'environnement configurées.

#### Avec un volume Docker

```bash
docker run --rm \
  -e SOURCE_DB_URL="postgresql://user:password@source-host/dbname" \
  -e TARGET_DB_URL="postgresql://user:password@target-host/dbname" \
  -v postgres_backup_volume:/backup \
  postgres-backup-restore
```

#### Avec un répertoire local

```bash
docker run --rm \
  -e SOURCE_DB_URL="postgresql://user:password@source-host/dbname" \
  -e TARGET_DB_URL="postgresql://user:password@target-host/dbname" \
  -v $(pwd)/postgres_backups:/backup \
  postgres-backup-restore
```

---

## Structure des fichiers

Les sauvegardes sont stockées sous forme de fichiers `.tar` dans le répertoire `/backup`. Par défaut :  
- Un fichier nommé `db_backup.tar` est généré pour chaque export.  
- Ce fichier est ensuite utilisé pour la restauration.

### Exemple d'accès au volume

- Si un volume Docker est utilisé :  
  Inspectez le contenu avec :
  ```bash
  docker run --rm \
    -v postgres_backup_volume:/backup \
    alpine ls /backup
  ```

- Si un répertoire local est utilisé :  
  Listez directement les fichiers dans le répertoire :
  ```bash
  ls ./postgres_backups
  ```

---

## Explications techniques

### Outils utilisés

- **`pg_dump`** : Outil PostgreSQL utilisé pour exporter le contenu d'une base de données sous forme de fichier `.tar`.  
- **`pg_restore`** : Utilisé pour restaurer une base à partir du fichier `.tar`.

### Script Bash : `backup_and_restore.sh`

Le script exécute les étapes suivantes :

1. Vérifie que les variables d'environnement `SOURCE_DB_URL` et `TARGET_DB_URL` sont définies.
2. Utilise `pg_dump` pour exporter le contenu de la base source dans `/backup/db_backup.tar`.
3. Utilise `pg_restore` pour importer le contenu du fichier exporté dans la base cible.

---

## Développement

### Structure du projet

```
.
├── Dockerfile               # Définition de l'image Docker
├── backup_and_restore.sh    # Script Bash pour l'export et la restauration
└── README.md                # Documentation
```

### Contribuer

Les contributions sont les bienvenues !  
Ouvrez une **issue** ou soumettez une **pull request** pour signaler un problème ou proposer une amélioration.

