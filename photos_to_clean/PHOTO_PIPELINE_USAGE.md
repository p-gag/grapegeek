# 📸 Photo Pipeline Usage Guide

## Overview

The photo pipeline downloads grape variety photos from VIVC and uploads them to Google Cloud Storage, making them available for the website.

## Script: `08a_photo_sync_gcs.py`

**Purpose**: Sync VIVC photos to GCS and update `grape_variety_mapping.jsonl`

**When to run**: After VIVC consolidation (step 5), before database generation

**Rate limiting**: 3 seconds between VIVC requests (configurable, minimum 1 second)

---

## 🚀 Quick Start

### First Run (Recommended)

By default, the script processes only varieties missing photos and downloads only "Cluster in the field" photos:

```bash
# Dry run first to see what would happen
uv run src/08a_photo_sync_gcs.py --dry-run

# Actual run with limit (test with 5 varieties)
uv run src/08a_photo_sync_gcs.py --limit 5

# Full run (all varieties missing photos - default behavior)
uv run src/08a_photo_sync_gcs.py
```

### Test with Single Variety

```bash
# Test with L'Acadie Blanc (VIVC 17638)
uv run src/08a_photo_sync_gcs.py --vivc 17638 --dry-run
uv run src/08a_photo_sync_gcs.py --vivc 17638
```

---

## 📋 Command Reference

### Mode Selection

| Flag | Description | Use Case |
|------|-------------|----------|
| (none) | Process varieties without photos (default) | **Default** - safe, resumable |
| `--vivc 17638` | Process specific VIVC number | Testing, single variety |
| `--force` | Reprocess all varieties (including those with photos) | Force update existing photos |

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--photo-types "Type1,Type2"` | "Cluster in the field" | Filter photo types (comma-separated for multiple) |
| `--limit N` | No limit | Process only first N varieties |
| `--delay N` | 3.0 | Seconds between VIVC requests (min: 1.0) |
| `--dry-run` | False | Show what would be done without changes |

---

## 🎯 Usage Examples

### Conservative First Run

Default behavior - only download cluster photos for varieties missing photos:

```bash
uv run src/08a_photo_sync_gcs.py
```

**Why**:
- Only processes varieties that need photos (default)
- Focuses on most useful photo type (default: "Cluster in the field")
- Resumable if interrupted
- Conservative rate limiting protects VIVC

### Test Run

Test with 10 varieties:

```bash
uv run src/08a_photo_sync_gcs.py \
  \
  --photo-types "Cluster in the field" \
  --limit 10
```

### Dry Run

See what would be processed without downloading:

```bash
uv run src/08a_photo_sync_gcs.py \
  \
  --photo-types "Cluster in the field" \
  --dry-run
```

### Download Multiple Photo Types

Override default to download cluster and leaf photos:

```bash
uv run src/08a_photo_sync_gcs.py \
  --photo-types "Cluster in the field,Mature leaf"
```

### Faster Processing (Use Carefully!)

Reduce delay to 2 seconds (still respectful):

```bash
uv run src/08a_photo_sync_gcs.py \
  \
  --photo-types "Cluster in the field" \
  --delay 2.0
```

**Warning**: Don't go below 1.0 seconds. VIVC is not a high-performance server.

### Process Specific Variety

```bash
uv run src/08a_photo_sync_gcs.py --vivc 17638
```

### Reprocess All Varieties

**Warning**: This will re-download everything, even varieties with photos.

```bash
uv run src/08a_photo_sync_gcs.py \
  --force \
  --photo-types "Cluster in the field"
```

---

## 📊 Photo Types Available

Common VIVC photo types (use exact names):

- `"Cluster in the field"` ⭐ **Default** - Grape clusters in vineyard
- `"Mature leaf"` - Fully developed leaf samples
- `"Young leaf"` - Early-season leaf development
- `"Shoot tip"` - Growing shoot apex
- `"Bunch"` - Harvested grape bunches
- `"Berry"` - Individual berries

**Default**: The script defaults to `"Cluster in the field"` only. Use `--photo-types` to override.

---

## 🔄 Integration with Pipeline

### Full Pipeline Command Sequence

```bash
# 1. VIVC assignment
uv run src/04_vivc_assign.py

# 2. Consolidate duplicates
uv run src/includes/grape_varieties.py consolidate

# 3. Photo sync (NEW STEP - defaults to "Cluster in the field")
uv run src/08a_photo_sync_gcs.py

# 4. Generate final dataset
uv run src/05_data_final_normalized.py

# 5. Build database
uv run src/09_build_database.py

# 6. Generate outputs
uv run src/06_output_geojson.py
uv run src/07_generate_stats.py
```

### When to Run Photo Sync

**Always run after**:
- VIVC assignment (`04_vivc_assign.py`)
- VIVC consolidation (`grape_varieties.py consolidate`)

**Always run before**:
- Database generation (`09_build_database.py`)

**Why**: Photos must be synced after VIVC data is finalized but before the database is built, so photo URLs are included in the database.

---

## 📁 What Gets Updated

### `data/grape_variety_mapping.jsonl`

Photos are added to variety records:

```json
{
  "name": "L'ACADIE BLANC",
  "portfolio": {
    "grape": {
      "vivc_number": "17638"
    },
    "photos": [
      {
        "photo_type": "Cluster in the field",
        "filename": "cluster_in_the_field_17107.jpg",
        "local_path": "photos/varieties/vivc/17638/cluster_in_the_field_17107.jpg",
        "credits": "Ursula Brühl, Julius Kühn-Institut (JKI)...",
        "image_url": "https://storage.googleapis.com/grapegeek-data/photos/varieties/vivc/17638/cluster_in_the_field_17107.jpg",
        "download_url": "http://www.vivc.de/gbvp/17107.jpg"
      }
    ]
  }
}
```

### Google Cloud Storage

Photos uploaded to:

```
gs://grapegeek-data/photos/varieties/vivc/
├── 17638/
│   └── cluster_in_the_field_17107.jpg
├── 17639/
│   └── cluster_in_the_field_12345.jpg
└── ...
```

Public URLs:

```
https://storage.googleapis.com/grapegeek-data/photos/varieties/vivc/17638/cluster_in_the_field_17107.jpg
```

---

## ⚠️ Rate Limiting & VIVC Respect

### Why Rate Limiting Matters

VIVC is an academic database, not a commercial service. It's important to be respectful:

- **Default**: 3 seconds between photo page requests (configurable)
- **Additional**: 3 seconds delay in vivc_client for all HTTP requests
- **Photo downloads**: 2 seconds delay before each photo
- **Minimum**: 1 second (enforced)
- **Recommended**: Keep at default unless you have a good reason

### Retry Logic

The script automatically retries on failures:

- **504 Gateway Timeout**: Up to 3 retries with 10s/20s/30s backoff
- **Request Timeout**: Up to 3 retries with 10s/20s/30s backoff
- **Connection Errors**: Up to 3 retries with 10s/20s/30s backoff
- **Timeout Duration**: 60 seconds (VIVC can be very slow)

### Estimated Time

With default delays (3s + 3s per page request + 2s per photo):

- **10 varieties**: ~1-2 minutes
- **50 varieties**: ~8-10 minutes
- **100 varieties**: ~15-20 minutes
- **500 varieties**: ~90-120 minutes

**This is intentionally slow** to be respectful of VIVC's servers.

### If You Get Blocked

If you get repeated HTTP errors or timeouts:

1. **Wait**: The script automatically retries with backoff
2. **Increase delay**: Use `--delay 5.0` or higher if needed
3. **Take a break**: Wait 30 minutes if errors persist
4. **Resume**: Script is resumable (default behavior skips completed varieties)

---

## 🔍 Monitoring Progress

### Output Format

```
🍇 VIVC Photo Sync to GCS
======================================================================
Bucket: gs://grapegeek-data/
Photo prefix: photos/varieties/
Rate limit: 3.0s between requests
Photo types: Cluster in the field
======================================================================

Found 285 varieties to process

[1/285]
======================================================================
Processing: L'ACADIE BLANC (VIVC 17638)
======================================================================
   Fetching photo page from VIVC...
   Waiting 3.0s before VIVC request...
   Found 1 photo(s) matching filters:
      - Cluster in the field

   Processing: Cluster in the field
   ✅ Uploaded to GCS: photos/varieties/vivc/17638/cluster_in_the_field_17107.jpg (1818801 bytes)
   ✅ Added photo to variety: https://storage.googleapis.com/grapegeek-data/photos/varieties/vivc/17638/cluster_in_the_field_17107.jpg

[2/285]
...
```

### Statistics Summary

At the end:

```
======================================================================
📊 Statistics
======================================================================
Varieties processed: 285
Varieties skipped: 15
Photos downloaded: 285
Photos uploaded: 285
Errors: 0
======================================================================
```

---

## 🐛 Troubleshooting

### "google-cloud-storage not installed"

```bash
uv pip install google-cloud-storage
```

### "Credentials file not found"

Check your `.env` file:

```bash
cat .env | grep GCS_CREDENTIALS_PATH
```

Verify file exists:

```bash
ls -la ~/.gcp/grapegeek-credentials.json
```

### "Error fetching photo page: Timeout"

VIVC is slow or overloaded. Increase delay:

```bash
uv run src/08a_photo_sync_gcs.py \
  \
  --photo-types "Cluster in the field" \
  --delay 5.0
```

### "Error uploading to GCS"

Test GCS connection:

```bash
uv run infrastructure/gcp/test-connection.py
```

Check bucket permissions:

```bash
gcloud storage buckets describe gs://grapegeek-data
```

### Script Interrupted

Simply re-run the command (default behavior resumes automatically):

```bash
uv run src/08a_photo_sync_gcs.py \
  --photo-types "Cluster in the field"
```

The script will skip varieties that already have photos by default.

---

## 📈 Best Practices

### 1. Start Small

```bash
# Test with 5 varieties
uv run src/08a_photo_sync_gcs.py \
  \
  --photo-types "Cluster in the field" \
  --limit 5
```

### 2. Use Dry Run

```bash
# See what would happen
uv run src/08a_photo_sync_gcs.py --dry-run
```

### 3. Run During Off-Hours

VIVC may be more responsive during European night hours (US daytime).

### 4. Be Patient

Don't reduce `--delay` below 3 seconds unless necessary.

### 5. Resume-Friendly

Default behavior skips varieties with photos, so you can always resume if interrupted.

### 6. Monitor Errors

If you see many errors, stop and investigate before continuing.

---

## 🎓 Advanced Usage

### Custom GCS Path

Edit `.env`:

```bash
GCS_VARIETY_PHOTOS_PATH=photos/varieties-custom
```

### Process Without Filters

Download all photo types:

```bash
uv run src/08a_photo_sync_gcs.py --missing-only
```

### Batch Processing

Process in batches of 50:

```bash
# Batch 1
uv run src/08a_photo_sync_gcs.py --limit 50

# Batch 2 (automatically skips first 50)
uv run src/08a_photo_sync_gcs.py --limit 50

# Continue...
```

---

## 📝 Notes

### Photo Credits

All VIVC photos are credited to:

> Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY

Credits are automatically included in the photo metadata.

### Photo Quality

- Photos are downloaded in full resolution from VIVC
- Original VIVC URLs are preserved in `download_url` field
- GCS URLs are used as primary `image_url`

### Storage Costs

With ~500 varieties × 1 photo × 200KB average:

- Storage: ~100MB = ~$0.002/month
- Bandwidth: ~1GB/month = ~$0.12/month

**Total cost**: ~$0.13/month (negligible)

---

## ✅ Checklist

Before running photo sync:

- [ ] GCP setup complete (`infrastructure/gcp/test-connection.py` passes)
- [ ] VIVC assignment complete (`04_vivc_assign.py`)
- [ ] VIVC consolidation complete (`grape_varieties.py consolidate`)
- [ ] `.env` configured with GCS variables
- [ ] `google-cloud-storage` installed
- [ ] Tested with `--dry-run`
- [ ] Tested with `--limit 5`

After running photo sync:

- [ ] Check statistics (errors should be 0 or minimal)
- [ ] Verify photos in GCS: `gcloud storage ls gs://grapegeek-data/photos/varieties/vivc/`
- [ ] Verify URLs work: Open a sample URL in browser
- [ ] Continue pipeline: Run `05_data_final_normalized.py`

---

## 🆘 Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Run with `--dry-run` to diagnose
3. Test GCS connection: `python infrastructure/gcp/test-connection.py`
4. Check VIVC is accessible: `curl -I https://www.vivc.de/`
5. Review error messages carefully

**Remember**: The script is designed to be safe, resumable, and respectful of VIVC's resources.
