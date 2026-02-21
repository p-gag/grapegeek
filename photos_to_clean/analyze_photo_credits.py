#!/usr/bin/env python3
"""Quick script to analyze photo credits distribution."""

import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent / "src"))

from includes.grape_varieties import GrapeVarietiesModel
from includes.vivc_client import _cache
from bs4 import BeautifulSoup
import re

print("\n📊 Analyzing Photo Credits Distribution")
print("=" * 70)

# Load varieties
grape_model = GrapeVarietiesModel()
varieties_with_vivc = [
    (v.name, v.get_vivc_number())
    for v in grape_model.get_all_varieties()
    if v.get_vivc_number()
]

print(f"Total varieties: {len(varieties_with_vivc)}\n")

breeder_counts = Counter()
varieties_by_breeder = {}
jki_indicators = ['julius', 'kühn', 'jki', 'brühl', 'geilweilerhof']

# Check cache
cached_count = sum(1 for _, vivc in varieties_with_vivc
                   if _cache.get(f"https://www.vivc.de/index.php?r=passport/view&id={vivc}"))
print(f"Cached passport pages: {cached_count}/{len(varieties_with_vivc)}")
print("Analyzing from cache...\n")

for i, (variety_name, vivc_number) in enumerate(varieties_with_vivc, 1):
    if i % 50 == 0:
        print(f"Progress: {i}/{len(varieties_with_vivc)}")

    passport_url = f"https://www.vivc.de/index.php?r=passport/view&id={vivc_number}"
    passport_html = _cache.get(passport_url)

    if not passport_html:
        continue

    try:
        soup = BeautifulSoup(passport_html, 'html.parser')
        breeder_row = soup.find('th', string=re.compile(r'^\s*Breeder\s*$', re.IGNORECASE))

        if breeder_row:
            breeder_td = breeder_row.find_next('td')
            if breeder_td:
                breeder_link = breeder_td.find('a')
                breeder_name = breeder_link.get_text().strip() if breeder_link else breeder_td.get_text().strip()

                is_jki = any(indicator in breeder_name.lower() for indicator in jki_indicators)

                category = "JKI/VIVC" if is_jki else (breeder_name if breeder_name and len(breeder_name) > 3 else "Unknown")

                breeder_counts[category] += 1
                if category not in varieties_by_breeder:
                    varieties_by_breeder[category] = []
                varieties_by_breeder[category].append((variety_name, vivc_number))
    except:
        pass

# Results
print(f"\n{'=' * 70}")
print("📊 RESULTS")
print(f"{'=' * 70}\n")

total = sum(breeder_counts.values())
print(f"Total analyzed: {total}\n")
print(f"{'Breeder/Source':<40} {'Count':>10} {'%':>8}")
print("-" * 70)

for breeder, count in breeder_counts.most_common(20):
    percentage = (count / total * 100) if total > 0 else 0
    print(f"{breeder:<40} {count:>10} {percentage:>7.1f}%")

# Non-JKI breeders
print(f"\n{'=' * 70}")
print("⚠️  NON-JKI BREEDERS (Potential External Photos)")
print(f"{'=' * 70}\n")

for breeder, varieties in sorted(varieties_by_breeder.items()):
    if breeder != "JKI/VIVC" and breeder != "Unknown":
        print(f"\n{breeder} ({len(varieties)} varieties):")
        for variety_name, vivc_num in varieties[:3]:
            print(f"  - {variety_name} (VIVC {vivc_num})")
        if len(varieties) > 3:
            print(f"  ... and {len(varieties) - 3} more")
