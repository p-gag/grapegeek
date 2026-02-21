#!/bin/bash
# Quick setup script for existing GCP project
# Project: astral-oven-392317

set -e  # Exit on error

echo "🚀 Setting up GCS for GrapeGeek Photo Storage"
echo "=============================================="
echo ""

# Configuration
export PROJECT_ID="astral-oven-392317"
export BUCKET_NAME="grapegeek-data"
export REGION="us-central1"
export SERVICE_ACCOUNT_NAME="grapegeek-data-manager"

echo "📋 Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Bucket: $BUCKET_NAME"
echo "  Region: $REGION"
echo "  Service Account: $SERVICE_ACCOUNT_NAME"
echo ""

# Confirm project is set
echo "1️⃣  Setting active project..."
gcloud config set project $PROJECT_ID
echo "✅ Project set to: $(gcloud config get-value project)"
echo ""

# Create bucket
echo "2️⃣  Creating storage bucket..."
if gcloud storage buckets describe gs://$BUCKET_NAME &>/dev/null; then
    echo "⚠️  Bucket already exists: $BUCKET_NAME"
else
    gcloud storage buckets create gs://$BUCKET_NAME \
        --location=$REGION \
        --default-storage-class=STANDARD \
        --no-public-access-prevention
    echo "✅ Bucket created: $BUCKET_NAME"
fi
echo ""

# Make bucket public
echo "3️⃣  Making bucket publicly readable..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member=allUsers \
    --role=roles/storage.objectViewer
echo "✅ Bucket is now public"
echo ""

# Set CORS
echo "4️⃣  Setting CORS policy..."
cat > /tmp/cors.json <<'EOF'
[
  {
    "origin": ["https://grapegeek.com", "https://p-gag.github.io", "http://localhost:3000", "http://localhost:8000"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type", "Content-Length"],
    "maxAgeSeconds": 3600
  }
]
EOF
gcloud storage buckets update gs://$BUCKET_NAME --cors-file=/tmp/cors.json
rm /tmp/cors.json
echo "✅ CORS policy applied"
echo ""

# Create service account
echo "5️⃣  Creating service account..."
export SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL &>/dev/null; then
    echo "⚠️  Service account already exists: $SERVICE_ACCOUNT_EMAIL"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="GrapeGeek Photo Uploader" \
        --description="Service account for uploading VIVC photos to GCS"
    echo "✅ Service account created: $SERVICE_ACCOUNT_EMAIL"
fi
echo ""

# Grant permissions
echo "6️⃣  Granting bucket permissions to service account..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role=roles/storage.objectAdmin
echo "✅ Permissions granted"
echo ""

# Create .secrets directory
echo "7️⃣  Creating .secrets directory..."
mkdir -p .secrets
chmod 700 .secrets
echo "✅ .secrets directory ready"
echo ""

# Create credentials
echo "8️⃣  Creating service account key..."
CREDENTIALS_FILE=".secrets/gcs-credentials.json"
if [ -f "$CREDENTIALS_FILE" ]; then
    echo "⚠️  Credentials file already exists: $CREDENTIALS_FILE"
    echo "    To create a new key, delete the existing file first"
else
    gcloud iam service-accounts keys create "$CREDENTIALS_FILE" \
        --iam-account=$SERVICE_ACCOUNT_EMAIL
    chmod 600 "$CREDENTIALS_FILE"
    echo "✅ Credentials saved to: $CREDENTIALS_FILE"
fi
echo ""

# Update .env
echo "9️⃣  Updating .env file..."
if grep -q "GCS_BUCKET_NAME" .env 2>/dev/null; then
    echo "⚠️  GCS configuration already exists in .env"
else
    cat >> .env <<EOF

# Google Cloud Storage Configuration
GCS_BUCKET_NAME=${BUCKET_NAME}
GCS_CREDENTIALS_PATH=./.secrets/gcs-credentials.json
GCS_PROJECT_ID=${PROJECT_ID}
GCS_BASE_URL=https://storage.googleapis.com/${BUCKET_NAME}

# Asset paths (using bucket prefixes)
GCS_VARIETY_PHOTOS_PATH=photos/varieties
GCS_PRODUCER_PHOTOS_PATH=photos/producers
GCS_DOCUMENTS_PATH=documents
EOF
    echo "✅ Environment variables added to .env"
fi
echo ""

# Test upload
echo "🔟 Testing upload..."
echo "Test from GrapeGeek setup script" > /tmp/test-upload.txt
gcloud storage cp /tmp/test-upload.txt gs://$BUCKET_NAME/test/setup-test.txt
export TEST_URL="https://storage.googleapis.com/${BUCKET_NAME}/test/setup-test.txt"
echo "✅ Upload successful!"
echo ""

echo "1️⃣1️⃣ Testing public access..."
if curl -s -f "$TEST_URL" > /dev/null; then
    echo "✅ Public access working!"
    echo "   URL: $TEST_URL"
else
    echo "❌ Public access failed"
    exit 1
fi

# Cleanup test
gcloud storage rm gs://$BUCKET_NAME/test/setup-test.txt
rm /tmp/test-upload.txt
echo ""

# Summary
echo "=============================================="
echo "🎉 Setup Complete!"
echo "=============================================="
echo ""
echo "📦 Bucket: gs://$BUCKET_NAME"
echo "🔗 Base URL: https://storage.googleapis.com/${BUCKET_NAME}/"
echo "🔑 Credentials: gcs-credentials.json"
echo "📧 Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""
echo "Next steps:"
echo "1. Keep gcs-credentials.json secure (already in .gitignore)"
echo "2. Run: pip install google-cloud-storage"
echo "3. Test with Python: python test-gcs-upload.py"
echo "4. Proceed to Phase 2: Script development"
echo ""
