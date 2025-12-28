#!/usr/bin/env python3
"""
Unified Producer Data Fetch

Downloads and normalizes both Quebec (RACJ) and US (TTB) wine producer data 
into a unified format, then outputs a sorted JSONL file for version control.

This replaces the previous separate 00_quebec_fetch.py and combined fetch logic,
using modular fetchers for clean separation of concerns.

INPUTS:
- Quebec RACJ API: https://racj.ca/api/vins (live API call)
- US TTB Data: data/us/ttb_wine_producers.csv (pre-downloaded CSV file)

OUTPUTS:
- data/01_unified_producers.jsonl (unified producer records in JSONL format)
- data/01_unified_producers_metadata.json (fetch metadata and statistics)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))
from includes.racj_fetcher import fetch_quebec_producers
from includes.ttb_fetcher import fetch_us_producers


def save_unified_data(unified_data: List[Dict], metadata: Dict[str, Any]) -> Path:
    """Save unified data to JSONL file."""
    output_file = Path("data/01_unified_producers.jsonl")
    
    # Ensure directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save producers as JSONL (one JSON object per line)
    with open(output_file, 'w', encoding='utf-8') as f:
        for producer in unified_data:
            json.dump(producer, f, ensure_ascii=False)
            f.write('\n')
    
    # Save metadata separately for reference
    metadata_file = output_file.parent / "01_unified_producers_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Saved {len(unified_data)} unified producer records")
    print(f"📊 Metadata saved to {metadata_file}")
    
    return output_file


def analyze_unified_dataset(quebec_data: Dict, us_data: Dict, unified_producers: List[Dict]):
    """Print analysis of the unified dataset."""
    print(f"\n📊 Unified Dataset Summary")
    print("=" * 50)
    
    # By source
    quebec_count = len(quebec_data['producers'])
    us_count = len(us_data['producers'])
    
    print(f"By Source:")
    print(f"   Quebec (RACJ): {quebec_count:,}")
    print(f"   US (TTB): {us_count:,}")
    print(f"   Total: {len(unified_producers):,}")
    
    # By state/province
    location_counts = {}
    for producer in unified_producers:
        location = producer.get('state_province', 'Unknown')
        location_counts[location] = location_counts.get(location, 0) + 1
    
    print(f"\nBy State/Province:")
    for location, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {location}: {count:,}")
    
    # Data quality
    with_address = sum(1 for p in unified_producers if p.get('address'))
    with_city = sum(1 for p in unified_producers if p.get('city'))
    
    print(f"\nData Quality:")
    print(f"   With address: {with_address:,} ({with_address/len(unified_producers)*100:.1f}%)")
    print(f"   With city: {with_city:,} ({with_city/len(unified_producers)*100:.1f}%)")


def main():
    """Main function to fetch and unify producer data."""
    print("🍷 Unified Producer Data Fetch")
    print("=" * 50)
    
    # Fetch Quebec data
    print("📥 Fetching Quebec (RACJ) wine producer data...")
    quebec_data = fetch_quebec_producers()
    quebec_producers = quebec_data['producers']
    print(f"   Loaded {len(quebec_producers)} Quebec wine producers")
    
    if quebec_data.get('metadata', {}).get('error'):
        print(f"   ⚠️  Quebec fetch issue: {quebec_data['metadata']['error']}")
    else:
        print(f"   Normalized {len(quebec_producers)} Quebec producers")
    
    # Fetch US data  
    print("📥 Fetching US (TTB) wine producer data...")
    us_data = fetch_us_producers()
    us_producers = us_data['producers']
    
    if us_data.get('metadata', {}).get('error'):
        print(f"   ❌ US fetch failed: {us_data['metadata']['error']}")
        us_producers = []
    else:
        print(f"   Loaded {len(us_producers)} US producers")
    
    # Combine datasets
    print("🔄 Combining and sorting datasets...")
    unified_producers = quebec_producers + us_producers
    
    # Sort by source then by business name for consistent ordering
    unified_producers.sort(key=lambda x: (
        x.get('source', ''),
        x.get('business_name', '').lower()
    ))
    
    print(f"   Combined {len(quebec_producers)} Quebec + {len(us_producers)} US = {len(unified_producers)} total producers")
    
    # Create combined metadata
    combined_metadata = {
        'fetch_date': datetime.now().isoformat(),
        'total_producers': len(unified_producers),
        'sources': {
            'quebec': {
                'count': len(quebec_producers),
                'metadata': quebec_data.get('metadata', {})
            },
            'us': {
                'count': len(us_producers), 
                'metadata': us_data.get('metadata', {})
            }
        }
    }
    
    # Save unified dataset
    output_file = save_unified_data(unified_producers, combined_metadata)
    
    # Print analysis
    analyze_unified_dataset(quebec_data, us_data, unified_producers)
    
    print(f"\n✅ Unified producer data saved to: {output_file}")
    print(f"📄 Ready for pipeline processing with scripts 02-12")


if __name__ == "__main__":
    main()