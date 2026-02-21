# GCP Reference

Operational reference for the GrapeGeek Google Cloud infrastructure.

## Resources

| Resource | Value |
|---|---|
| Project | `astral-oven-392317` |
| Bucket | `grapegeek-data` (us-central1) |
| Service Account | `grapegeek-data-manager` |
| Credentials | `~/.gcp/grapegeek-credentials.json` |
| Public base URL | `https://storage.googleapis.com/grapegeek-data/` |
| Cost | ~$5/month |

## Bucket Structure

```
gs://grapegeek-data/
├── photos/varieties/vivc/      # VIVC grape photos (by VIVC number)
├── photos/varieties/custom/    # Custom variety photos
├── photos/producers/           # Producer photos by region
├── documents/                  # PDFs, research
└── exports/                    # Generated data exports
```

## Environment Variables

```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/grapegeek-credentials.json
export GCS_BUCKET_NAME=grapegeek-data
```

## Key Commands

```bash
# List photos
gsutil ls gs://grapegeek-data/photos/varieties/vivc/

# Upload a file
gsutil cp photo.jpg gs://grapegeek-data/photos/varieties/vivc/

# Sync photos
uv run src/08a_photo_sync_gcs.py

# Test connection
python infrastructure/gcp/test-connection.py
```

## Security

- Credentials stored outside project at `~/.gcp/grapegeek-credentials.json` (never commit)
- `~/.gcp/` permissions: `700` (directory), `600` (key file)
- Rotate keys quarterly via GCP Console → IAM → Service Accounts
- If credentials leak: revoke immediately in GCP Console, generate new key, update local file

## First-Time Setup

See `infrastructure/SETUP.md`.
