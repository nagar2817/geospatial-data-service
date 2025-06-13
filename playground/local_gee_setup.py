# gee_local.py

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import ee
from google.auth import aws
from google.auth.transport.requests import Request

def load_env(env_path: str = "./app/.env"):
    """Load environment variables from .env file."""
    if Path(env_path).exists():
        load_dotenv(env_path)
    else:
        raise FileNotFoundError(f"{env_path} not found.")

def get_config():
    """Fetch config values from environment."""
    config = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not config:
        raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS is not set.")
    if not project:
        raise EnvironmentError("GOOGLE_CLOUD_PROJECT is not set.")
    print(f"Using config: {config}, project: {project}")
    return config, project

def get_wif_credentials(config_path: str):
    """Create and refresh WIF credentials."""
    with open(config_path) as f:
        info = json.load(f)
    creds = aws.Credentials.from_info(
        info,
        scopes=["https://www.googleapis.com/auth/earthengine"]
    )
    creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError("Failed to refresh WIF credentials.")
    return creds

def init_earthengine(creds, project: str):
    """Initialize Earth Engine with given credentials."""
    ee.Initialize(credentials=creds, project=project)
    print(f"✅ Earth Engine initialized with project '{project}'")

def main():
    load_env()
    config_path, project = get_config()
    creds = get_wif_credentials(config_path)
    init_earthengine(creds, project)

if __name__ == "__main__":
    main()


# aws sts assume-role \
#   --role-arn arn:aws:iam::585768148346:role/gcp-wif-access-role \
#   --role-session-name localGeeSession