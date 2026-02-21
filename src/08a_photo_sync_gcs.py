#!/usr/bin/env python3
"""
VIVC Photo Sync to GCS

Downloads grape variety photos from VIVC and uploads to Google Cloud Storage.
Updates grape_variety_mapping.jsonl with GCS URLs.

This script runs AFTER VIVC consolidation and BEFORE database generation.

USAGE:
# Dry run - see what would be processed
uv run src/08a_photo_sync_gcs.py --dry-run

# Default: process varieties missing photos, "Cluster in the field" photos only
uv run src/08a_photo_sync_gcs.py

# Process specific VIVC number
uv run src/08a_photo_sync_gcs.py --vivc 17638

# Force reprocess all varieties (including those with photos)
uv run src/08a_photo_sync_gcs.py --force

# Stop after finding photos for 10 varieties (for testing)
uv run src/08a_photo_sync_gcs.py --limit 10

# Download multiple photo types
uv run src/08a_photo_sync_gcs.py --photo-types "Cluster in the field,Mature leaf"

RATE LIMITING & RETRY LOGIC:
- Default: 60 seconds delay before each VIVC page request (very conservative)
- Additional 3 seconds delay in vivc_client for all HTTP requests (if not cached)
- 2 seconds delay before each photo download
- Automatic retry on 504 Gateway Timeout (up to 3 attempts with 10s/20s/30s backoff)
- Automatic retry on request timeout (up to 3 attempts with 10s/20s/30s backoff)
- 60 second timeout for all requests (VIVC can be very slow)
- Use --delay to adjust pre-request delay (minimum 1 second, e.g., --delay 30 for 30s)
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Optional, Set
import tempfile

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Import modules
sys.path.insert(0, str(Path(__file__).parent))
from includes.grape_varieties import GrapeVarietiesModel, PhotoInfo
from includes.vivc_client import fetch_url, extract_photo_ids_from_photoview, extract_photo_credits

# Try to import Google Cloud Storage
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False


class VIVCPhotoSyncGCS:
    """Sync VIVC photos to Google Cloud Storage."""

    # Allowed photo credits - exact string match required
    # All JKI/VIVC credits are allowed (public institution photos)
    ALLOWED_CREDITS = {
        # JKI/VIVC - Doris Schneider (125 varieties)
        "Doris Schneider, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY",

        # JKI/VIVC - Ursula Brühl (108 varieties)
        "Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY",

        # JKI/VIVC - Both Doris & Ursula (69 varieties)
        "Doris Schneider, Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY",

        # JKI/VIVC - No photographer name (16 varieties)
        "Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY",

        # JKI/VIVC - Ursula Brühl (alternative format) (12 varieties)
        "Ursula Brühl, Julius Kühn-Institut (JKI) Bundesforschungsinstitut für Kulturpflanzen Institut für Rebenzüchtung Geilweilerhof - 76833 Siebeldingen - GERMANY",

        # Tom Plocher - External source with permission (4 varieties)
        "Tom Plocher, Plocher-Vines LLC, 9040 152nd Street N., Hugo, MN 55038, USA",
    }

    def __init__(
        self,
        bucket_name: str,
        credentials_path: str,
        base_url: str,
        photo_prefix: str = "photos/varieties",
        delay_seconds: float = 60.0,
        dry_run: bool = False,
        photo_types: Optional[List[str]] = None
    ):
        self.bucket_name = bucket_name
        self.credentials_path = os.path.expanduser(credentials_path)
        self.base_url = base_url.rstrip('/')
        self.photo_prefix = photo_prefix.strip('/')
        self.delay_seconds = max(1.0, delay_seconds)  # Minimum 1 second
        self.dry_run = dry_run
        # Default to "Cluster in the field" if no photo types specified
        self.photo_types_filter = set(photo_types) if photo_types else {"Cluster in the field"}

        # Load grape varieties model
        self.grape_model = GrapeVarietiesModel()

        # Initialize GCS client
        self.gcs_client = None
        self.gcs_bucket = None
        if not dry_run:
            self._init_gcs()

        # Statistics
        self.stats = {
            'varieties_processed': 0,
            'varieties_skipped': 0,
            'photos_downloaded': 0,
            'photos_uploaded': 0,
            'photos_skipped': 0,
            'errors': 0
        }

    def _init_gcs(self):
        """Initialize Google Cloud Storage client."""
        if not GCS_AVAILABLE:
            raise ImportError(
                "google-cloud-storage not installed. "
                "Run: pip install google-cloud-storage"
            )

        if not Path(self.credentials_path).exists():
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_path}"
            )

        # Set credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path

        # Initialize client
        self.gcs_client = storage.Client()
        self.gcs_bucket = self.gcs_client.bucket(self.bucket_name)

        print(f"✅ GCS client initialized: gs://{self.bucket_name}/")

    def fetch_photo_page(self, vivc_number: str) -> str:
        """Fetch photo page from VIVC (uses cache when available)."""
        photo_url = f"https://www.vivc.de/index.php?r=passport/photoviewresult&id={vivc_number}"

        # vivc_client will check cache first, then delay only if not cached
        return fetch_url(photo_url, delay=self.delay_seconds)

    def _get_photo_credit(self, vivc_number: str, debug: bool = False) -> tuple[Optional[str], str]:
        """Get photo credit from foto2 modal.

        Returns: (credit_text, classification)
            credit_text: The actual credit string from foto2 modal
            classification: "ALLOWED" or "EXTERNAL_UNKNOWN" or "NOT_FOUND"
        """
        try:
            # Get photo IDs from the photoviewresult page (cached)
            photos = extract_photo_ids_from_photoview(vivc_number)

            if not photos:
                if debug:
                    print(f"   🔍 Debug: No photos found in photoviewresult page")
                return (None, "NOT_FOUND")

            # Get credit for first photo (cached foto2 modal)
            photo_id, _, _ = photos[0]
            if debug:
                print(f"   🔍 Debug: Fetching foto2 modal for photo {photo_id}")

            photo_credit = extract_photo_credits(vivc_number, photo_id, delay=self.delay_seconds)

            if not photo_credit:
                if debug:
                    print(f"   🔍 Debug: extract_photo_credits returned None")
                return (None, "NOT_FOUND")

            if not photo_credit.credit:
                if debug:
                    print(f"   🔍 Debug: PhotoCredit object has no credit text")
                return (None, "NOT_FOUND")

            credit_text = photo_credit.credit
            if debug:
                print(f"   🔍 Debug: Extracted credit: {credit_text[:80]}...")

            # Check if credit is in allowed set (exact match)
            if credit_text in self.ALLOWED_CREDITS:
                return (credit_text, "ALLOWED")

            # Unknown external source - needs investigation!
            return (credit_text, "EXTERNAL_UNKNOWN")

        except Exception as e:
            print(f"   ⚠️  Error fetching photo credit: {e}")
            if debug:
                import traceback
                traceback.print_exc()
            return (None, "NOT_FOUND")

    def extract_photos_from_page(
        self,
        html_content: str,
        vivc_number: str,
        apply_filter: bool = True,
        credit_text: Optional[str] = None
    ) -> List[PhotoInfo]:
        """Extract photo information from VIVC photo page.

        Args:
            html_content: HTML content of the photo page
            vivc_number: VIVC number of the variety
            apply_filter: If True, filter by photo_types_filter. If False, return all photos.
            credit_text: Pre-fetched credit text to use for all photos
        """
        photos = []

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            panels = soup.find_all('div', class_='panel2 panel-default')

            for panel in panels:
                panel_title = panel.find('h4', class_='panel-title')
                if not panel_title:
                    continue

                # Extract photo type
                title_text = panel_title.get_text()
                category_match = re.search(r'Category:\s*(.+)', title_text, re.IGNORECASE)
                if not category_match:
                    continue

                photo_type = category_match.group(1).strip()

                # Filter by photo type if specified and apply_filter is True
                if apply_filter and self.photo_types_filter and photo_type not in self.photo_types_filter:
                    continue

                # Find image
                img = panel.find('img')
                if not img or not img.get('src'):
                    continue

                image_url = img.get('src')
                original_filename = image_url.split('/')[-1]

                if not original_filename:
                    continue

                # Create GCS path: photos/varieties/vivc/17638/cluster_17107.jpg
                safe_type = re.sub(r'[^a-zA-Z0-9]', '_', photo_type).lower()
                photo_id = original_filename.replace('k.jpg', '').replace('.jpg', '')
                gcs_filename = f"{safe_type}_{photo_id}.jpg"
                gcs_path = f"{self.photo_prefix}/vivc/{vivc_number}/{gcs_filename}"

                # Full-size download URL
                download_url = image_url.replace('k.jpg', '.jpg') if image_url.endswith('k.jpg') else image_url

                # Use provided credit text or fallback
                credits = credit_text if credit_text else "Photo credit information not available"

                photo = PhotoInfo(
                    photo_type=photo_type,
                    filename=gcs_filename,
                    local_path=gcs_path,  # This will be GCS path now
                    credits=credits,
                    image_url=image_url,
                    download_url=download_url
                )

                photos.append(photo)

        except Exception as e:
            print(f"   ⚠️  Error parsing HTML for VIVC {vivc_number}: {e}")

        return photos

    def download_photo(self, photo: PhotoInfo, max_retries: int = 3) -> Optional[bytes]:
        """Download photo from VIVC with retry logic."""
        if self.dry_run:
            print(f"   DRY RUN: Would download {photo.download_url}")
            return b"fake_photo_data"

        # Add delay before photo download to respect VIVC
        time.sleep(2)

        for attempt in range(max_retries):
            try:
                response = requests.get(photo.download_url, timeout=60)
                response.raise_for_status()
                return response.content

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    print(f"   ⚠️  Timeout downloading photo, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    print(f"   ❌ Timeout downloading after {max_retries} attempts: {photo.download_url}")
                    return None
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    print(f"   ⚠️  Error downloading photo: {e}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    print(f"   ❌ Error downloading after {max_retries} attempts: {photo.download_url}: {e}")
                    return None

        return None

    def upload_to_gcs(
        self,
        photo_data: bytes,
        gcs_path: str,
        content_type: str = "image/jpeg"
    ) -> bool:
        """Upload photo to Google Cloud Storage."""
        if self.dry_run:
            print(f"   DRY RUN: Would upload to gs://{self.bucket_name}/{gcs_path}")
            return True

        try:
            blob = self.gcs_bucket.blob(gcs_path)

            # Check if already exists
            if blob.exists():
                print(f"   ⏭️  Already in GCS: {gcs_path}")
                return True

            # Upload
            blob.upload_from_string(photo_data, content_type=content_type)
            print(f"   ✅ Uploaded to GCS: {gcs_path} ({len(photo_data)} bytes)")
            return True

        except Exception as e:
            print(f"   ❌ Error uploading to GCS: {e}")
            return False

    def get_gcs_url(self, gcs_path: str) -> str:
        """Get public GCS URL for a path."""
        return f"{self.base_url}/{gcs_path}"

    def process_variety(self, variety_name: str, vivc_number: str) -> int:
        """Process photos for a single variety. Returns number of photos added."""
        print(f"\n{'='*70}")
        print(f"Processing: {variety_name} (VIVC {vivc_number})")
        print(f"{'='*70}")

        variety = self.grape_model.get_variety(variety_name)
        if not variety:
            print(f"   ⚠️  Variety not found in model: {variety_name}")
            self.stats['errors'] += 1
            return 0

        # Fetch photo page from VIVC
        print(f"   Fetching photo page from VIVC...")
        html_content = self.fetch_photo_page(vivc_number)

        if html_content.startswith("❌"):
            print(f"   ❌ Error fetching photo page: {html_content}")
            self.stats['errors'] += 1
            return 0

        # Get photo credit from foto2 modal (uses cache)
        print(f"   Checking photo credits...")
        credit_text, classification = self._get_photo_credit(vivc_number, debug=False)

        if classification == "EXTERNAL_UNKNOWN":
            print(f"\n{'#' * 80}")
            print(f"{'#' * 80}")
            print(f"##  ⚠️  WARNING: UNKNOWN EXTERNAL PHOTO SOURCE")
            print(f"##")
            print(f"##  Variety: {variety_name} (VIVC {vivc_number})")
            print(f"##  Credit: {credit_text}")
            print(f"##")
            print(f"##  ❌ THIS PHOTO CREDIT IS NOT IN THE ALLOWED LIST!")
            print(f"##  ❌ CANNOT USE THIS PHOTO WITHOUT PERMISSION!")
            print(f"##")
            print(f"##  Action needed:")
            print(f"##  1. Verify usage rights with the source")
            print(f"##  2. If allowed, add to ALLOWED_CREDITS in this script")
            print(f"##  3. Re-run to process this variety")
            print(f"{'#' * 80}")
            print(f"{'#' * 80}\n")
            self.stats['varieties_skipped'] += 1
            return 0

        if classification == "NOT_FOUND":
            # Check if it's because there are no photos or extraction failed
            from includes.vivc_client import extract_photo_ids_from_photoview
            photos_check = extract_photo_ids_from_photoview(vivc_number)

            if not photos_check:
                print(f"   ℹ️  No photos available on VIVC for this variety")
            else:
                print(f"   ⚠️  Could not extract photo credit from foto2 modal")
                print(f"   ⚠️  (foto2 may not be cached - run analyze_photo_credit_distribution.py)")

            print(f"   ⚠️  Skipping for safety (cannot verify usage rights)")
            self.stats['varieties_skipped'] += 1
            return 0

        # Classification is "ALLOWED" - proceed with downloading
        print(f"   ✅ Photo credit verified as allowed")
        print(f"   Credit: {credit_text[:80]}...")

        # Extract filtered photos
        photos = self.extract_photos_from_page(html_content, vivc_number, apply_filter=True, credit_text=credit_text)

        if not photos:
            # No matching photos - check if there are ANY photos available
            all_photos = self.extract_photos_from_page(html_content, vivc_number, apply_filter=False, credit_text=credit_text)
            if all_photos:
                available_types = [p.photo_type for p in all_photos]
                print(f"   ℹ️  No matching photos found. Available types: {', '.join(available_types)}")
            else:
                print(f"   ℹ️  No photos found for this variety")
            self.stats['varieties_skipped'] += 1
            return 0

        print(f"   Found {len(photos)} photo(s) matching filters:")
        for photo in photos:
            print(f"      - {photo.photo_type}")

        # Process each photo
        photos_added = 0
        for photo in photos:
            print(f"\n   Processing: {photo.photo_type}")

            gcs_path = photo.local_path  # This is GCS path
            gcs_url = self.get_gcs_url(gcs_path)

            # Check if photo already exists in GCS
            photo_exists = False
            if not self.dry_run and self.gcs_bucket:
                blob = self.gcs_bucket.blob(gcs_path)
                photo_exists = blob.exists()

            if photo_exists:
                print(f"   ✅ Photo already in GCS, updating credit only")
                # Don't download - just update the variety with new credit
                photo_with_gcs = PhotoInfo(
                    photo_type=photo.photo_type,
                    filename=photo.filename,
                    local_path=gcs_path,
                    credits=photo.credits,
                    image_url=gcs_url,
                    download_url=photo.download_url
                )
                variety.add_photo(photo_with_gcs)
                photos_added += 1
                print(f"   ✅ Updated credit: {photo.credits[:60]}...")
            else:
                # Download photo
                photo_data = self.download_photo(photo)
                if not photo_data:
                    self.stats['errors'] += 1
                    continue

                self.stats['photos_downloaded'] += 1

                # Upload to GCS
                if self.upload_to_gcs(photo_data, gcs_path):
                    self.stats['photos_uploaded'] += 1

                    # Create photo info with GCS URL
                    photo_with_gcs = PhotoInfo(
                        photo_type=photo.photo_type,
                        filename=photo.filename,
                        local_path=gcs_path,
                        credits=photo.credits,
                        image_url=gcs_url,  # Use GCS URL as main URL
                        download_url=photo.download_url  # Keep original VIVC URL
                    )

                    # Add to variety
                    variety.add_photo(photo_with_gcs)
                    photos_added += 1
                    print(f"   ✅ Added photo to variety: {gcs_url}")
                else:
                    self.stats['errors'] += 1

        if photos_added > 0:
            self.stats['varieties_processed'] += 1

            # Save immediately after each variety with photos (crash-safe)
            if not self.dry_run:
                print(f"\n   💾 Saving progress to grape_variety_mapping.jsonl...")
                self.grape_model.save_jsonl()
                print(f"   ✅ Saved!")

        return photos_added

    def run(
        self,
        vivc_number: Optional[str] = None,
        all_varieties: bool = False,
        missing_only: bool = False,
        limit: Optional[int] = None
    ):
        """Run photo sync process."""
        print(f"\n🍇 VIVC Photo Sync to GCS")
        print(f"{'='*70}")
        print(f"Bucket: gs://{self.bucket_name}/")
        print(f"Photo prefix: {self.photo_prefix}/")
        print(f"Rate limit: {self.delay_seconds}s between requests")
        print(f"Photo types: {', '.join(self.photo_types_filter)}")
        if missing_only:
            print(f"Mode: Skip varieties with photos (default)")
        else:
            print(f"Mode: Force reprocess all varieties")
        if self.dry_run:
            print(f"⚠️  DRY RUN MODE - No downloads or uploads")

        # Check if foto2 modals are cached
        from includes.vivc_client import _cache
        cache_file = Path("data/vivc_cache.jsonl")
        if cache_file.exists():
            # Count foto2 URLs in cache
            foto2_count = 0
            try:
                with open(cache_file, 'r') as f:
                    for line in f:
                        if 'foto2' in line:
                            foto2_count += 1
            except:
                pass

            if foto2_count == 0:
                print(f"\n⚠️  WARNING: No foto2 modals found in cache!")
                print(f"⚠️  Run analyze_photo_credit_distribution.py first to cache credits")
                print(f"⚠️  Otherwise all varieties will be skipped (cannot verify credits)")
            else:
                print(f"✅ Found {foto2_count} foto2 modals in cache")

        print(f"{'='*70}\n")

        # Collect varieties to process
        varieties_to_process = []

        if vivc_number:
            # Process specific VIVC number
            for variety in self.grape_model.get_all_varieties():
                if variety.get_vivc_number() == vivc_number:
                    varieties_to_process.append((variety.name, vivc_number))
                    break

            if not varieties_to_process:
                print(f"❌ No variety found with VIVC number {vivc_number}")
                return

        else:
            # Process all varieties (default behavior)
            for variety in self.grape_model.get_all_varieties():
                vivc_num = variety.get_vivc_number()
                if not vivc_num:
                    continue

                # Skip if missing_only and variety already has photos
                if missing_only and variety.has_photos():
                    continue

                varieties_to_process.append((variety.name, vivc_num))

        # Don't apply limit upfront - we'll stop when we've found enough varieties WITH photos
        print(f"Found {len(varieties_to_process)} varieties to process")
        if limit and limit > 0:
            print(f"Limit: Will stop after finding photos for {limit} varieties\n")
        else:
            print()

        if not varieties_to_process:
            print("✅ No varieties to process")
            return

        # Process varieties - stop when limit is reached for varieties WITH photos
        varieties_with_photos = 0
        for i, (variety_name, vivc_num) in enumerate(varieties_to_process, 1):
            # Check if we've reached the limit (only count varieties with photos)
            if limit and limit > 0 and varieties_with_photos >= limit:
                print(f"\n✅ Reached limit of {limit} varieties with photos found. Stopping.")
                break

            print(f"\n[{i}/{len(varieties_to_process)}]")
            photos_added = self.process_variety(variety_name, vivc_num)

            # Count this variety if we found and added photos
            if photos_added > 0:
                varieties_with_photos += 1

        # Progress was saved after each variety (no final save needed)
        if not self.dry_run and self.stats['varieties_processed'] > 0:
            print(f"\n{'='*70}")
            print(f"✅ All changes saved incrementally (crash-safe)")

        # Print statistics
        print(f"\n{'='*70}")
        print("📊 Statistics")
        print(f"{'='*70}")
        print(f"Varieties processed: {self.stats['varieties_processed']}")
        print(f"Varieties skipped: {self.stats['varieties_skipped']}")
        print(f"Photos downloaded: {self.stats['photos_downloaded']}")
        print(f"Photos uploaded: {self.stats['photos_uploaded']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"{'='*70}\n")

        if self.dry_run:
            print("⚠️  DRY RUN - No changes made")
        else:
            print("✅ Photo sync complete!")


def analyze_credits(delay: float = 60.0):
    """Analyze breeder/credit distribution across all varieties.

    This will fetch passport pages with delays and cache them for future use.
    """
    from collections import Counter
    from includes.vivc_client import fetch_url, _cache

    print(f"\n📊 Analyzing Photo Credits Distribution")
    print("=" * 70)

    # Load grape varieties
    grape_model = GrapeVarietiesModel()
    all_varieties = grape_model.get_all_varieties()

    # Filter to varieties with VIVC numbers
    varieties_with_vivc = [
        (v.name, v.get_vivc_number())
        for v in all_varieties
        if v.get_vivc_number()
    ]

    print(f"\nFound {len(varieties_with_vivc)} varieties with VIVC numbers")
    print(f"Delay between requests: {delay}s (will be cached for future use)")

    # Check how many are already cached
    cached_count = 0
    for _, vivc_number in varieties_with_vivc:
        passport_url = f"https://www.vivc.de/index.php?r=passport/view&id={vivc_number}"
        if _cache.get(passport_url):
            cached_count += 1

    print(f"Already cached: {cached_count}/{len(varieties_with_vivc)}")
    print(f"Need to fetch: {len(varieties_with_vivc) - cached_count}")

    if cached_count < len(varieties_with_vivc):
        print(f"\n⏳ This will take ~{int((len(varieties_with_vivc) - cached_count) * delay / 60)} minutes...")
    print()

    breeder_counts = Counter()
    varieties_by_breeder = {}
    jki_indicators = ['julius', 'kühn', 'jki', 'brühl', 'geilweilerhof']

    for i, (variety_name, vivc_number) in enumerate(varieties_with_vivc, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(varieties_with_vivc)} ({i*100//len(varieties_with_vivc)}%)")

        passport_url = f"https://www.vivc.de/index.php?r=passport/view&id={vivc_number}"

        # Check if cached
        is_cached = _cache.get(passport_url) is not None

        # Fetch (will use cache if available, or fetch with delay and cache)
        passport_html = fetch_url(passport_url, delay=delay)

        if passport_html.startswith("❌"):
            continue

        try:
            soup = BeautifulSoup(passport_html, 'html.parser')
            breeder_row = soup.find('th', string=re.compile(r'^\s*Breeder\s*$', re.IGNORECASE))

            if breeder_row:
                breeder_td = breeder_row.find_next('td')
                if breeder_td:
                    breeder_link = breeder_td.find('a')
                    if breeder_link:
                        breeder_name = breeder_link.get_text().strip()
                    else:
                        breeder_name = breeder_td.get_text().strip()

                    # Categorize
                    is_jki = any(indicator in breeder_name.lower() for indicator in jki_indicators)

                    if is_jki:
                        category = "JKI/VIVC"
                    elif breeder_name and len(breeder_name) > 3:
                        category = breeder_name
                    else:
                        category = "Unknown/No breeder"

                    breeder_counts[category] += 1

                    if category not in varieties_by_breeder:
                        varieties_by_breeder[category] = []
                    varieties_by_breeder[category].append((variety_name, vivc_number))

        except Exception as e:
            continue

    # Print results
    print(f"\n{'=' * 70}")
    print(f"📊 RESULTS: Photo Credit Distribution")
    print(f"{'=' * 70}\n")

    total = sum(breeder_counts.values())

    print(f"Total varieties analyzed: {total}\n")
    print(f"{'Breeder/Source':<40} {'Count':>10} {'%':>8}")
    print("-" * 70)

    for breeder, count in breeder_counts.most_common():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"{breeder:<40} {count:>10} {percentage:>7.1f}%")

    # Show non-JKI varieties (potential external photos)
    print(f"\n{'=' * 70}")
    print(f"⚠️  NON-JKI BREEDERS (Potential External Photos)")
    print(f"{'=' * 70}\n")

    for breeder, varieties in sorted(varieties_by_breeder.items()):
        if breeder != "JKI/VIVC" and breeder != "Unknown/No breeder":
            print(f"\n{breeder} ({len(varieties)} varieties):")
            for variety_name, vivc_num in varieties[:5]:  # Show first 5
                print(f"  - {variety_name} (VIVC {vivc_num})")
            if len(varieties) > 5:
                print(f"  ... and {len(varieties) - 5} more")

    print(f"\n{'=' * 70}")


def debug_photo_html(vivc_number: str):
    """Debug function to examine photo and passport page HTML structure."""
    from includes.vivc_client import fetch_url

    print(f"\n🔍 Debugging HTML for VIVC {vivc_number}")
    print("=" * 70)

    # Check photo page
    print("\n📷 PHOTO PAGE:")
    print("-" * 70)
    photo_url = f"https://www.vivc.de/index.php?r=passport/photoviewresult&id={vivc_number}"
    photo_html = fetch_url(photo_url, delay=1.0)

    if photo_html.startswith("❌"):
        print(f"Error fetching photo page: {photo_html}")
    else:
        soup = BeautifulSoup(photo_html, 'html.parser')
        panels = soup.find_all('div', class_='panel2 panel-default')
        print(f"Found {len(panels)} photo panel(s)")

        for i, panel in enumerate(panels, 1):
            title = panel.find('h4', class_='panel-title')
            if title:
                print(f"  Panel {i}: {title.get_text().strip()}")

    # Check passport page for breeder info
    print("\n📋 PASSPORT PAGE (Breeder Info):")
    print("-" * 70)
    passport_url = f"https://www.vivc.de/index.php?r=passport/view&id={vivc_number}"
    passport_html = fetch_url(passport_url, delay=1.0)

    if passport_html.startswith("❌"):
        print(f"Error fetching passport page: {passport_html}")
    else:
        soup = BeautifulSoup(passport_html, 'html.parser')

        # Look for breeder information
        breeder_row = soup.find('th', string=re.compile('Breeder', re.IGNORECASE))
        if breeder_row:
            breeder_td = breeder_row.find_next('td')
            if breeder_td:
                breeder = breeder_td.get_text().strip()
                print(f"  Breeder: {breeder}")

        # Look for breeder contact
        contact_row = soup.find('th', string=re.compile('Breeder contact', re.IGNORECASE))
        if contact_row:
            contact_td = contact_row.find_next('td')
            if contact_td:
                contact = contact_td.get_text().strip()
                print(f"  Contact: {contact}")

        # Search for any permission/credit notices
        text = soup.get_text()
        if 'permission' in text.lower() or 'reproduction' in text.lower():
            print("\n  ⚠️  Found permission/reproduction keywords in passport page")
            # Extract relevant sections
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if 'permission' in line.lower() or 'reproduction' in line.lower():
                    context = '\n'.join(lines[max(0, i-2):min(len(lines), i+3)])
                    print(f"\n  Context:\n{context[:300]}")
                    break

    print("\n" + "=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync VIVC photos to Google Cloud Storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Mode selection
    parser.add_argument(
        '--vivc',
        type=str,
        help='Process specific VIVC number'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reprocess all varieties (including those with photos)'
    )
    parser.add_argument(
        '--debug-html',
        action='store_true',
        help='Debug mode: Show HTML structure for photo page'
    )
    parser.add_argument(
        '--analyze-credits',
        action='store_true',
        help='Analyze breeder distribution across all varieties (uses cache)'
    )

    # Options
    parser.add_argument(
        '--limit',
        type=int,
        help='Stop after finding photos for N varieties (skips varieties with no photos)'
    )
    parser.add_argument(
        '--photo-types',
        type=str,
        help='Comma-separated list of photo types to download (default: "Cluster in the field")'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=60.0,
        help='Seconds to wait between VIVC requests (default: 60.0 = 1 minute, minimum: 1.0)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Handle analysis mode
    if args.analyze_credits:
        delay = args.delay if hasattr(args, 'delay') else 60.0
        analyze_credits(delay=delay)
        return

    # Handle debug mode
    if args.debug_html:
        if not args.vivc:
            print("❌ --debug-html requires --vivc parameter")
            sys.exit(1)
        debug_photo_html(args.vivc)
        return

    # Load environment
    load_dotenv()

    # Get GCS configuration
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    credentials_path = os.getenv('GCS_CREDENTIALS_PATH')
    base_url = os.getenv('GCS_BASE_URL')
    photo_prefix = os.getenv('GCS_VARIETY_PHOTOS_PATH', 'photos/varieties')

    if not all([bucket_name, credentials_path, base_url]):
        print("❌ Missing GCS configuration in .env file")
        print("   Required: GCS_BUCKET_NAME, GCS_CREDENTIALS_PATH, GCS_BASE_URL")
        sys.exit(1)

    # Parse photo types
    photo_types = None
    if args.photo_types:
        photo_types = [pt.strip() for pt in args.photo_types.split(',')]

    try:
        # Initialize sync
        sync = VIVCPhotoSyncGCS(
            bucket_name=bucket_name,
            credentials_path=credentials_path,
            base_url=base_url,
            photo_prefix=photo_prefix,
            delay_seconds=args.delay,
            dry_run=args.dry_run,
            photo_types=photo_types
        )

        # Run sync
        # Default: skip varieties with photos (missing_only=True)
        # Use --force to reprocess all varieties
        sync.run(
            vivc_number=args.vivc,
            all_varieties=True,
            missing_only=not args.force,  # Default is True unless --force
            limit=args.limit
        )

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if not args.dry_run:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
