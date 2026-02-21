#!/usr/bin/env python3
"""Analyze photo credit distribution across all grape varieties.

Fetches photo credits from VIVC foto2 modals and analyzes the distribution
to understand how many are JKI internal vs external sources.
"""

import sys
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path.cwd() / "src"))

from includes.grape_varieties import GrapeVarietiesModel
from includes.vivc_client import (
    extract_photo_ids_from_photoview,
    extract_photo_credits,
    PhotoCredit
)
import time

def classify_credit(photo_credit: PhotoCredit) -> str:
    """Classify a photo credit as JKI or external source.

    Returns:
        Category string: 'JKI', external source name, or 'Unknown'
    """
    if not photo_credit or not photo_credit.credit:
        return "Unknown"

    credit_text = photo_credit.credit.lower()

    # JKI indicators
    jki_indicators = ['julius kühn', 'jki', 'brühl', 'geilweilerhof', 'siebeldingen']
    if any(indicator in credit_text for indicator in jki_indicators):
        return "JKI/VIVC"

    # External sources - try to extract organization name
    credit_parts = photo_credit.credit.split(',')
    if len(credit_parts) >= 2:
        # Usually: "Name, Organization/Location"
        # Return the first substantial part (name or org)
        for part in credit_parts[:2]:
            part_clean = part.strip()
            if len(part_clean) > 3:
                return part_clean

    return photo_credit.credit[:50]  # Truncate for display


def main():
    print("\n" + "=" * 80)
    print("PHOTO CREDIT DISTRIBUTION ANALYSIS")
    print("=" * 80)
    print("\nExtracting photo credits from VIVC foto2 modals for all varieties...")
    print("Results are cached - subsequent runs will be much faster.")
    print("=" * 80)

    # Load varieties
    grape_model = GrapeVarietiesModel()
    varieties_with_vivc = [
        (v.name, v.get_vivc_number())
        for v in grape_model.get_all_varieties()
        if v.get_vivc_number()
    ]

    print(f"\nTotal varieties with VIVC numbers: {len(varieties_with_vivc)}")

    # Track results
    credit_counts = Counter()
    varieties_by_category: Dict[str, List[Tuple[str, str, PhotoCredit]]] = {}
    failed_varieties = []
    no_photo_varieties = []

    # Tracking counters
    total_processed = 0
    with_photos = 0
    succeeded = 0

    # Recent errors for debugging
    recent_errors = []

    print("\nStarting analysis...")
    print("(Using progressive delays and exponential backoff for timeouts)\n")

    for i, (variety_name, vivc_number) in enumerate(varieties_with_vivc, 1):
        total_processed += 1

        if i % 50 == 0 or i == 10:  # Show progress at 10 and every 50
            print(f"\n{'='*80}")
            print(f"Progress: {i}/{len(varieties_with_vivc)} ({i*100//len(varieties_with_vivc)}%)")
            print(f"  ✅ Credits extracted: {succeeded}")
            print(f"  📷 Varieties with photos: {with_photos}")
            print(f"  ⭕ No photos found: {len(no_photo_varieties)}")
            print(f"  ❌ Failed to extract: {len(failed_varieties)}")
            if with_photos > 0:
                print(f"  📊 Extraction success rate: {succeeded}/{with_photos} ({succeeded*100//with_photos}%)")
            if recent_errors:
                print(f"\n  Last 3 errors:")
                for err in recent_errors[-3:]:
                    print(f"    • {err}")
            print("="*80)

        try:
            # Get photo IDs
            photos = extract_photo_ids_from_photoview(vivc_number)

            if not photos:
                no_photo_varieties.append((variety_name, vivc_number))
                if i <= 20:  # Show details for first 20
                    print(f"  ⭕ {variety_name} (VIVC {vivc_number}): No photos")
                continue

            with_photos += 1

            # Get credits for first photo
            photo_id, photo_type, _ = photos[0]

            # No delay needed - fetch_url handles delays for non-cached requests
            photo_credit = extract_photo_credits(vivc_number, photo_id, delay=3.0)

            if photo_credit:
                succeeded += 1
                category = classify_credit(photo_credit)
                credit_counts[category] += 1

                if category not in varieties_by_category:
                    varieties_by_category[category] = []
                varieties_by_category[category].append((variety_name, vivc_number, photo_credit))

                if i <= 20:  # Show details for first 20
                    print(f"  ✅ {variety_name} (VIVC {vivc_number}): {category}")
            else:
                error_msg = f"{variety_name} (VIVC {vivc_number}): Could not extract credit from HTML"
                failed_varieties.append((variety_name, vivc_number, "Could not extract credit from HTML"))
                recent_errors.append(error_msg)
                if i <= 20:  # Show details for first 20
                    print(f"  ❌ {error_msg}")

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user. Showing results so far...\n")
            break
        except Exception as e:
            error_msg = f"{variety_name} (VIVC {vivc_number}): {str(e)}"
            failed_varieties.append((variety_name, vivc_number, str(e)))
            recent_errors.append(error_msg)
            if i <= 20:  # Show details for first 20
                print(f"  ❌ {error_msg}")

    # Results
    print("\n\n" + "=" * 80)
    print("📊 DISTRIBUTION RESULTS")
    print("=" * 80)

    total_analyzed = sum(credit_counts.values())
    print(f"\nTotal varieties processed: {total_processed}")
    print(f"  ├─ Varieties with photos: {with_photos}")
    print(f"  │   ├─ ✅ Credits extracted: {succeeded}")
    print(f"  │   └─ ❌ Failed to extract: {len(failed_varieties)}")
    print(f"  └─ ⭕ No photos found: {len(no_photo_varieties)}")
    if with_photos > 0:
        print(f"\nExtraction success rate: {succeeded}/{with_photos} ({succeeded*100//with_photos}%)")
        print("  (Success = extracted credit from foto2 modal for varieties with photos)")

    print("\n" + "-" * 80)
    print(f"{'Credit Source':<50} {'Count':>10} {'%':>8}")
    print("-" * 80)

    for source, count in credit_counts.most_common():
        percentage = (count / total_analyzed * 100) if total_analyzed > 0 else 0
        print(f"{source:<50} {count:>10} {percentage:>7.1f}%")

    # Detailed external sources
    print("\n" + "=" * 80)
    print("🌍 EXTERNAL PHOTO SOURCES (Non-JKI)")
    print("=" * 80)

    external_categories = [cat for cat in varieties_by_category.keys() if cat != "JKI/VIVC" and cat != "Unknown"]

    if external_categories:
        for category in sorted(external_categories):
            varieties = varieties_by_category[category]
            print(f"\n{category} ({len(varieties)} varieties):")
            for variety_name, vivc_num, photo_credit in varieties[:5]:
                print(f"  • {variety_name} (VIVC {vivc_num})")
                print(f"    Note: {photo_credit.note[:80]}...")
                print(f"    Credit: {photo_credit.credit[:80]}...")
            if len(varieties) > 5:
                print(f"  ... and {len(varieties) - 5} more")
    else:
        print("\nNo external sources found (all credits are JKI/VIVC)")

    # Analyze failures by error type
    if failed_varieties:
        print("\n" + "=" * 80)
        print("⚠️  FAILED EXTRACTIONS ANALYSIS")
        print("=" * 80)

        # Group by error type
        error_types = Counter()
        errors_by_type: Dict[str, List[Tuple[str, str]]] = {}

        for variety_name, vivc_num, error in failed_varieties:
            # Simplify error message for grouping
            if "Could not extract" in error:
                error_type = "Could not extract credit from HTML"
            elif "timeout" in error.lower() or "timed out" in error.lower():
                error_type = "Request timeout"
            elif "404" in error or "not found" in error.lower():
                error_type = "Page not found (404)"
            elif "504" in error or "gateway" in error.lower():
                error_type = "Gateway timeout (504)"
            else:
                error_type = error[:50]  # Truncate long errors

            error_types[error_type] += 1
            if error_type not in errors_by_type:
                errors_by_type[error_type] = []
            errors_by_type[error_type].append((variety_name, vivc_num))

        print(f"\nTotal failures: {len(failed_varieties)}")
        print("\nError types:")
        for error_type, count in error_types.most_common():
            print(f"  • {error_type}: {count} varieties")

        print("\nSample varieties by error type:")
        for error_type, varieties in sorted(errors_by_type.items()):
            print(f"\n  {error_type} ({len(varieties)} varieties):")
            for variety_name, vivc_num in varieties[:3]:
                print(f"    - {variety_name} (VIVC {vivc_num})")
            if len(varieties) > 3:
                print(f"    ... and {len(varieties) - 3} more")

    print("\n" + "=" * 80)
    print("✅ Analysis complete! Results cached to: data/vivc_cache.jsonl")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
