#!/usr/bin/env python3
"""Test script for extracting photo credits from VIVC foto2 modals.

This demonstrates the solution for extracting photo credits:
1. Parse photoviewresult page to find photo IDs from onclick handlers
2. Fetch foto2 modal URL for each photo: index.php?r=datasheet/foto2&id={photo_id}&kennnr={vivc_id}
3. Extract credit text from the modal HTML

When VIVC is responsive, this will extract the actual photo credits shown in the modal popup.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from includes.vivc_client import (
    extract_photo_ids_from_photoview,
    extract_photo_credits,
    get_photo_credit_for_variety
)

def test_photo_credit_extraction():
    """Test photo credit extraction with various examples."""

    test_cases = [
        ("17638", "L'ACADIE BLANC", "Should have JKI credits"),
        ("23382", "Petite Pearl", "Should have Tom Plocher external credits"),
        ("15904", "Seyval Blanc", "Should have JKI or external credits"),
    ]

    print("\n" + "=" * 80)
    print("PHOTO CREDIT EXTRACTION TEST")
    print("=" * 80)
    print("\nThis test demonstrates extracting photo credits from VIVC foto2 modals.")
    print("The credits are in JavaScript-loaded modal popups, not static HTML.")
    print("\nSolution:")
    print("  1. Parse photoviewresult page for photo IDs from onclick handlers")
    print("  2. Fetch foto2 modal: index.php?r=datasheet/foto2&id={photo_id}&kennnr={vivc_id}")
    print("  3. Extract credit text from modal HTML")
    print("\n" + "=" * 80 + "\n")

    for vivc_number, variety_name, expected in test_cases:
        print(f"\n{'=' * 80}")
        print(f"Testing: {variety_name} (VIVC {vivc_number})")
        print(f"Expected: {expected}")
        print("=" * 80)

        # Step 1: Get photo IDs
        print(f"\nStep 1: Extracting photo IDs from photoviewresult page...")
        photos = extract_photo_ids_from_photoview(vivc_number)

        if not photos:
            print(f"  ⚠️  No photos found (VIVC may be down or variety has no photos)")
            continue

        print(f"  ✅ Found {len(photos)} photo(s):")
        for photo_id, photo_type, photo_url in photos:
            print(f"     - Photo {photo_id}: {photo_type}")
            print(f"       URL: {photo_url}")

        # Step 2: Get credits for first photo
        print(f"\nStep 2: Fetching foto2 modal for first photo...")
        photo_id, photo_type, photo_url = photos[0]

        credit_text = extract_photo_credits(vivc_number, photo_id, delay=3.0)

        if credit_text:
            print(f"  ✅ Extracted credit:")
            print(f"     {credit_text}")
        else:
            print(f"  ⚠️  No credit text found (parsing may need adjustment)")

    # Test convenience function
    print(f"\n\n{'=' * 80}")
    print("CONVENIENCE FUNCTION TEST: get_photo_credit_for_variety()")
    print("=" * 80)

    vivc_number = "17638"
    print(f"\nGetting credit for VIVC {vivc_number} (L'ACADIE BLANC)...")
    credit = get_photo_credit_for_variety(vivc_number, delay=3.0)

    if credit:
        print(f"  ✅ Credit: {credit}")
    else:
        print(f"  ⚠️  No credit found")

    print("\n" + "=" * 80)
    print("Test complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_photo_credit_extraction()
