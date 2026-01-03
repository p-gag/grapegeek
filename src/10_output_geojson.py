#!/usr/bin/env python3
"""
GeoJSON Output Generator for Wine Producers

Converts the final normalized wine producer dataset to GeoJSON format for 
interactive map visualization with geographic filtering and variety analysis.

PURPOSE: GeoJSON Export - Convert final dataset to interactive map format

INPUTS:
- data/05_wine_producers_final_normalized.jsonl (final production dataset)

OUTPUTS:
- docs/assets/data/wine-producers-final.geojson (interactive map data)

DEPENDENCIES:
- None (uses normalized data from final dataset)

USAGE:
# Generate GeoJSON for interactive map
uv run src/10_output_geojson.py

FUNCTIONALITY:
- Converts normalized wine producer data to GeoJSON format
- Includes wine data with pre-normalized grape varieties and wine types
- Generates comprehensive metadata and statistics
- Creates feature properties for interactive map filtering
- Provides location coverage analysis and variety statistics
- Outputs ready-to-use map data for MkDocs site
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set






def create_final_geojson():
    """Convert final3 wine producers dataset to GeoJSON."""
    input_file = Path("data/05_wine_producers_final_normalized.jsonl")
    output_file = Path("docs/assets/data/wine-producers-final.geojson")
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return
    
    print("🗺️  Converting final3 wine producers to GeoJSON...")
    print("   (Grape varieties and wine types are already normalized in final3 data)")
    
    features = []
    stats = {
        'total': 0,
        'with_location': 0,
        'with_wines': 0,
        'open_for_visits': 0,
        'states': {},
        'grape_varieties': defaultdict(int),
        'wine_types': defaultdict(int),
        'total_wines': 0,
        'total_wines_with_cepages': 0,
        'total_cepages': 0,
        'producers_with_cepages': 0,
        'unique_varieties_global': set()
    }
    
    # Process each producer
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
                
            try:
                producer = json.loads(line.strip())
                stats['total'] += 1
                
                # Extract basic info
                state = producer.get('state_province', 'Unknown')
                stats['states'][state] = stats['states'].get(state, 0) + 1
                
                # Extract wine data (grape varieties and wine types are already normalized in final3 data)
                wines = producer.get('wines', []) or []
                grape_varieties = set()
                wine_types = set()
                producer_cepage_count = 0
                producer_unique_varieties = set()
                wines_with_cepages_count = 0
                
                # Count wines
                if wines:
                    stats['with_wines'] += 1
                    stats['total_wines'] += len(wines)
                
                for wine in wines:
                    wine_has_cepages = False
                    
                    # Extract already-normalized grape varieties (cépages)
                    cepages = wine.get('cepages', []) or []
                    for cepage in cepages:
                        if cepage and isinstance(cepage, str):
                            grape_varieties.add(cepage)
                            producer_unique_varieties.add(cepage)
                            stats['unique_varieties_global'].add(cepage)
                            producer_cepage_count += 1
                            wine_has_cepages = True
                    
                    if wine_has_cepages:
                        wines_with_cepages_count += 1
                    
                    # Extract already-normalized wine type
                    wine_type = wine.get('type')
                    if wine_type and isinstance(wine_type, str):
                        wine_types.add(wine_type)
                        stats['wine_types'][wine_type] += 1
                
                # Update producer-level stats
                if producer_unique_varieties:
                    stats['producers_with_cepages'] += 1
                
                # Count grape varieties for this producer
                for variety in producer_unique_varieties:
                    stats['grape_varieties'][variety] += 1
                    
                # Update global stats
                stats['total_cepages'] += producer_cepage_count
                stats['total_wines_with_cepages'] += wines_with_cepages_count
                
                # Visiting information
                activities = producer.get('activities', []) or []
                open_for_visits = bool(activities)
                if open_for_visits:
                    stats['open_for_visits'] += 1
                
                # Skip if no coordinates
                lat = producer.get('latitude')
                lon = producer.get('longitude')
                
                if lat is None or lon is None:
                    continue
                    
                stats['with_location'] += 1
                
                # Create GeoJSON feature
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "permit_id": producer.get('permit_id'),
                        "name": producer.get('business_name', producer.get('name', 'Unknown')),
                        "address": producer.get('address'),
                        "city": producer.get('city'),
                        "state_province": producer.get('state_province'),
                        "country": producer.get('country'),
                        "postal_code": producer.get('postal_code'),
                        "classification": producer.get('classification'),
                        "website": producer.get('website'),
                        "social_media": producer.get('social_media'),
                        "wine_label": producer.get('wine_label'),
                        "activities": activities,
                        "open_for_visits": open_for_visits,
                        "verified_wine_producer": producer.get('verified_wine_producer'),
                        "geocoding_method": producer.get('geocoding_method'),
                        "source": producer.get('source'),
                        "enriched_at": producer.get('enriched_at'),
                        "grape_varieties": sorted(list(grape_varieties)),
                        "wine_types": sorted(list(wine_types)),
                        "wines": wines
                    }
                }
                
                features.append(feature)
                
            except json.JSONDecodeError as e:
                print(f"⚠️  Error parsing line: {e}")
                continue
    
    # Create GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "generated_at": "2025-12-20",
            "total_producers": stats['total'],
            "mapped_producers": stats['with_location'],
            "producers_with_wines": stats['with_wines'],
            "open_for_visits": stats['open_for_visits'],
            "coverage": f"{stats['with_location']/stats['total']*100:.1f}%",
            "states": dict(sorted(stats['states'].items())),
            "grape_varieties": {variety: count for variety, count in sorted(stats['grape_varieties'].items())},
            "grape_varieties_with_counts": {variety: f"{variety} ({count})" for variety, count in sorted(stats['grape_varieties'].items())},
            "wine_types": dict(sorted(stats['wine_types'].items()))
        }
    }
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save GeoJSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    
    print(f"✅ GeoJSON created: {output_file}")
    print(f"   Total producers: {stats['total']}")
    print(f"   Mapped producers: {stats['with_location']}")
    print(f"   With wine data: {stats['with_wines']}")
    print(f"   Open for visits: {stats['open_for_visits']}")
    
    # Safe division for coverage
    coverage = (stats['with_location']/stats['total']*100) if stats['total'] > 0 else 0
    print(f"   Coverage: {coverage:.1f}%")
    
    print(f"\n📊 Wine & Variety Statistics:")
    print(f"   Total wines: {stats['total_wines']}")
    print(f"   Wines with cépages: {stats['total_wines_with_cepages']}")
    print(f"   Producers with cépages: {stats['producers_with_cepages']}")
    print(f"   Total cépages mentions: {stats['total_cepages']}")
    print(f"   Unique grape varieties: {len(stats['unique_varieties_global'])}")
    print(f"   Unique wine types: {len(stats['wine_types'])}")
    
    # Safe division for averages
    if stats['producers_with_cepages'] > 0:
        avg_cepages_per_producer = stats['total_cepages'] / stats['producers_with_cepages']
        print(f"   Avg cépages per producer: {avg_cepages_per_producer:.1f}")
        
    if stats['total_wines_with_cepages'] > 0:
        avg_cepages_per_wine = stats['total_cepages'] / stats['total_wines_with_cepages']
        print(f"   Avg cépages per wine: {avg_cepages_per_wine:.1f}")
    
    # Show top varieties and wine types
    print(f"\nTop 10 Grape Varieties:")
    for variety, count in sorted(stats['grape_varieties'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {variety}: {count}")
        
    print(f"\nWine Types:")
    for wine_type, count in sorted(stats['wine_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {wine_type}: {count}")
        
    # Producer breakdown by state/province
    print(f"\nProducers by State/Province:")
    for state, count in sorted(stats['states'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {state}: {count}")

if __name__ == "__main__":
    create_final_geojson()