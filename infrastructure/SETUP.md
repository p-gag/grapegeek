# GCP First-Time Setup

One-time setup to connect to the existing `grapegeek-data` GCP bucket.

## Prerequisites

- Google account with access to project `astral-oven-392317`
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed

## Steps

```bash
# 1. Authenticate
gcloud auth login
gcloud config set project astral-oven-392317

# 2. Run setup script (creates ~/.gcp/ and downloads service account key)
bash infrastructure/gcp/setup-home-directory.sh

# 3. Set environment variables (add to ~/.zshrc or ~/.bashrc)
export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/grapegeek-credentials.json
export GCS_BUCKET_NAME=grapegeek-data

# 4. Verify connection
python infrastructure/gcp/test-connection.py
```

## Troubleshooting

- **Permission denied**: Ensure `~/.gcp/grapegeek-credentials.json` permissions are `600`
- **Bucket not found**: Confirm `GOOGLE_APPLICATION_CREDENTIALS` is set in your shell
- **Auth error**: Re-run `gcloud auth login` and check project is `astral-oven-392317`

See `infrastructure/GCP.md` for operational reference.
