from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Security
    api_key: Optional[str] = None
    
    # Legacy GCP bucket name (for backward compatibility)
    bucket_name: Optional[str] = None
    
    # GCP Storage settings
    gcp_bucket_name: Optional[str] = None
    gcp_sa_credentials: Optional[str] = None
    
    # S3-compatible storage settings (including MinIO)
    s3_endpoint_url: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    s3_region: Optional[str] = None

settings = Settings()
