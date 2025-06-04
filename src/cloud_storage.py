# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import logging
import mimetypes
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from typing import Optional

logger = logging.getLogger(__name__)

class CloudStorageProvider(ABC):
    """Abstract base class for cloud storage providers."""
    
    @abstractmethod
    def upload_file(self, file_path: str, content_type: Optional[str] = None) -> str:
        """Upload a file and return the public URL."""
        pass

class GCPStorageProvider(CloudStorageProvider):
    """Google Cloud Storage provider."""
    
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name

    def upload_file(self, file_path: str, content_type: Optional[str] = None) -> str:
        from .gcp_toolkit import upload_to_gcs
        return upload_to_gcs(file_path, self.bucket_name, content_type=content_type)

class S3CompatibleProvider(CloudStorageProvider):
    """S3-compatible storage provider (including MinIO)."""
    
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str, 
                 bucket_name: str, region: str):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.region = region
        
        # Check if endpoint is Digital Ocean and extract bucket/region if missing
        if (self.endpoint_url and 
            'digitalocean' in self.endpoint_url.lower() and 
            (not self.bucket_name or not self.region)):
            
            logger.info("Digital Ocean endpoint detected with missing bucket or region. Extracting from URL.")
            try:
                parsed_url = urlparse(self.endpoint_url)
                if parsed_url.hostname:
                    hostname_parts = parsed_url.hostname.split('.')
                    
                    if not self.bucket_name and len(hostname_parts) > 0:
                        self.bucket_name = hostname_parts[0]
                        logger.info(f"Extracted bucket name from URL: {self.bucket_name}")
                    
                    if not self.region and len(hostname_parts) > 1:
                        self.region = hostname_parts[1]
                        logger.info(f"Extracted region from URL: {self.region}")
                
            except Exception as e:
                logger.warning(f"Failed to parse Digital Ocean URL: {e}. Using provided values.")

    def upload_file(self, file_path: str, content_type: Optional[str] = None) -> str:
        from .s3_toolkit import upload_to_s3
        return upload_to_s3(
            file_path, 
            self.endpoint_url, 
            self.access_key, 
            self.secret_key, 
            self.bucket_name, 
            self.region, 
            content_type=content_type
        )

def validate_env_vars(provider: str) -> None:
    """Validate the necessary environment variables for the selected storage provider."""
    required_vars = {
        'GCP': ['GCP_BUCKET_NAME', 'GCP_SA_CREDENTIALS'],
        'S3': ['S3_ENDPOINT_URL', 'S3_ACCESS_KEY', 'S3_SECRET_KEY', 'S3_BUCKET_NAME', 'S3_REGION'],
        'S3_DO': ['S3_ENDPOINT_URL', 'S3_ACCESS_KEY', 'S3_SECRET_KEY']
    }
    
    missing_vars = [var for var in required_vars[provider] if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing environment variables for {provider} storage: {', '.join(missing_vars)}")

def get_storage_provider() -> CloudStorageProvider:
    """Get the appropriate storage provider based on environment variables."""
    
    # Check for S3-compatible storage first
    s3_endpoint = os.getenv('S3_ENDPOINT_URL')
    if s3_endpoint:
        if 'digitalocean' in s3_endpoint.lower():
            validate_env_vars('S3_DO')
        else:
            validate_env_vars('S3')
        
        return S3CompatibleProvider(
            endpoint_url=s3_endpoint,
            access_key=os.getenv('S3_ACCESS_KEY', ''),
            secret_key=os.getenv('S3_SECRET_KEY', ''),
            bucket_name=os.getenv('S3_BUCKET_NAME', ''),
            region=os.getenv('S3_REGION', '')
        )
    
    # Check for GCP storage
    gcp_bucket = os.getenv('GCP_BUCKET_NAME')
    if gcp_bucket:
        validate_env_vars('GCP')
        return GCPStorageProvider(bucket_name=gcp_bucket)
    
    # Check for legacy bucket_name (backward compatibility)
    legacy_bucket = os.getenv('BUCKET_NAME')
    if legacy_bucket:
        logger.info("Using legacy BUCKET_NAME for GCP storage. Please migrate to GCP_BUCKET_NAME.")
        return GCPStorageProvider(bucket_name=legacy_bucket)
    
    raise ValueError("No cloud storage settings provided. Please configure either S3 or GCP storage.")

def upload_file(file_path: str) -> str:
    """Upload a file to the configured cloud storage and return the public URL."""
    provider = get_storage_provider()
    
    try:
        # Guess MIME type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        logger.info(f"Uploading file to cloud storage: {file_path} with Content-Type: {content_type}")
        url = provider.upload_file(file_path, content_type=content_type)
        logger.info(f"File uploaded successfully: {url}")
        return url
        
    except Exception as e:
        logger.error(f"Error uploading file to cloud storage: {e}")
        raise
