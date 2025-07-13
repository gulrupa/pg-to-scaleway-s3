# Backup PostgreSQL vers Scaleway S3

Script de backup automatique de bases de données PostgreSQL vers Scaleway S3, conçu pour fonctionner dans un environnement Kubernetes.

## Fonctionnalités

- Backup automatique de bases PostgreSQL
- Upload vers Scaleway S3
- Nettoyage automatique des fichiers temporaires
- Gestion d'erreurs robuste
- Logs détaillés
- Configuration via variables d'environnement

## Structure du projet

```
pg-to-scaleway-s3/
├── backup_script.py      # Script principal de backup
├── test_backup.py        # Script de test de configuration
├── deployment.yaml       # Configuration Kubernetes CronJob
├── dockerfile           # Image Docker
├── start.sh             # Script de démarrage
└── README.md            # Ce fichier
```

## Configuration requise

### Variables d'environnement

Le script nécessite les variables d'environnement suivantes :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `PG_HOST` | Hôte PostgreSQL | `postgres.example.com` |
| `PG_PORT` | Port PostgreSQL | `5432` |
| `PG_USER` | Utilisateur PostgreSQL | `backup_user` |
| `PG_PASSWORD` | Mot de passe PostgreSQL | `secret_password` |
| `PG_DB` | Nom de la base de données | `docuseal` |
| `S3_BUCKET` | Nom du bucket S3 | `docuseal-backups` |
| `S3_REGION` | Région S3 | `fr-par` |
| `S3_ACCESS_KEY` | Clé d'accès S3 | `SCWXXXXXXXXXXXXXXX` |
| `S3_SECRET_KEY` | Clé secrète S3 | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `S3_ENDPOINT` | Endpoint S3 Scaleway | `https://s3.fr-par.scw.cloud` |
| `S3_PREFIX` | Préfixe optionnel pour les fichiers | `backups/` |
| `ARCHIVE_NAME` | Nom de base des archives | `backup` |

## Déploiement

### 1. Test local

Avant de déployer, testez la configuration localement :

```bash
# Installer les dépendances
pip install boto3

# Définir les variables d'environnement
export PG_HOST="your-postgres-host"
export PG_PORT="5432"
export PG_USER="your-user"
export PG_PASSWORD="your-password"
export PG_DB="docuseal"
export S3_BUCKET="your-bucket"
export S3_REGION="fr-par"
export S3_ACCESS_KEY="your-access-key"
export S3_SECRET_KEY="your-secret-key"
export S3_ENDPOINT="https://s3.fr-par.scw.cloud"

# Tester la configuration
python test_backup.py

# Tester le script de backup
python backup_script.py
```

### 2. Déploiement Kubernetes

#### Créer le secret

```bash
kubectl create secret generic pg-backup-secret \
  --from-literal=PG_HOST=your-postgres-host \
  --from-literal=PG_PORT=5432 \
  --from-literal=PG_USER=your-user \
  --from-literal=PG_PASSWORD=your-password \
  --from-literal=S3_ENDPOINT=https://s3.fr-par.scw.cloud \
  --from-literal=S3_REGION=fr-par \
  --from-literal=S3_ACCESS_KEY=your-access-key \
  --from-literal=S3_SECRET_KEY=your-secret-key
```

#### Déployer le CronJob

```bash
kubectl apply -f deployment.yaml
```

#### Vérifier le déploiement

```bash
# Voir les CronJobs
kubectl get cronjobs

# Voir les jobs récents
kubectl get jobs

# Voir les logs du dernier job
kubectl logs job/pg-backup-s3-docuseal-<timestamp>
```

## Dépannage

### Le job ne se termine pas

**Causes possibles :**

1. **Volume manquant** : Le script écrit dans `/backup/` mais aucun volume n'est monté
2. **Timeout de connexion** : La connexion PostgreSQL ou S3 prend trop de temps
3. **Erreur silencieuse** : Le script plante sans afficher d'erreur
4. **Ressources insuffisantes** : Le pod n'a pas assez de mémoire/CPU

**Solutions :**

1. **Vérifier les logs** :
   ```bash
   kubectl logs job/pg-backup-s3-docuseal-<timestamp>
   ```

2. **Vérifier l'état du pod** :
   ```bash
   kubectl describe pod <pod-name>
   ```

3. **Tester manuellement** :
   ```bash
   kubectl run test-backup --image=ghcr.io/gulrupa/gul-si-pg-backup:latest --rm -it --restart=Never --env="PG_HOST=..." --env="PG_PASSWORD=..." ...
   ```

### Erreurs courantes

#### Erreur de connexion PostgreSQL
```
Error during pg_dump: CalledProcessError
```
- Vérifier les credentials PostgreSQL
- Vérifier la connectivité réseau
- Vérifier que l'utilisateur a les droits de backup

#### Erreur S3
```
Credentials not available for S3 upload
```
- Vérifier les clés S3
- Vérifier les permissions du bucket
- Vérifier l'endpoint Scaleway

#### Erreur de volume
```
Permission denied: /backup/
```
- Le volume n'est pas monté correctement
- Vérifier la configuration du volume dans `deployment.yaml`

### Monitoring

#### Vérifier l'historique des jobs

```bash
# Jobs réussis
kubectl get jobs --field-selector status.successful=1

# Jobs échoués
kubectl get jobs --field-selector status.failed=1
```

#### Surveiller les logs en temps réel

```bash
# Suivre les logs du CronJob
kubectl logs -f cronjob/pg-backup-s3-docuseal
```

## Configuration avancée

### Modifier la planification

Le CronJob s'exécute par défaut tous les jours à 2h UTC. Pour modifier :

```yaml
spec:
  schedule: "0 2 * * *"  # Format cron
```

Exemples :
- `"0 */6 * * *"` : Toutes les 6 heures
- `"0 2 * * 0"` : Tous les dimanches à 2h
- `"0 2 1 * *"` : Le 1er de chaque mois à 2h

### Limites de ressources

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### Timeout et retry

```yaml
activeDeadlineSeconds: 3600  # Timeout de 1 heure
backoffLimit: 2              # Maximum 2 tentatives
```

## Sécurité

- Les credentials sont stockés dans des secrets Kubernetes
- Le volume temporaire est automatiquement nettoyé
- Les fichiers de backup sont supprimés après upload
- Le script utilise des timeouts pour éviter les blocages

## Support

En cas de problème :

1. Vérifier les logs avec `kubectl logs`
2. Tester la configuration avec `test_backup.py`
3. Vérifier la connectivité réseau
4. Contacter l'équipe DevOps
