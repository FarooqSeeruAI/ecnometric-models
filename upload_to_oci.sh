#!/bin/bash
# Script to upload files to OCI instance
# Run this from your local machine

set -e

# Configuration - UPDATE THESE VALUES
OCI_USER="ubuntu"
OCI_HOST=""  # Will be provided
OCI_KEY=""   # Path to SSH private key
REMOTE_DIR="~/ecnometric-models"

echo "=========================================="
echo "Upload CGE Model to OCI Instance"
echo "=========================================="

# Check if SSH key is provided
if [ -z "$OCI_KEY" ] || [ ! -f "$OCI_KEY" ]; then
    echo "Error: SSH key not found or not specified"
    echo "Usage: OCI_HOST=<ip> OCI_KEY=<path_to_key> ./upload_to_oci.sh"
    exit 1
fi

# Check if host is provided
if [ -z "$OCI_HOST" ]; then
    echo "Error: OCI_HOST not specified"
    echo "Usage: OCI_HOST=<ip> OCI_KEY=<path_to_key> ./upload_to_oci.sh"
    exit 1
fi

echo "Uploading to: $OCI_USER@$OCI_HOST"
echo "Using key: $OCI_KEY"
echo ""

# Create remote directory
echo "Creating remote directory..."
ssh -i "$OCI_KEY" "$OCI_USER@$OCI_HOST" "mkdir -p $REMOTE_DIR"

# Upload files (excluding large files and outputs)
echo "Uploading files..."
rsync -avz --progress \
    -e "ssh -i $OCI_KEY" \
    --exclude='outputs/' \
    --exclude='temp_closures/' \
    --exclude='*.xlsx' \
    --exclude='*.xls' \
    --exclude='*.xlsm' \
    --exclude='__pycache__/' \
    --exclude='.git/' \
    --exclude='database/' \
    --exclude='.DS_Store' \
    ./ \
    "$OCI_USER@$OCI_HOST:$REMOTE_DIR/"

echo ""
echo "=========================================="
echo "Upload completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. SSH into the instance:"
echo "   ssh -i $OCI_KEY $OCI_USER@$OCI_HOST"
echo ""
echo "2. Navigate to directory:"
echo "   cd $REMOTE_DIR"
echo ""
echo "3. Run deployment:"
echo "   chmod +x deploy_oci.sh"
echo "   ./deploy_oci.sh"
echo ""
