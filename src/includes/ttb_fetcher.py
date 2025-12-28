#!/usr/bin/env python3
"""
TTB (US) Producer Fetcher

Extracted from 01_producer_fetch.py for use in unified producer fetch pipeline.
Fetches and processes US wine producers from TTB permits data.
"""

import csv
import requests
from pathlib import Path
from typing import Dict, List, Any


# US northeastern border states configuration
NORTHEASTERN_STATES = {
    'MN': 'Minnesota',
    'WI': 'Wisconsin', 
    'MI': 'Michigan',
    'OH': 'Ohio',
    'PA': 'Pennsylvania',
    'NY': 'New York',
    'VT': 'Vermont',
    'NH': 'New Hampshire',
    'ME': 'Maine'
}

# Business exclusion patterns (non-wine businesses with wine permits)
EXCLUSION_PATTERNS = [
    'BREW', 'BREWING', 'BEER', 'ALE', 'LAGER', 'IPA', 'STOUT', 'PORTER',
    'DISTILL', 'SPIRITS', 'WHISKEY', 'VODKA', 'GIN', 'RUM', 'BOURBON',
    'CIDER', 'CIDERY', 'MEAD', 'MEADERY',
    'GROCERY', 'MARKET', 'STORE', 'RETAIL', 'SHOP',
    'DISTRIBUTOR', 'WHOLESALE', 'IMPORT'
]


def extract_state_from_permit(permit_id: str) -> str:
    """Extract state code from TTB permit ID."""
    if len(permit_id) >= 2:
        return permit_id[:2].upper()
    return ""


def is_excluded_business(business_name: str) -> bool:
    """Check if business should be excluded based on name patterns."""
    name_upper = business_name.upper()
    
    # Check for exclusion patterns
    for pattern in EXCLUSION_PATTERNS:
        if pattern in name_upper:
            return True
    
    return False


def normalize_ttb_to_producer(permit_id: str, business_name: str, trade_name: str,
                             address: str, city: str, postal_code: str, 
                             county: str, state_code: str) -> Dict[str, Any]:
    """Convert TTB permit data to normalized producer format."""
    return {
        'permit_id': permit_id,
        'source': 'TTB',
        'country': 'US',
        'state_province': NORTHEASTERN_STATES[state_code],
        'business_name': business_name,
        'trade_name': trade_name,
        'permit_holder': business_name,  # TTB doesn't have separate permit holder
        'address': address,
        'city': city,
        'postal_code': postal_code,
        'county': county,
        'classification': None,
        'website': None,
        'social_media': None,
        'latitude': None,
        'longitude': None,
        'geocoding_method': None
    }


def fetch_us_producers(data_dir: str = "data/us") -> Dict[str, Any]:
    """Fetch US wine producers from TTB data.
    
    Args:
        data_dir: Directory to save TTB data files
        
    Returns:
        Dict with normalized producer data and metadata
    """
    us_dir = Path(data_dir)
    us_dir.mkdir(parents=True, exist_ok=True)
    
    ttb_url = "https://www.ttb.gov/media/81096/download"
    ttb_file = us_dir / "ttb_wine_producers.csv"
    
    # Download TTB data
    print("   Downloading TTB data...")
    try:
        response = requests.get(ttb_url, stream=True)
        response.raise_for_status()
        
        with open(ttb_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"   Downloaded TTB data to {ttb_file}")
    except Exception as e:
        print(f"   Error downloading TTB data: {e}")
        if ttb_file.exists():
            print(f"   Using existing file: {ttb_file}")
        else:
            return {"producers": [], "metadata": {"error": f"Failed to download TTB data: {e}"}}
    
    # Parse and filter US data
    producers = []
    total_count = 0
    filtered_count = 0
    excluded_count = 0
    state_counts = {}
    
    print("   Parsing and filtering TTB data...")
    with open(ttb_file, 'r', newline='', encoding='latin1') as f:
        reader = csv.reader(f)
        
        for row in reader:
            total_count += 1
            
            if len(row) < 8:
                continue  # Skip malformed rows
            
            permit_id = row[0].strip()
            business_name = row[1].strip().strip('"')
            trade_name = row[2].strip().strip('"') if row[2] else ""
            address = row[3].strip().strip('"')
            city = row[4].strip().strip('"')
            postal_code = row[5].strip()
            county = row[6].strip().strip('"')
            
            # Extract state from permit ID
            state_code = extract_state_from_permit(permit_id)
            
            # Filter by northeastern states
            if state_code not in NORTHEASTERN_STATES:
                continue
            
            # Filter out non-wine businesses
            combined_name = f"{business_name} {trade_name}".strip()
            if is_excluded_business(combined_name):
                excluded_count += 1
                continue
            
            # Create normalized producer
            producer = normalize_ttb_to_producer(
                permit_id, business_name, trade_name, address, 
                city, postal_code, county, state_code
            )
            
            producers.append(producer)
            filtered_count += 1
            
            # Count by state
            state_name = NORTHEASTERN_STATES[state_code]
            state_counts[state_name] = state_counts.get(state_name, 0) + 1
    
    # Create metadata
    metadata = {
        'source_url': ttb_url,
        'raw_record_count': total_count,
        'northeastern_producers': filtered_count,
        'excluded_non_wine': excluded_count,
        'filter_criteria': f"Northeastern US states: {list(NORTHEASTERN_STATES.values())}",
        'state_distribution': state_counts
    }
    
    print(f"   Processed {total_count:,} total TTB records")
    print(f"   Filtered to {filtered_count:,} northeastern wine producers")
    print(f"   Excluded {excluded_count} non-wine businesses")
    
    return {
        'producers': producers,
        'metadata': metadata
    }