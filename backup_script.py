import os
import subprocess
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError

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
S3_ENDPOINT = f"https://{S3_BUCKET}.s3.{S3_REGION}.scw.cloud"

ARCHIVE_NAME = os.getenv("ARCHIVE_NAME", "backup")

# Construire le nom du fichier
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
file_name = f"{ARCHIVE_NAME}_{timestamp}.tar"
file_path = f"/backup/{file_name}"

def backup_database():
    try:
        print(f"Starting backup of database {PG_DB}...")
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
        subprocess.run(dump_command, check=True)
        print(f"Database backup completed: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during pg_dump: {e}")
        exit(1)

def upload_to_s3():
    try:
        print(f"Uploading {file_name} to S3 bucket {S3_BUCKET} at {S3_ENDPOINT}...")
        # Configurer Boto3 avec les credentials et l'endpoint Scaleway
        s3 = boto3.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name: S3_REGION,
            endpoint_url=S3_ENDPOINT  # Scaleway S3 endpoint
        )
        # Ajouter un préfixe si spécifié
        s3_key = f"{S3_PREFIX}/{file_name}" if S3_PREFIX else file_name
        s3.upload_file(file_path, S3_BUCKET, s3_key)
        print(f"Upload completed successfully: {s3_key}")
    except NoCredentialsError:
        print("Credentials not available for S3 upload.")
        exit(1)
    except Exception as e:
        print(f"Error during S3 upload: {e}")
        exit(1)

if __name__ == "__main__":
    backup_database()
    upload_to_s3()