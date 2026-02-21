# VIVC Photo Credits - Technical Notes

## Key Discovery: Credits in JavaScript-Loaded Modals

Photo credits are **NOT in static HTML** - they're loaded dynamically via JavaScript when clicking photos.

**Discovery process:**
1. Initial attempts failed looking at passport pages (only has breeder info, not photo credits)
2. Found credits are in modal popups shown on photo click
3. Reverse-engineered `showFoto2()` JavaScript function in `/js/main.js`
4. Discovered AJAX endpoint: `index.php?r=datasheet/foto2&id={photo_id}&kennnr={vivc_id}`

**Solution:**
- Parse photoviewresult page for photo IDs from `onclick="showFoto2(photo_id, vivc_id)"`
- Fetch foto2 modal URL to get credit HTML
- Extract credit text from modal content
- All cached in `data/vivc_cache.jsonl` for instant reuse

## All 6 Allowed Credit Formats

**JKI/VIVC (330 varieties total):**
```
1. Doris Schneider (125 varieties)
"Doris Schneider, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY"

2. Ursula Brühl (108 varieties)
"Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY"

3. Both photographers (69 varieties)
"Doris Schneider, Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY"

4. No photographer (16 varieties)
"Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY"

5. Alternate format (12 varieties)
"Ursula Brühl, Julius Kühn-Institut (JKI) Bundesforschungsinstitut für Kulturpflanzen Institut für Rebenzüchtung Geilweilerhof - 76833 Siebeldingen - GERMANY"
```

**External with Permission (4 varieties):**
```
6. Tom Plocher
"Tom Plocher, Plocher-Vines LLC, 9040 152nd Street N., Hugo, MN 55038, USA"

Varieties: Crimson Pearl, Petite Pearl, Véritage TP1-1-12, Verona
Note: For reproduction of external photos, contact source for permission
```

## Critical Code Changes Made

**1. `src/includes/grape_varieties.py` - add_photo()**
- Changed from "skip if exists" to "update if exists"
- Prevents duplicate photos when reprocessing
- Updates credits for existing photos

**2. `src/includes/vivc_client.py` - Progressive delays**
- Added exponential backoff: 10s → 20s → 40s (was linear)
- Progressive timeout: 60s → 90s → 120s
- Only delays on non-cached requests

**3. `analyze_photo_credit_distribution.py` - Performance**
- Removed `time.sleep(2)` between varieties
- Was 11 minutes with cache, now instant
- fetch_url() already handles delays for non-cached

**4. `src/08a_photo_sync_gcs.py` - Photo sync**
- Checks GCS before downloading (reuses existing photos)
- Updates credits even if photo already uploaded
- Exact string matching against ALLOWED_CREDITS set
- Very visible warnings for unknown external sources

## Common Pitfalls

**Breeder ≠ Photo Credits**
- Breeder: Person who created the variety (on passport page)
- Photo credit: Photographer who took the photo (in foto2 modal)
- These are often different people!

**~27% of varieties have no photos**
- 334 varieties with photos / 581 total ≈ 57%
- This is normal - not all varieties are photographed
- Script correctly skips these

**Must use --force to update existing**
- Default: skip varieties that already have photos
- `--force`: reprocess all varieties (updates credits)
- Photos already in GCS are not re-downloaded

**Dry run doesn't save**
- `--dry-run` shows what would happen
- Must run without it to actually update grape_variety_mapping.jsonl

## Files Modified

**Production:**
- `src/08a_photo_sync_gcs.py` - Main photo sync (NEW)
- `src/includes/vivc_client.py` - Added foto2 extraction
- `src/includes/grape_varieties.py` - Updated add_photo()
- `analyze_photo_credit_distribution.py` - Credit analysis (NEW)
- `data/vivc_cache.jsonl` - 334 foto2 modals cached
- `data/grape_variety_mapping.jsonl` - Updated with correct credits

**Documentation:**
- `CLAUDE.md` - VIVC Photo Pipeline section
- `tests/integration/photo/INTEGRATION_TEST_PLAN.md` - Future test plan

**Old scripts (keep for now, superseded by 08a):**
- `src/add_photo_to_variety.py`
- `src/vivc_photo_downloader.py`
- `src/vivc_photo_manager.py`

## Usage Quick Reference

```bash
# Analyze credit distribution (first time)
python analyze_photo_credit_distribution.py

# Sync photos with verified credits
uv run src/08a_photo_sync_gcs.py --force

# Test with specific variety
uv run src/08a_photo_sync_gcs.py --vivc 17638

# Dry run (preview only)
uv run src/08a_photo_sync_gcs.py --force --dry-run
```
