#!/usr/bin/env python3
"""
Unified Producer Research Pipeline

Efficient single-script pipeline that combines classification, web search, geolocation, 
and enrichment with early exit logic to minimize API costs.

Pipeline:
1. Check enrichment cache → Skip if exists  
2. Run classifier/search → Get classification
3. Check is_wine_producer() → Early exit if not wine
4. Geolocate wine producer → Add location data
5. Run full enrichment → Save complete data
6. Save early exits to cache → Prevent re-processing

INPUTS:
- data/01_unified_producers.jsonl (from 01_producer_fetch.py)
- data/enriched_producers_cache.jsonl (existing cache, if any)
- data/producer_geolocations_cache.jsonl (existing geolocation cache, if any)
- OpenAI API (for classification and enrichment)
- Web search APIs (via OpenAI web_search tool)

OUTPUTS:
- data/enriched_producers_cache.jsonl (enriched wine producer data + early exits)
- data/producer_geolocations_cache.jsonl (geolocation cache for all producers)
"""

import json
import os
import sys
import time
import threading
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))
from includes.producer_classifier import classify_producer
from includes.producer_enricher import enrich_producer, calculate_enrichment_cost
from includes.producer_geolocator import (
    load_geolocation_cache, save_geolocation_to_cache, 
    geolocate_producer, initialize_geo_cache_file
)

load_dotenv()


def is_wine_producer(producer_data: Dict) -> bool:
    """Check if producer is wine-related based on classification.
    
    Uses same logic as 05_data_merge_final.py
    """
    classification = producer_data.get('classification')
    wine_classifications = {'wine_grower', 'winemaker', 'grape_grower'}
    return classification in wine_classifications


def load_unified_producers() -> List[Dict]:
    """Load unified producer data."""
    unified_file = Path("data/01_unified_producers.jsonl")
    
    if not unified_file.exists():
        raise FileNotFoundError(f"Unified producers file not found: {unified_file}")
    
    producers = []
    with open(unified_file, 'r', encoding='utf-8') as f:
        for line in f:
            producer = json.loads(line.strip())
            producers.append(producer)
    
    print(f"📥 Loaded {len(producers)} unified producers")
    return producers


def load_enrichment_cache() -> Dict[str, Dict]:
    """Load existing enrichment cache."""
    cache_file = Path("data/enriched_producers_cache.jsonl")
    
    if not cache_file.exists():
        print("📁 No existing enrichment cache found, starting fresh")
        return {}
    
    cache = {}
    with open(cache_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line.strip())
            permit_id = item.get('permit_id')
            if permit_id:
                cache[permit_id] = item
    
    print(f"💾 Loaded {len(cache)} cached enrichment entries")
    return cache


def save_to_cache(cache_entry: Dict, cache_file: Path, file_lock: threading.Lock):
    """Thread-safe save to cache file."""
    with file_lock:
        with open(cache_file, 'a', encoding='utf-8') as f:
            json.dump(cache_entry, f, ensure_ascii=False)
            f.write('\n')


def process_producer(producer: Dict, enrichment_cache: Dict, geolocation_cache: Dict,
                    geocode_cache: Dict, client: OpenAI, cache_file: Path, 
                    geo_cache_file: Path, file_lock: threading.Lock, 
                    geo_file_lock: threading.Lock, print_lock: threading.Lock, 
                    cost_tracker: Dict) -> Optional[Dict]:
    """Process a single producer through the research pipeline."""
    permit_id = producer.get('permit_id')
    business_name = producer.get('business_name', 'Unknown')
    
    # Step 1: Check cache
    if permit_id in enrichment_cache:
        cached_entry = enrichment_cache[permit_id]
        if cached_entry.get('skip_reason'):
            reason = f"skipped: {cached_entry['skip_reason']}"
        elif cached_entry.get('wines'):
            reason = "enriched"
        elif cached_entry.get('error'):
            reason = "error"
        else:
            reason = "processed"
        
        with print_lock:
            print(f"⏭️  {business_name} - already in cache ({reason})")
        return None
    
    try:
        # Step 2: Classify producer
        with print_lock:
            print(f"🔍 Classifying {business_name}...")
        
        classification_result = classify_producer(producer, client)
        
        # Track classification cost
        with cost_tracker['lock']:
            cost_tracker['classifications'] += 1
        
        # Step 3: Check if wine producer
        producer_with_class = {**producer, **classification_result}
        if not is_wine_producer(producer_with_class):
            # Early exit - save to cache
            cache_entry = {
                "permit_id": permit_id,
                "classification": classification_result.get('classification'),
                "website": classification_result.get('website'),
                "social_media": classification_result.get('social_media'),
                "skip_reason": "not_wine_producer",
                "verified_wine_producer": False,
                "processed_at": datetime.now().isoformat()
            }
            
            with print_lock:
                print(f"⏸️  {business_name} - not wine producer ({classification_result.get('classification')})")
            
            save_to_cache(cache_entry, cache_file, file_lock)
            return cache_entry
        
        # Step 4: Geolocate wine producer (after early exit check)
        geolocation_data = None
        if permit_id not in geolocation_cache:
            with print_lock:
                print(f"📍 Geolocating wine producer {business_name}...")
            
            geolocation_result = geolocate_producer(producer, geocode_cache, print_lock)
            if geolocation_result:
                geolocation_data = geolocation_result
                save_geolocation_to_cache(geolocation_result, geo_cache_file, geo_file_lock)
                # Update local cache to prevent duplicate processing
                geolocation_cache[permit_id] = geolocation_result
        else:
            geolocation_data = geolocation_cache[permit_id]
            with print_lock:
                print(f"📍 {business_name} - already geolocated")
        
        # Step 5: Full enrichment for wine producers
        with print_lock:
            print(f"🍇 Enriching wine producer {business_name}...")
        
        _, enrichment_data = enrich_producer(producer, os.getenv('OPENAI_API_KEY'), 
                                           request_delay=1.0, print_lock=print_lock)
        
        # Track enrichment cost
        with cost_tracker['lock']:
            cost_tracker['enrichments'] += 1
        
        # Step 6: Save complete data
        cache_entry = {
            "permit_id": permit_id,
            "classification": classification_result.get('classification'),
            "website": classification_result.get('website') or enrichment_data.get('website'),
            "social_media": classification_result.get('social_media') or enrichment_data.get('social_media'),
            "processed_at": datetime.now().isoformat(),
            **enrichment_data  # Include all enrichment data
        }
        
        save_to_cache(cache_entry, cache_file, file_lock)
        return cache_entry
        
    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        with print_lock:
            print(f"❌ {business_name} - {error_msg}")
        
        # Save error to cache to prevent reprocessing
        cache_entry = {
            "permit_id": permit_id,
            "error": error_msg,
            "processed_at": datetime.now().isoformat()
        }
        
        save_to_cache(cache_entry, cache_file, file_lock)
        return cache_entry


def main():
    """Main function to run the unified producer research pipeline."""
    parser = argparse.ArgumentParser(description="Unified producer research pipeline")
    parser.add_argument("--limit", type=int, help="Limit number of producers to process (for testing)")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads to use")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    print("🍷 Unified Producer Research Pipeline")
    print("=" * 50)
    
    # Load data
    all_producers = load_unified_producers()
    enrichment_cache = load_enrichment_cache()
    geolocation_cache = load_geolocation_cache()
    
    # Initialize geolocation cache file
    geo_cache_file = initialize_geo_cache_file(geolocation_cache)
    print(f"💾 Initialized geolocation cache with {len(geolocation_cache)} entries")
    
    # Apply limit if specified
    if args.limit:
        all_producers = all_producers[:args.limit]
        print(f"🔢 Limited to first {args.limit} producers")
    
    # Filter out already processed producers
    unprocessed_producers = [
        p for p in all_producers 
        if p.get('permit_id') not in enrichment_cache
    ]
    
    print(f"📊 Found {len(unprocessed_producers)} unprocessed producers (out of {len(all_producers)} total)")
    
    if not unprocessed_producers:
        print("✅ All producers already processed!")
        return
    
    # Cost estimation
    wine_producer_ratio = 0.3  # Estimate based on historical data
    estimated_wine_producers = len(unprocessed_producers) * wine_producer_ratio
    cost_estimates = calculate_enrichment_cost(int(estimated_wine_producers))
    
    print(f"\n💰 Cost Estimation:")
    print(f"   Unprocessed producers: {len(unprocessed_producers)}")
    print(f"   Estimated wine producers (~30%): {int(estimated_wine_producers)}")
    print(f"   Estimated total cost: ${cost_estimates['estimated_total_cost']:.2f}")
    print(f"   Cost range: ${cost_estimates['estimated_cost_range']['low']:.2f} - ${cost_estimates['estimated_cost_range']['high']:.2f}")
    
    # Confirm processing
    if not args.yes:
        user_input = input("\n🤔 Continue with processing? (y/N): ")
        if user_input.lower() != 'y':
            print("🚫 Processing cancelled")
            return
    
    # Setup for processing
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    cache_file = Path("data/enriched_producers_cache.jsonl")
    
    # Create shared geocoding cache for API efficiency
    geocode_cache = {}
    for permit_id, geo_data in geolocation_cache.items():
        lat = geo_data.get('latitude')
        lon = geo_data.get('longitude')
        method = geo_data.get('geocoding_method', 'unknown')
        if lat is not None and lon is not None:
            is_fallback = method == 'city_fallback'
            geocode_cache[permit_id] = (lat, lon, is_fallback)
    
    # Threading locks
    file_lock = threading.Lock()
    geo_file_lock = threading.Lock()
    print_lock = threading.Lock()
    
    # Cost tracking
    cost_tracker = {
        'lock': threading.Lock(),
        'classifications': 0,
        'enrichments': 0
    }
    
    # Process producers
    print(f"\n🚀 Starting processing with {args.threads} threads...")
    start_time = time.time()
    
    results = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        # Submit all producers
        future_to_producer = {
            executor.submit(
                process_producer, producer, enrichment_cache, geolocation_cache,
                geocode_cache, client, cache_file, geo_cache_file, file_lock, 
                geo_file_lock, print_lock, cost_tracker
            ): producer
            for producer in unprocessed_producers
        }
        
        # Collect results
        for future in as_completed(future_to_producer):
            producer = future_to_producer[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as exc:
                permit_id = producer.get('permit_id', 'unknown')
                with print_lock:
                    print(f'❌ Producer {permit_id} generated an exception: {exc}')
    
    # Final statistics
    elapsed_time = time.time() - start_time
    total_processed = len(results)
    wine_producers_enriched = cost_tracker['enrichments']
    non_wine_producers = cost_tracker['classifications'] - wine_producers_enriched
    
    print(f"\n📈 Processing Complete!")
    print(f"   Total processed: {total_processed}")
    print(f"   Wine producers enriched: {wine_producers_enriched}")
    print(f"   Non-wine producers (early exit): {non_wine_producers}")
    print(f"   Processing time: {elapsed_time:.1f} seconds")
    print(f"   Average time per producer: {elapsed_time/total_processed:.1f}s")
    
    # Cost savings calculation
    if cost_tracker['classifications'] > 0:
        savings_percentage = (non_wine_producers / cost_tracker['classifications']) * 100
        print(f"   Cost savings from early exits: {savings_percentage:.1f}%")
    
    print(f"   Enrichment results saved to: {cache_file}")
    print(f"   Geolocation results saved to: {geo_cache_file}")


if __name__ == "__main__":
    main()