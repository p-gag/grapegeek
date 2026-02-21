#!/usr/bin/env python3
"""Fetch and display photo credits for specific varieties."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

from includes.vivc_client import extract_photo_ids_from_photoview, extract_photo_credits
import time

varieties = [
    ("17638", "L'ACADIE BLANC"),
    ("23382", "Petite Pearl"),
]

print("\n" + "=" * 80)
print("FETCHING PHOTO CREDITS FROM VIVC")
print("=" * 80)

for vivc_num, name in varieties:
    print(f"\n{'=' * 80}")
    print(f"{name} (VIVC {vivc_num})")
    print("=" * 80)

    try:
        # Get photo IDs
        print("  → Getting photo list...")
        photos = extract_photo_ids_from_photoview(vivc_num)

        if not photos:
            print("  ❌ No photos found")
            continue

        photo_id, photo_type, photo_url = photos[0]
        print(f"  ✅ Found photo {photo_id} ({photo_type})")

        # Get credits
        print("  → Fetching foto2 modal for credits...")
        time.sleep(2)
        photo_credit = extract_photo_credits(vivc_num, photo_id, delay=3.0)

        if photo_credit:
            print("\n  ✅ PHOTO CREDIT EXTRACTED:")
            print(f"\n  📋 Note:")
            print(f"     {photo_credit.note}")
            print(f"\n  👤 Credit:")
            print(f"     {photo_credit.credit}")
        else:
            print("  ⚠️  Could not extract credit text")

    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\n{'=' * 80}")
print("✅ Results cached to: data/vivc_cache.jsonl")
print("=" * 80 + "\n")
