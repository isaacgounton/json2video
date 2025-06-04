# Cloud Storage Implementation for JSON2Video

This document describes the cloud storage implementation added to the json2video service, supporting both Google Cloud Storage and S3-compatible storage (including MinIO).

## Overview

The json2video service now supports multiple cloud storage backends:

1. **Google Cloud Platform (GCP) Storage** - Original implementation
2. **S3-Compatible Storage** - New implementation supporting:
   - Amazon S3
   - MinIO
   - DigitalOcean Spaces
   - Any S3-compatible storage service

## Architecture

### Files Added/Modified

1. **`src/cloud_storage.py`** - Main abstraction layer for cloud storage
2. **`src/s3_toolkit.py`** - S3-compatible storage implementation
3. **`src/gcp_toolkit.py`** - Google Cloud Storage implementation
4. **`settings.py`** - Updated to support both storage types
5. **`main.py`** - Updated to use the new cloud storage system
6. **`requirements.txt`** - Added boto3 dependency for S3 support
7. **`.env.example`** - Configuration examples for both storage types

### Class Structure

```
CloudStorageProvider (ABC)
├── GCPStorageProvider
└── S3CompatibleProvider
```

## Configuration

### Environment Variables

The service automatically detects which storage provider to use based on available environment variables:

#### S3-Compatible Storage (Priority 1)
```bash
S3_ENDPOINT_URL=https://your-s3-endpoint.com
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket-name
S3_REGION=your-region
```

#### Google Cloud Storage (Priority 2)
```bash
GCP_BUCKET_NAME=your-gcp-bucket-name
GCP_SA_CREDENTIALS=/path/to/service-account-key.json
```

#### Legacy Support (Priority 3)
```bash
BUCKET_NAME=your-legacy-bucket-name  # Uses GCP
```

### Provider Selection Logic

1. If `S3_ENDPOINT_URL` is set → Use S3-compatible storage
2. Else if `GCP_BUCKET_NAME` is set → Use GCP storage
3. Else if `BUCKET_NAME` is set → Use GCP storage (legacy)
4. Else → Throw configuration error

## Usage Examples

### MinIO Configuration
```bash
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=videos
S3_REGION=us-east-1
```

### DigitalOcean Spaces Configuration
```bash
S3_ENDPOINT_URL=https://your-space-name.nyc3.digitaloceanspaces.com
S3_ACCESS_KEY=your-do-spaces-key
S3_SECRET_KEY=your-do-spaces-secret
# Note: Bucket name and region are auto-extracted from URL for DO
```

### AWS S3 Configuration
```bash
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=your-aws-access-key
S3_SECRET_KEY=your-aws-secret-key
S3_BUCKET_NAME=your-s3-bucket
S3_REGION=us-west-2
```

### Google Cloud Storage Configuration
```bash
GCP_BUCKET_NAME=your-gcp-bucket-name
GCP_SA_CREDENTIALS=/path/to/service-account-key.json
```

## Features

### Automatic MIME Type Detection
The system automatically detects and sets appropriate MIME types for uploaded files using Python's `mimetypes` module.

### DigitalOcean Spaces Auto-Configuration
For DigitalOcean Spaces, the bucket name and region can be automatically extracted from the endpoint URL if not explicitly provided.

### Backward Compatibility
The implementation maintains backward compatibility with the original GCP-only configuration.

### Error Handling
Comprehensive error handling and logging for debugging storage issues.

### Public URL Generation
Both providers generate public URLs for uploaded files with proper URL encoding.

## API Changes

The `/render` endpoint now:
1. Creates the video file
2. Uploads it to the configured cloud storage
3. Returns the public URL
4. Cleans up the temporary file

## Dependencies

- `boto3>=1.35.94` - For S3-compatible storage
- `google-cloud-storage>=3.1.0` - For GCP storage (existing)

## Migration Guide

### From GCP-only to Multi-provider

1. **No changes required for existing GCP deployments** - they will continue to work
2. **To migrate to S3-compatible storage**:
   - Add S3 environment variables
   - Remove or comment out GCP variables
   - Restart the service

### Environment Variable Migration
```bash
# Old (still supported)
BUCKET_NAME=my-bucket

# New GCP format
GCP_BUCKET_NAME=my-bucket
GCP_SA_CREDENTIALS=/path/to/key.json

# New S3 format
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=access_key
S3_SECRET_KEY=secret_key
S3_BUCKET_NAME=videos
S3_REGION=us-east-1
```

## Testing

To test the implementation:

1. **Set up your storage provider** (MinIO, S3, or GCP)
2. **Configure environment variables**
3. **Test the `/render` endpoint**
4. **Verify file upload and URL generation**

## Security Considerations

- Store credentials securely (use secrets management)
- Ensure bucket permissions are properly configured
- Use HTTPS endpoints when possible
- Consider implementing signed URLs for additional security

## Troubleshooting

### Common Issues

1. **"No cloud storage settings provided"**
   - Ensure at least one set of storage credentials is configured

2. **S3 connection errors**
   - Verify endpoint URL, credentials, and network connectivity
   - Check bucket exists and permissions are correct

3. **GCP authentication errors**
   - Verify service account key path and permissions
   - Ensure bucket exists and service account has access

### Logging

The implementation provides detailed logging at INFO level for successful operations and ERROR level for failures.
