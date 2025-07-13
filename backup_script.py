import os
import subprocess
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError
import sys

# Récupérer les variables d'environnement
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DB = os.getenv("PG_DB")

S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION")
S3_PREFIX = os.getenv("S3_PREFIX", "")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_ENDPOINT = os.getenv("S3_ENDPOINT")

ARCHIVE_NAME = os.getenv("ARCHIVE_NAME", "backup")

# Construire le nom du fichier
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
file_name = f"{ARCHIVE_NAME}_{timestamp}.tar"
file_path = f"/backup/{file_name}"

def cleanup_file(file_path):
    """Nettoie le fichier temporaire"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        print(f"Warning: Could not clean up {file_path}: {e}")

def backup_database():
    try:
        print(f"Starting backup of database {PG_DB}...")
        print(f"Host: {PG_HOST}, Port: {PG_PORT}, User: {PG_USER}")
        
        # Vérifier que le répertoire de backup existe
        os.makedirs("/backup", exist_ok=True)
        
        os.environ["PGPASSWORD"] = PG_PASSWORD
        dump_command = [
            "pg_dump",
            "-h", PG_HOST,
            "-p", PG_PORT,
            "-U", PG_USER,
            "-F", "t",  # Format tar
            "-f", file_path,
            PG_DB
        ]
        
        print(f"Running command: {' '.join(dump_command[:4])} ... -f {file_path} {PG_DB}")
        result = subprocess.run(dump_command, check=True, capture_output=True, text=True)
        
        if result.stdout:
            print(f"pg_dump stdout: {result.stdout}")
        if result.stderr:
            print(f"pg_dump stderr: {result.stderr}")
            
        print(f"Database backup completed: {file_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during pg_dump: {e}")
        print(f"Return code: {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error during backup: {e}")
        return False

def upload_to_s3():
    try:
        print(f"Uploading {file_name} to S3 bucket {S3_BUCKET} at {S3_ENDPOINT}...")
        
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            print(f"Error: Backup file not found at {file_path}")
            return False
            
        # Configurer Boto3 avec les credentials et l'endpoint Scaleway
        s3 = boto3.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION,
            endpoint_url=S3_ENDPOINT  # Scaleway S3 endpoint
        )
        
        # Ajouter un préfixe si spécifié
        s3_key = f"{S3_PREFIX}/{file_name}" if S3_PREFIX else file_name
        s3.upload_file(file_path, S3_BUCKET, s3_key)
        print(f"Upload completed successfully: {s3_key}")
        return True
        
    except NoCredentialsError:
        print("Credentials not available for S3 upload.")
        return False
    except Exception as e:
        print(f"Error during S3 upload: {e}")
        return False

def main():
    print(f"Starting backup process at {datetime.now()}")
    
    # Vérifier les variables d'environnement critiques
    required_vars = ["PG_HOST", "PG_USER", "PG_PASSWORD", "PG_DB", "S3_BUCKET", "S3_ACCESS_KEY", "S3_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    try:
        # Effectuer le backup
        if not backup_database():
            print("Backup failed, exiting")
            sys.exit(1)
        
        # Upload vers S3
        if not upload_to_s3():
            print("S3 upload failed, exiting")
            sys.exit(1)
        
        # Nettoyer le fichier temporaire
        cleanup_file(file_path)
        
        print(f"Backup process completed successfully at {datetime.now()}")
        sys.exit(0)
        
    except Exception as e:
        print(f"Unexpected error in main process: {e}")
        cleanup_file(file_path)
        sys.exit(1)

if __name__ == "__main__":
    main()