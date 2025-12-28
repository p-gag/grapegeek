#!/usr/bin/env python3
"""
Producer Geolocator Module

Extracts geolocation functionality for use in the unified producer research pipeline.
Provides thread-safe geolocation with caching support.
"""

import json
import re
import time
import requests
import os
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def load_geolocation_cache() -> Dict[str, Dict]:
    """Load existing geolocation cache."""
    cache_file = Path("data/producer_geolocations_cache.jsonl")
    cache = {}
    
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            for line in f:
                item = json.loads(line.strip())
                permit_id = item.get('permit_id')
                if permit_id:
                    cache[permit_id] = item
    
    return cache


def save_geolocation_to_cache(geolocation: Dict, cache_file: Path, file_lock: threading.Lock):
    """Thread-safe save to geolocation cache file."""
    with file_lock:
        with open(cache_file, 'a', encoding='utf-8') as f:
            json.dump(geolocation, f, ensure_ascii=False)
            f.write('\n')


def clean_address(address: str) -> str:
    """Clean address by extracting only the first civic number when multiple numbers exist."""
    if not address or not address.strip():
        return address
    
    # Pattern to match addresses like "220 ET 239" or "123 & 125" or "100 et 110"
    pattern = r'^(\d+)\s*(?:ET|et|&|AND|and)\s*\d+(.*)$'
    
    match = re.match(pattern, address.strip())
    if match:
        first_number = match.group(1)
        rest_of_address = match.group(2)
        cleaned = f"{first_number}{rest_of_address}".strip()
        return cleaned
    
    return address.strip()


def geocode_google(address: str, delay: float = 0.1) -> Optional[Tuple[float, float]]:
    """Geocode using Google Maps Geocoding API."""
    time.sleep(delay)
    
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        return None
    
    try:
        response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json',
            params={
                'address': address,
                'key': api_key
            },
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        return None
        
    except Exception:
        return None


def geocode_address(permit_id: str, address: str, city: str, state_province: str, 
                   country: str, postal_code: str, geocode_cache: Dict[str, Tuple], 
                   request_delay: float = 1.1, print_lock: Optional[threading.Lock] = None) -> Optional[Tuple[float, float, bool]]:
    """
    Geocode an address using hybrid strategy: Nominatim first, then Google, then city fallback.
    
    Args:
        permit_id: Unique identifier for caching
        address: Street address
        city: City name
        state_province: State or province
        country: Country code (CA or US)
        postal_code: Postal/zip code
        geocode_cache: Shared geocoding cache
        request_delay: Delay between API requests
        print_lock: Thread lock for print statements (optional)
    
    Returns:
        Tuple of (latitude, longitude, is_fallback) or None if geocoding fails
    """
    def thread_safe_print(message):
        if print_lock:
            with print_lock:
                print(message)
        else:
            print(message)
    
    # Clean address to handle multiple civic numbers
    cleaned_address = clean_address(address) if address else ""
    
    # Use permit_id as cache key for efficiency
    cache_key = permit_id
    
    # Build query for full address
    query_parts = []
    if cleaned_address:
        query_parts.append(cleaned_address)
    if city:
        query_parts.append(city)
    if postal_code:
        query_parts.append(postal_code)
    if state_province:
        query_parts.append(state_province)
    if country:
        country_name = "Canada" if country == "CA" else "United States"
        query_parts.append(country_name)
    
    full_query = ", ".join(part.strip() for part in query_parts if part.strip())
    
    # Check cache first
    if cache_key in geocode_cache:
        cached_result = geocode_cache[cache_key]
        if cached_result:
            # Handle both old format (lat, lon) and new format (lat, lon, fallback)
            if len(cached_result) == 2:
                lat, lon = cached_result
                fallback_status = "(unknown if fallback)"
                result = (lat, lon, False)  # Assume not fallback for old cache entries
            else:
                lat, lon, is_fallback = cached_result
                fallback_status = "(city fallback)" if is_fallback else "(full address)"
                result = cached_result
            thread_safe_print(f"  Using cached: {full_query} → {lat:.4f}, {lon:.4f} {fallback_status}")
            return result
        else:
            thread_safe_print(f"  Using cached: {full_query} → (failed)")
            return cached_result
    
    # Strategy 1: Try Nominatim first (free)
    nominatim_base = "https://nominatim.openstreetmap.org/search"
    user_agent = "GrapeGeek-Unified-Wine-Geocoding/1.0"
    
    countrycodes = 'ca' if country == "CA" else 'us'
    
    params = {
        'q': full_query,
        'format': 'json',
        'limit': 1,
        'countrycodes': countrycodes,
    }
    
    headers = {'User-Agent': user_agent}
    
    try:
        thread_safe_print(f"  1. Nominatim: {full_query}")
        time.sleep(request_delay)
        response = requests.get(nominatim_base, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            result = data[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            
            coords = (lat, lon, False)  # False = not a fallback
            geocode_cache[cache_key] = coords
            thread_safe_print(f"     ✓ {lat:.4f}, {lon:.4f} (Nominatim)")
            return coords
        else:
            thread_safe_print(f"     ✗ No Nominatim results")
            
    except Exception as e:
        thread_safe_print(f"     ✗ Nominatim error: {e}")
    
    # Strategy 2: Try Google for failed cases (paid but accurate)
    if cleaned_address.strip():  # Only try Google if we have a street address
        thread_safe_print(f"  2. Google: {full_query}")
        google_result = geocode_google(full_query)
        
        if google_result:
            lat, lon = google_result
            coords = (lat, lon, False)
            geocode_cache[cache_key] = coords
            thread_safe_print(f"     ✓ {lat:.4f}, {lon:.4f} (Google)")
            return coords
        else:
            thread_safe_print(f"     ✗ Google failed")
        
    # Strategy 3: City fallback for cases where we have a city
    thread_safe_print(f"  3. City fallback: {city}, {state_province}")
    fallback_query_parts = [city, state_province]
    if country == "CA":
        fallback_query_parts.append("Canada")
    else:
        fallback_query_parts.append("United States")
    
    fallback_query = ", ".join(part for part in fallback_query_parts if part)
    
    try:
        time.sleep(request_delay)
        
        fallback_params = {
            'q': fallback_query,
            'format': 'json',
            'limit': 1,
            'countrycodes': countrycodes,
        }
        
        response = requests.get(nominatim_base, 
                              params=fallback_params, 
                              headers=headers, 
                              timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            result = data[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            
            coords = (lat, lon, True)  # True = fallback to city center
            geocode_cache[cache_key] = coords
            thread_safe_print(f"     ✓ {lat:.4f}, {lon:.4f} (city fallback)")
            return coords
        else:
            thread_safe_print(f"     ✗ City geocoding failed")
            
    except Exception as e:
        thread_safe_print(f"     ✗ City geocoding error: {e}")

    # Complete failure - cache the failure
    geocode_cache[cache_key] = None
    thread_safe_print(f"  ✗ Complete geocoding failure")
    return None


def geolocate_producer(producer: Dict, geocode_cache: Dict[str, Tuple], 
                      print_lock: Optional[threading.Lock] = None) -> Optional[Dict]:
    """
    Geolocate a single producer.
    
    Args:
        producer: Producer data dictionary
        geocode_cache: Shared geocoding cache
        print_lock: Thread lock for print statements (optional)
    
    Returns:
        Geolocation data dictionary or None if failed
    """
    try:
        address = producer.get('address', '')
        city = producer.get('city', '')
        state_province = producer.get('state_province', '')
        country = producer.get('country', '')
        postal_code = producer.get('postal_code', '')
        
        permit_id = producer["permit_id"]
        coords = geocode_address(permit_id, address, city, state_province, 
                               country, postal_code, geocode_cache, print_lock=print_lock)
        
        if coords:
            lat, lon, is_fallback = coords
            result = {
                "permit_id": producer["permit_id"],
                "latitude": lat,
                "longitude": lon,
                "address": address,
                "city": city,
                "state_province": state_province,
                "country": country,
                "geocoded_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add fallback information if it was a city fallback
            if is_fallback:
                result["geocoding_method"] = "city_fallback"
            else:
                result["geocoding_method"] = "full_address"
                
            return result
        else:
            return None  # Failed geocoding, don't save anything
            
    except Exception as e:
        def thread_safe_print(message):
            if print_lock:
                with print_lock:
                    print(message)
            else:
                print(message)
        
        thread_safe_print(f"❌ Error geolocating {producer.get('business_name', 'Unknown')}: {e}")
        thread_safe_print(f"   Skipping geolocation due to error")
        return None


def initialize_geo_cache_file(existing_cache: Dict[str, Dict]) -> Path:
    """Initialize the geolocation cache file with existing data."""
    cache_file = Path("data/producer_geolocations_cache.jsonl")
    
    # Sort cache entries by permit_id for consistency
    all_cached = list(existing_cache.values())
    all_cached.sort(key=lambda x: x.get('permit_id', ''))
    
    # Write all cached data to file
    with open(cache_file, 'w', encoding='utf-8') as f:
        for geolocation in all_cached:
            json.dump(geolocation, f, ensure_ascii=False)
            f.write('\n')
    
    return cache_file