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
from google.cloud import storage

logger = logging.getLogger(__name__)

def upload_to_gcs(file_path, bucket_name, content_type=None):
    """
    Upload a file to Google Cloud Storage.
    
    Args:
        file_path: Path to the file to upload
        bucket_name: GCS bucket name
        content_type: MIME type of the file (optional)
    
    Returns:
        str: Public URL of the uploaded file
    """
    try:
        # Create a storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Create a blob with the filename
        filename = os.path.basename(file_path)
        blob = bucket.blob(filename)
        
        # Set content type if provided
        if content_type:
            blob.content_type = content_type
            logger.info(f"Uploading {file_path} to GCS with Content-Type: {content_type}")
        else:
            logger.info(f"Uploading {file_path} to GCS (Content-Type not specified, GCS will guess)")
        
        # Upload the file
        blob.upload_from_filename(file_path)
        
        # Make the blob publicly accessible
        blob.make_public()
        
        logger.info(f"File uploaded successfully to GCS: {blob.public_url}")
        return blob.public_url
        
    except Exception as e:
        logger.error(f"Error uploading file to GCS: {e}")
        raise
