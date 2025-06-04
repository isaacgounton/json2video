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
import boto3
import logging
from urllib.parse import urlparse, quote

logger = logging.getLogger(__name__)

def upload_to_s3(file_path, s3_url, access_key, secret_key, bucket_name, region, content_type=None):
    """
    Upload a file to S3-compatible storage (including MinIO).
    
    Args:
        file_path: Path to the file to upload
        s3_url: S3 endpoint URL
        access_key: S3 access key
        secret_key: S3 secret key
        bucket_name: S3 bucket name
        region: S3 region
        content_type: MIME type of the file (optional)
    
    Returns:
        str: Public URL of the uploaded file
    """
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    
    client = session.client('s3', endpoint_url=s3_url)

    extra_args = {'ACL': 'public-read'}
    if content_type:
        extra_args['ContentType'] = content_type
        logger.info(f"Uploading {file_path} to S3 with Content-Type: {content_type}")
    else:
        logger.info(f"Uploading {file_path} to S3 (Content-Type not specified, S3 will guess or default)")

    try:
        # Upload the file to the specified S3 bucket
        with open(file_path, 'rb') as data:
            client.upload_fileobj(data, bucket_name, os.path.basename(file_path), ExtraArgs=extra_args)

        # URL encode the filename for the URL
        encoded_filename = quote(os.path.basename(file_path))
        file_url = f"{s3_url}/{bucket_name}/{encoded_filename}"
        return file_url
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise
