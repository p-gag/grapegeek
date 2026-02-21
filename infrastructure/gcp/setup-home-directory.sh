#!/bin/bash
# Setup script using HOME directory for credentials
# More secure - credentials outside project directory

set -e  # Exit on error

echo "🚀 Setting up GCS with Home Directory Credentials"
echo "================================================="
echo ""

# Configuration
export PROJECT_ID="astral-oven-392317"
export BUCKET_NAME="grapegeek-data"
export REGION="us-central1"
export SERVICE_ACCOUNT_NAME="grapegeek-data-manager"
export GCP_CONFIG_DIR="$HOME/.gcp"
export CREDENTIALS_FILE="$GCP_CONFIG_DIR/grapegeek-credentials.json"

echo "📋 Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Bucket: $BUCKET_NAME"
echo "  Credentials: $CREDENTIALS_FILE"
echo ""

# Create GCP config directory in home
echo "1️⃣  Creating ~/.gcp directory..."
mkdir -p "$GCP_CONFIG_DIR"
chmod 700 "$GCP_CONFIG_DIR"
echo "✅ Created: $GCP_CONFIG_DIR"
echo ""

# Confirm project is set
echo "2️⃣  Setting active project..."
gcloud config set project $PROJECT_ID
echo "✅ Project set to: $(gcloud config get-value project)"
echo ""

# Create bucket
echo "3️⃣  Creating storage bucket..."
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
echo "4️⃣  Making bucket publicly readable..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member=allUsers \
    --role=roles/storage.objectViewer
echo "✅ Bucket is now public"
echo ""

# Set CORS
echo "5️⃣  Setting CORS policy..."
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
echo "6️⃣  Creating service account..."
export SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL &>/dev/null; then
    echo "⚠️  Service account already exists: $SERVICE_ACCOUNT_EMAIL"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="GrapeGeek Data Manager" \
        --description="Service account for managing GrapeGeek data in GCS"
    echo "✅ Service account created: $SERVICE_ACCOUNT_EMAIL"
fi
echo ""

# Grant permissions
echo "7️⃣  Granting bucket permissions to service account..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role=roles/storage.objectAdmin
echo "✅ Permissions granted"
echo ""

# Create credentials in home directory
echo "8️⃣  Creating service account key in home directory..."
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
    echo "    Manually update GCS_CREDENTIALS_PATH if needed:"
    echo "    GCS_CREDENTIALS_PATH=$CREDENTIALS_FILE"
else
    cat >> .env <<EOF

# Google Cloud Storage Configuration
GCS_BUCKET_NAME=${BUCKET_NAME}
GCS_CREDENTIALS_PATH=$CREDENTIALS_FILE
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
echo "🔑 Credentials: $CREDENTIALS_FILE"
echo "📧 Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""
echo "✅ Credentials are stored in your home directory"
echo "   They are outside the project and can't be accidentally committed!"
echo ""
echo "Next steps:"
echo "1. Credentials are in: $GCP_CONFIG_DIR/"
echo "2. Run: pip install google-cloud-storage"
echo "3. Test with Python: python test-gcs-upload.py"
echo "4. Your .env file references the home directory path"
echo ""
