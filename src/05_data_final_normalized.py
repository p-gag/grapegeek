#!/usr/bin/env python3
"""
Create Final Normalized Wine Producers Dataset

Merges unified producer data with search cache and geolocation cache,
filters to wine-related producers using verified_wine_producer attribute,
and applies grape variety and wine type normalization in a single step.

INPUTS:
- data/01_unified_producers.jsonl (base producer data)
- data/enriched_producers_cache.jsonl (classification + web presence + verification + wines)
- data/producer_geolocations_cache.jsonl (latitude/longitude)
- data/grape_variety_mapping.jsonl (via GrapeVarietiesModel - grape variety aliases)
- data/wine_type_mapping.yaml (wine type normalization mappings)

OUTPUTS:
- data/05_wine_producers_final_normalized.jsonl (merged + filtered + normalized dataset)
"""

import json
import yaml
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Import the grape varieties model
sys.path.insert(0, str(Path(__file__).parent))
from includes.grape_varieties import GrapeVarietiesModel


def load_unified_producers() -> List[Dict]:
    """Load the base unified producer dataset."""
    unified_file = Path("data/01_unified_producers.jsonl")
    
    if not unified_file.exists():
        print(f"❌ Base file not found: {unified_file}")
        return []
    
    producers = []
    with open(unified_file, 'r', encoding='utf-8') as f:
        for line in f:
            producers.append(json.loads(line.strip()))
    
    print(f"📥 Loaded {len(producers)} unified producers")
    return producers


def load_search_cache() -> Dict[str, Dict]:
    """Load search cache data indexed by permit_id."""
    search_file = Path("data/enriched_producers_cache.jsonl")
    
    if not search_file.exists():
        print(f"⚠️  Search cache not found: {search_file}")
        return {}
    
    search_cache = {}
    with open(search_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            permit_id = data.get('permit_id')
            if permit_id:
                search_cache[permit_id] = data
    
    print(f"📥 Loaded {len(search_cache)} search cache entries")
    return search_cache


def load_geo_cache() -> Dict[str, Dict]:
    """Load geolocation cache data indexed by permit_id."""
    geo_file = Path("data/producer_geolocations_cache.jsonl")
    
    if not geo_file.exists():
        print(f"⚠️  Geo cache not found: {geo_file}")
        return {}
    
    geo_cache = {}
    with open(geo_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            permit_id = data.get('permit_id')
            if permit_id:
                geo_cache[permit_id] = data
    
    print(f"📥 Loaded {len(geo_cache)} geo cache entries")
    return geo_cache


def load_wine_type_mapping() -> Dict[str, Dict]:
    """Load wine type normalization mapping."""
    mapping_file = Path("data/wine_type_mapping.yaml")
    
    if not mapping_file.exists():
        print(f"⚠️  Wine type mapping not found: {mapping_file}")
        return {}
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        return data.get('wine_type_mapping', {})


def normalize_grape_variety(variety: str, model: GrapeVarietiesModel) -> str:
    """Normalize a grape variety name using the grape varieties model."""
    if not variety or not model:
        return variety
    
    # Use the model's normalization method
    normalized = model.normalize_variety_name(variety)
    return normalized if normalized else variety


def normalize_wine_type(wine_type: str, mapping: Dict[str, Dict]) -> str:
    """Normalize a wine type using the mapping."""
    if not wine_type or not mapping:
        return wine_type
    
    # Clean the wine type before mapping:
    # 1. Remove anything in parentheses
    # 2. Remove anything after a forward slash
    # 3. Strip whitespace
    cleaned_wine_type = wine_type
    
    # Remove parentheses and their contents
    cleaned_wine_type = re.sub(r'\([^)]*\)', '', cleaned_wine_type)
    
    # Remove anything after forward slash
    if '/' in cleaned_wine_type:
        cleaned_wine_type = cleaned_wine_type.split('/')[0]
    
    # Strip whitespace
    cleaned_wine_type = cleaned_wine_type.strip()
    
    if not cleaned_wine_type:
        return wine_type  # Return original if cleaning resulted in empty string
    
    wine_type_lower = cleaned_wine_type.lower()
    
    # Check each official wine type's aliases
    for official_name, info in mapping.items():
        if not isinstance(info, dict):
            continue
            
        aliases = info.get('aliases', [])
        if not isinstance(aliases, list):
            continue
            
        # Safely check aliases, ensuring they are strings
        for alias in aliases:
            if isinstance(alias, str) and wine_type_lower == alias.lower():
                return official_name
    
    # If not found in mapping, return cleaned version
    return cleaned_wine_type


def merge_producer_data(producer: Dict, search_data: Optional[Dict], geo_data: Optional[Dict]) -> Dict:
    """Merge producer with search and geo data."""
    merged = producer.copy()
    
    # Add search data (classification, website, social_media, verified_wine_producer, wines)
    if search_data:
        merged['classification'] = search_data.get('classification')
        merged['website'] = search_data.get('website')
        merged['social_media'] = search_data.get('social_media')
        merged['verified_wine_producer'] = search_data.get('verified_wine_producer')
        merged['wines'] = search_data.get('wines', [])
    else:
        merged['classification'] = None
        merged['website'] = None
        merged['social_media'] = None
        merged['verified_wine_producer'] = None
        merged['wines'] = []
    
    # Add geo data (latitude, longitude, geocoding_method)
    if geo_data:
        merged['latitude'] = geo_data.get('latitude')
        merged['longitude'] = geo_data.get('longitude') 
        merged['geocoding_method'] = geo_data.get('geocoding_method')
    else:
        merged['latitude'] = None
        merged['longitude'] = None
        merged['geocoding_method'] = None
    
    # Add computed source field
    country = merged.get('country', 'US')
    merged['source'] = 'RACJ' if country == 'CA' else 'TTB'
    
    return merged


def is_wine_producer(merged_producer: Dict) -> bool:
    """Check if producer is wine-related based on classification and verification."""
    # First check if explicitly verified as wine producer
    verified_wine_producer = merged_producer.get('verified_wine_producer')
    if verified_wine_producer is True:
        return True
    elif verified_wine_producer is False:
        return False
    
    # Fallback to classification-based logic for unprocessed producers
    classification = merged_producer.get('classification')
    wine_classifications = {'wine_grower', 'winemaker', 'grape_grower'}
    return classification in wine_classifications


def normalize_producer_wines(producer: Dict, grape_model: GrapeVarietiesModel, wine_type_mapping: Dict[str, Dict]) -> Dict:
    """Normalize both grape varieties and wine types for a producer's wines."""
    normalized_producer = producer.copy()
    
    wines = producer.get('wines', [])
    if not isinstance(wines, list):
        return normalized_producer
    
    normalized_wines = []
    
    for wine in wines:
        if not isinstance(wine, dict):
            normalized_wines.append(wine)
            continue
            
        normalized_wine = wine.copy()
        
        # Normalize grape varieties (cépages)
        cepages = wine.get('cepages', [])
        if isinstance(cepages, list):
            normalized_cepages = []
            for cepage in cepages:
                if isinstance(cepage, str):
                    normalized_cepage = normalize_grape_variety(cepage, grape_model)
                    normalized_cepages.append(normalized_cepage)
                else:
                    normalized_cepages.append(cepage)
            normalized_wine['cepages'] = normalized_cepages
        
        # Normalize wine type
        wine_type = wine.get('type')
        if wine_type:
            normalized_type = normalize_wine_type(wine_type, wine_type_mapping)
            normalized_wine['type'] = normalized_type
        
        normalized_wines.append(normalized_wine)
    
    normalized_producer['wines'] = normalized_wines
    return normalized_producer


def analyze_coverage(producers: List[Dict], search_cache: Dict, geo_cache: Dict):
    """Analyze data coverage statistics."""
    total = len(producers)
    search_coverage = 0
    geo_coverage = 0
    both_coverage = 0
    
    for producer in producers:
        permit_id = producer.get('permit_id')
        has_search = permit_id in search_cache
        has_geo = permit_id in geo_cache
        
        if has_search:
            search_coverage += 1
        if has_geo:
            geo_coverage += 1
        if has_search and has_geo:
            both_coverage += 1
    
    print(f"\n📊 Data Coverage Analysis:")
    print(f"  Total producers:        {total}")
    print(f"  With search data:       {search_coverage} ({search_coverage/total*100:.1f}%)")
    print(f"  With geo data:          {geo_coverage} ({geo_coverage/total*100:.1f}%)")
    print(f"  With both:              {both_coverage} ({both_coverage/total*100:.1f}%)")


def create_final_normalized_dataset():
    """Create the final normalized wine producer dataset."""
    print("🍷 Creating Final Normalized Wine Producers Dataset")
    print("=" * 60)
    
    # Load all data sources
    producers = load_unified_producers()
    search_cache = load_search_cache()
    geo_cache = load_geo_cache()
    
    if not producers:
        print("❌ No base producer data found. Exiting.")
        return
    
    # Load normalization mappings
    grape_model = GrapeVarietiesModel()
    wine_type_mapping = load_wine_type_mapping()
    
    print(f"📋 Loaded {len(wine_type_mapping)} wine type mappings")
    print(f"📊 Loaded {len(grape_model.get_variety_names())} grape varieties")
    
    # Analyze coverage
    analyze_coverage(producers, search_cache, geo_cache)
    
    # Merge all producer data
    print(f"\n🔄 Merging data sources...")
    merged_producers = []
    
    for producer in producers:
        permit_id = producer.get('permit_id')
        search_data = search_cache.get(permit_id)
        geo_data = geo_cache.get(permit_id)
        
        merged = merge_producer_data(producer, search_data, geo_data)
        merged_producers.append(merged)
    
    print(f"✅ Merged {len(merged_producers)} producers")
    
    # Filter to wine producers only
    print(f"\n🍇 Filtering to wine producers...")
    wine_producers = []
    classification_counts = {}
    verification_stats = {'verified_wine': 0, 'verified_not_wine': 0, 'unverified': 0}
    
    for producer in merged_producers:
        classification = producer.get('classification') or 'unknown'
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
        
        # Track verification status
        verified = producer.get('verified_wine_producer')
        if verified is True:
            verification_stats['verified_wine'] += 1
        elif verified is False:
            verification_stats['verified_not_wine'] += 1
        else:
            verification_stats['unverified'] += 1
        
        if is_wine_producer(producer):
            wine_producers.append(producer)
    
    print(f"✅ Found {len(wine_producers)} wine producers")
    
    # Show verification breakdown
    print(f"\n🔍 Verification Status:")
    print(f"  ✅ Verified wine producers:      {verification_stats['verified_wine']:4d}")
    print(f"  ❌ Verified non-wine producers:  {verification_stats['verified_not_wine']:4d}")
    print(f"  ❓ Unverified (legacy):          {verification_stats['unverified']:4d}")
    
    # Show classification breakdown
    print(f"\n📋 Classification Breakdown:")
    for classification, count in sorted(classification_counts.items()):
        wine_status = "🍷" if classification in {'wine_grower', 'winemaker', 'grape_grower'} else "❌"
        print(f"  {wine_status} {classification:<15}: {count:4d}")
    
    # Normalize wine data
    print(f"\n🔄 Normalizing grape varieties and wine types...")
    normalized_producers = []
    normalization_stats = {
        'producers_with_wines': 0,
        'total_wines': 0,
        'total_wines_with_cepages': 0,
        'total_cepages_normalized': 0,
        'total_wine_types_normalized': 0,
        'unique_varieties_global': set(),
        'unique_wine_types_global': set()
    }
    
    for producer in wine_producers:
        normalized_producer = normalize_producer_wines(producer, grape_model, wine_type_mapping)
        normalized_producers.append(normalized_producer)
        
        # Calculate normalization statistics
        wines = normalized_producer.get('wines', [])
        if wines:
            normalization_stats['producers_with_wines'] += 1
            normalization_stats['total_wines'] += len(wines)
            
            for wine in wines:
                if isinstance(wine, dict):
                    # Count cépages
                    cepages = wine.get('cepages', [])
                    if isinstance(cepages, list) and cepages:
                        normalization_stats['total_wines_with_cepages'] += 1
                        for cepage in cepages:
                            if isinstance(cepage, str) and cepage.strip():
                                normalization_stats['total_cepages_normalized'] += 1
                                normalization_stats['unique_varieties_global'].add(cepage)
                    
                    # Count wine types
                    wine_type = wine.get('type')
                    if wine_type and isinstance(wine_type, str):
                        normalization_stats['total_wine_types_normalized'] += 1
                        normalization_stats['unique_wine_types_global'].add(wine_type)
    
    print(f"✅ Normalized {len(normalized_producers)} wine producers")
    
    # Analyze final dataset quality
    print(f"\n📈 Final Dataset Quality:")
    complete_records = 0
    has_website = 0
    has_location = 0
    has_wines = 0
    
    for producer in normalized_producers:
        is_complete = all([
            producer.get('classification'),
            producer.get('latitude') is not None,
            producer.get('longitude') is not None
        ])
        
        if is_complete:
            complete_records += 1
        
        if producer.get('website'):
            has_website += 1
            
        if producer.get('latitude') is not None:
            has_location += 1
            
        if producer.get('wines'):
            has_wines += 1
    
    total_wine = len(normalized_producers)
    print(f"  Complete records:       {complete_records} ({complete_records/total_wine*100:.1f}%)")
    print(f"  With website:           {has_website} ({has_website/total_wine*100:.1f}%)")
    print(f"  With location:          {has_location} ({has_location/total_wine*100:.1f}%)")
    print(f"  With wines:             {has_wines} ({has_wines/total_wine*100:.1f}%)")
    
    # Print normalization statistics
    print(f"\n📊 Normalization Results:")
    print(f"  Producers with wines:        {normalization_stats['producers_with_wines']}")
    print(f"  Total wines:                 {normalization_stats['total_wines']}")
    print(f"  Wines with cépages:          {normalization_stats['total_wines_with_cepages']}")
    print(f"  Total cépages normalized:    {normalization_stats['total_cepages_normalized']}")
    print(f"  Total wine types normalized: {normalization_stats['total_wine_types_normalized']}")
    print(f"  Unique grape varieties:      {len(normalization_stats['unique_varieties_global'])}")
    print(f"  Unique wine types:           {len(normalization_stats['unique_wine_types_global'])}")
    
    # Show averages
    if normalization_stats['producers_with_wines'] > 0:
        avg_wines_per_producer = normalization_stats['total_wines'] / normalization_stats['producers_with_wines']
        print(f"  Avg wines per producer:      {avg_wines_per_producer:.1f}")
        
    if normalization_stats['total_wines_with_cepages'] > 0:
        avg_cepages_per_wine = normalization_stats['total_cepages_normalized'] / normalization_stats['total_wines_with_cepages']
        print(f"  Avg cépages per wine:        {avg_cepages_per_wine:.1f}")
    
    # Save final dataset
    output_file = Path("data/05_wine_producers_final_normalized.jsonl")
    print(f"\n💾 Saving to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for producer in normalized_producers:
            json.dump(producer, f, ensure_ascii=False)
            f.write('\n')
    
    print(f"✅ Final normalized dataset created!")
    print(f"   Input:  {len(producers)} total producers")
    print(f"   Output: {len(normalized_producers)} wine producers (normalized)")
    print(f"   File:   {output_file}")
    
    return output_file


if __name__ == "__main__":
    create_final_normalized_dataset()