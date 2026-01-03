#!/usr/bin/env python3
"""
Canada Province Winery Data Fetcher

Loads and normalizes Canadian province winery data from research files
into the unified producer format.

INPUT: data/can/canada_province_wineries.jsonl (new format with province_code, address, city)
OUTPUT: List of normalized producer records in unified format
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def get_full_province_name(province_code: str) -> str:
    """Convert 2-letter province code to full province name."""
    code_to_name = {
        'AB': 'Alberta',
        'BC': 'British Columbia',
        'MB': 'Manitoba',
        'NB': 'New Brunswick',
        'NL': 'Newfoundland and Labrador',
        'NS': 'Nova Scotia',
        'NT': 'Northwest Territories',
        'NU': 'Nunavut',
        'ON': 'Ontario',
        'PE': 'Prince Edward Island',
        'QC': 'Quebec',
        'SK': 'Saskatchewan',
        'YT': 'Yukon'
    }
    return code_to_name.get(province_code, province_code)


def generate_permit_id(province_code: str, business_name: str) -> str:
    """Generate permit ID from province code + cleaned business name."""
    # Clean business name: uppercase and keep only A-Z
    clean_name = re.sub(r'[^A-Z]', '', business_name.upper())
    return f"{province_code}{clean_name}"


def normalize_canada_province_producer(winery_data: Dict, index: int) -> Dict[str, Any]:
    """Normalize a Canada province winery record to unified producer format."""
    
    province_code = winery_data.get('province_code', '')
    business_name = winery_data.get('business_name', '')
    address = winery_data.get('address')
    city = winery_data.get('city')
    
    # Generate permit_id using province code + cleaned business name
    permit_id = generate_permit_id(province_code, business_name)
    
    # Get full province name
    full_province_name = get_full_province_name(province_code)
    
    return {
        "permit_id": permit_id,
        "source": "Canada_Province_Research", 
        "country": "CA",
        "state_province": full_province_name,
        "business_name": business_name,
        "permit_holder": business_name,  # Use same as business name
        "neq": None,
        "permit_categories": ["VIN"],  # Assume all are wine producers
        "address": address,
        "city_code": None,
        "city": city, 
        "postal_code": None,
        "classification": None,
        "website": None,
        "social_media": None,
        "latitude": None,
        "longitude": None,
        "geocoding_method": None
    }


def fetch_canada_province_producers() -> Dict[str, Any]:
    """
    Load Canada province winery data from research file.
    
    Returns:
        Dict with 'producers' list and 'metadata' dict
    """
    data_file = Path("data/can/canada_province_wineries.jsonl")
    
    metadata = {
        'source_file': str(data_file),
        'fetch_date': datetime.now().isoformat(),
        'method': 'file_load'
    }
    
    if not data_file.exists():
        print(f"⚠️ Canada province data file not found: {data_file}")
        return {
            'producers': [],
            'metadata': {**metadata, 'error': f'File not found: {data_file}'}
        }
    
    producers = []
    line_count = 0
    error_count = 0
    province_counter = {}  # Track index per province for permit_id generation
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line_count += 1
                if line.strip():
                    try:
                        winery_data = json.loads(line.strip())
                        province_code = winery_data.get('province_code', 'XX')
                        
                        # Increment counter for this province
                        if province_code not in province_counter:
                            province_counter[province_code] = 0
                        province_counter[province_code] += 1
                        
                        # Generate producer record
                        producer = normalize_canada_province_producer(
                            winery_data, 
                            province_counter[province_code]
                        )
                        producers.append(producer)
                        
                    except json.JSONDecodeError as e:
                        error_count += 1
                        print(f"⚠️ Error parsing Canada province data line {line_num}: {str(e)[:100]}")
                        continue
    
    except Exception as e:
        error_msg = f"Failed to load Canada province data: {e}"
        print(f"❌ {error_msg}")
        return {
            'producers': [],
            'metadata': {**metadata, 'error': error_msg}
        }
    
    # Update metadata with results
    metadata.update({
        'lines_processed': line_count,
        'producers_loaded': len(producers), 
        'parsing_errors': error_count,
        'provinces_found': len(province_counter),
        'province_breakdown': dict(province_counter)
    })
    
    return {
        'producers': producers,
        'metadata': metadata
    }


if __name__ == "__main__":
    # Test the fetcher
    result = fetch_canada_province_producers()
    print(f"Loaded {len(result['producers'])} Canada province producers")
    
    # Show sample
    if result['producers']:
        print("Sample producer:")
        print(json.dumps(result['producers'][0], indent=2))
        
    # Show province breakdown
    if result['metadata'].get('province_breakdown'):
        print("Province breakdown:")
        for province, count in result['metadata']['province_breakdown'].items():
            print(f"  {province}: {count}")