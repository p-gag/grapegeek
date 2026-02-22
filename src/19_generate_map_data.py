#!/usr/bin/env python3
"""
Producer Map Data Generator for React-Leaflet

Generates optimized JSON data for wine producer maps to be consumed by React-Leaflet.
Transforms existing GeoJSON data into React-optimized format with variety filtering.

PURPOSE: Data Transformation - Generate map data for React-Leaflet consumption

INPUTS:
- data/wine-producers-final.geojson

OUTPUTS:
- grape-explorer-react/src/data/map-data.json (map data for React-Leaflet)

USAGE:
# Generate map data for React-Leaflet
uv run src/19_generate_map_data.py

# Output to specific location
uv run src/19_generate_map_data.py --output custom_path.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass


@dataclass
class ProducerFeature:
    """Represents a wine producer feature optimized for React."""
    id: str
    name: str
    coordinates: List[float]  # [lng, lat]
    city: str
    state_province: str
    country: str
    grape_varieties: List[str]
    wine_types: List[str]
    website: Optional[str] = None
    social_media: List[str] = None
    activities: List[str] = None
    open_for_visits: bool = False
    wine_label: Optional[str] = None


class MapDataGenerator:
    """Generates map data for wine producers for React-Leaflet consumption."""
    
    # Country to ISO code mapping for flag icons (subset from tree generator)
    COUNTRY_FLAGS = {
        'CA': 'ca',
        'US': 'us',
        'CANADA': 'ca',
        'USA': 'us',
        'UNITED STATES': 'us',
        'FRANCE': 'fr',
        'GERMANY': 'de',
        'ITALY': 'it',
        'SPAIN': 'es',
        'PORTUGAL': 'pt',
        'AUSTRIA': 'at',
        'SWITZERLAND': 'ch',
    }
    
    def __init__(self, geojson_path: str = "data/wine-producers-final.geojson"):
        self.geojson_path = Path(geojson_path)
        self.raw_features = []
        self.processed_features: List[ProducerFeature] = []
        self.grape_varieties: Set[str] = set()
        self.wine_types: Set[str] = set()
        self.states_provinces: Set[str] = set()
    
    def load_geojson_data(self):
        """Load and parse the GeoJSON file."""
        if not self.geojson_path.exists():
            raise FileNotFoundError(f"GeoJSON file not found: {self.geojson_path}")
        
        print(f"📍 Loading GeoJSON data from {self.geojson_path}")
        
        with open(self.geojson_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        if geojson_data.get('type') != 'FeatureCollection':
            raise ValueError("Invalid GeoJSON: expected FeatureCollection")
        
        self.raw_features = geojson_data.get('features', [])
        print(f"📊 Loaded {len(self.raw_features)} producer features")
    
    def process_features(self):
        """Process raw GeoJSON features into optimized React format."""
        print("🔄 Processing features for React optimization...")
        
        processed_count = 0
        skipped_count = 0
        
        for feature in self.raw_features:
            try:
                processed_feature = self._process_single_feature(feature)
                if processed_feature:
                    self.processed_features.append(processed_feature)
                    processed_count += 1
                    
                    # Collect metadata for filters
                    self.grape_varieties.update(processed_feature.grape_varieties)
                    self.wine_types.update(processed_feature.wine_types)
                    self.states_provinces.add(processed_feature.state_province)
                else:
                    skipped_count += 1
            except Exception as e:
                print(f"⚠️ Error processing feature {feature.get('properties', {}).get('name', 'unknown')}: {e}")
                skipped_count += 1
        
        print(f"✅ Processed {processed_count} features, skipped {skipped_count}")
        print(f"📊 Found {len(self.grape_varieties)} unique grape varieties")
        print(f"📊 Found {len(self.wine_types)} unique wine types")
        print(f"📊 Found {len(self.states_provinces)} unique states/provinces")
    
    def _process_single_feature(self, feature: dict) -> Optional[ProducerFeature]:
        """Process a single GeoJSON feature into a ProducerFeature."""
        geometry = feature.get('geometry', {})
        properties = feature.get('properties', {})
        
        # Validate required fields
        if geometry.get('type') != 'Point':
            return None
        
        coordinates = geometry.get('coordinates')
        if not coordinates or len(coordinates) != 2:
            return None
        
        name = properties.get('name')
        if not name:
            return None
        
        # Extract and validate data
        try:
            processed_feature = ProducerFeature(
                id=properties.get('permit_id', f"producer_{hash(name)}"),
                name=name,
                coordinates=coordinates,  # [lng, lat] format for Leaflet
                city=properties.get('city', 'Unknown'),
                state_province=properties.get('state_province', 'Unknown'),
                country=properties.get('country', 'Unknown'),
                grape_varieties=properties.get('grape_varieties', []) or [],
                wine_types=properties.get('wine_types', []) or [],
                website=properties.get('website'),
                social_media=properties.get('social_media', []) or [],
                activities=properties.get('activities', []) or [],
                open_for_visits=bool(properties.get('open_for_visits', False)),
                wine_label=properties.get('wine_label')
            )
            
            return processed_feature
            
        except Exception as e:
            print(f"⚠️ Error creating ProducerFeature: {e}")
            return None
    
    def generate_variety_map_data(self, variety_name: str) -> Dict[str, Any]:
        """Generate map data filtered for a specific grape variety."""
        if not variety_name:
            return self.generate_full_map_data()
        
        # Filter producers that grow this variety
        variety_producers = []
        for producer in self.processed_features:
            if variety_name in producer.grape_varieties:
                variety_producers.append(producer)
        
        print(f"🍇 Found {len(variety_producers)} producers growing {variety_name}")
        
        return {
            'variety_name': variety_name,
            'producer_count': len(variety_producers),
            'producers': [self._producer_to_dict(p) for p in variety_producers],
            'center': self._calculate_center(variety_producers),
            'bounds': self._calculate_bounds(variety_producers)
        }
    
    def generate_full_map_data(self) -> Dict[str, Any]:
        """Generate complete map data with all producers and filter options."""
        return {
            'producer_count': len(self.processed_features),
            'producers': [self._producer_to_dict(p) for p in self.processed_features],
            'filter_options': {
                'grape_varieties': sorted(list(self.grape_varieties)),
                'wine_types': sorted(list(self.wine_types)),
                'states_provinces': sorted(list(self.states_provinces))
            },
            'center': self._calculate_center(self.processed_features),
            'bounds': self._calculate_bounds(self.processed_features),
            'country_flags': self.COUNTRY_FLAGS
        }
    
    def _producer_to_dict(self, producer: ProducerFeature) -> Dict[str, Any]:
        """Convert ProducerFeature to dictionary for JSON serialization."""
        return {
            'id': producer.id,
            'name': producer.name,
            'coordinates': producer.coordinates,
            'city': producer.city,
            'state_province': producer.state_province,
            'country': producer.country,
            'country_code': self.COUNTRY_FLAGS.get(producer.country.upper(), producer.country.lower() if producer.country else ''),
            'grape_varieties': producer.grape_varieties,
            'wine_types': producer.wine_types,
            'website': producer.website,
            'social_media': producer.social_media or [],
            'activities': producer.activities or [],
            'open_for_visits': producer.open_for_visits,
            'wine_label': producer.wine_label
        }
    
    def _calculate_center(self, producers: List[ProducerFeature]) -> List[float]:
        """Calculate center point for a list of producers."""
        if not producers:
            return [-85.0, 45.0]  # North America default
        
        total_lat = sum(p.coordinates[1] for p in producers)
        total_lng = sum(p.coordinates[0] for p in producers)
        count = len(producers)
        
        return [total_lng / count, total_lat / count]  # [lng, lat]
    
    def _calculate_bounds(self, producers: List[ProducerFeature]) -> Dict[str, List[float]]:
        """Calculate bounding box for a list of producers."""
        if not producers:
            return {
                'southwest': [-130.0, 20.0],
                'northeast': [-50.0, 70.0]
            }
        
        lats = [p.coordinates[1] for p in producers]
        lngs = [p.coordinates[0] for p in producers]
        
        return {
            'southwest': [min(lngs), min(lats)],
            'northeast': [max(lngs), max(lats)]
        }
    
    def generate_unified_data(self) -> Dict[str, Any]:
        """Generate unified map data including variety-specific subsets."""
        print("🗺️ Generating unified map data...")
        
        # Full dataset
        full_data = self.generate_full_map_data()
        
        # Get top varieties for pre-generation (varieties with most producers)
        variety_counts = {}
        for producer in self.processed_features:
            for variety in producer.grape_varieties:
                variety_counts[variety] = variety_counts.get(variety, 0) + 1
        
        # Sort by producer count, take top 20
        top_varieties = sorted(variety_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        variety_data = {}
        for variety_name, count in top_varieties:
            print(f"📊 Pre-generating data for {variety_name} ({count} producers)")
            variety_data[variety_name] = self.generate_variety_map_data(variety_name)
        
        return {
            'full_map': full_data,
            'varieties': variety_data,
            'statistics': {
                'total_producers': len(self.processed_features),
                'total_varieties': len(self.grape_varieties),
                'total_wine_types': len(self.wine_types),
                'total_regions': len(self.states_provinces)
            }
        }
    
    def generate_data_file(self, output_path: str = "grapegeek-nextjs/public/data/map-data.json"):
        """Generate the JSON data file for React-Leaflet."""
        print("🔧 Generating map data...")
        
        # Load and process data
        self.load_geojson_data()
        self.process_features()
        
        # Generate unified data structure
        map_data = self.generate_unified_data()
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Writing JSON data to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(map_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Map data generated: {output_file}")
        print(f"📊 Total producers: {map_data['statistics']['total_producers']}")
        print(f"📊 Total varieties: {map_data['statistics']['total_varieties']}")
        print(f"📊 Pre-generated variety maps: {len(map_data['varieties'])}")
        
        return output_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate wine producer map data for React-Leaflet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/19_generate_map_data.py                           # Generate to grapegeek-nextjs/public/data/map-data.json
  python src/19_generate_map_data.py --output custom.json     # Custom output path
  python src/19_generate_map_data.py --geojson custom.geojson # Custom input GeoJSON
        """
    )

    parser.add_argument(
        "--output",
        default="grapegeek-nextjs/public/data/map-data.json",
        help="Output JSON file path (default: grapegeek-nextjs/public/data/map-data.json)"
    )
    
    parser.add_argument(
        "--geojson",
        default="data/wine-producers-final.geojson",
        help="Input GeoJSON file path (default: data/wine-producers-final.geojson)"
    )
    
    args = parser.parse_args()
    
    try:
        generator = MapDataGenerator(args.geojson)
        output_file = generator.generate_data_file(args.output)
        
        print(f"\n📁 Data file ready for React-Leaflet:")
        print(f"{output_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()