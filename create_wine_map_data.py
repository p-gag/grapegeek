#!/usr/bin/env python3
"""
Quebec Wine Map Data Generator

Converts enhanced wine producer data into GeoJSON format for interactive map.
Uses OpenStreetMap Nominatim API for geocoding addresses.
"""

import json
import re
import time
import requests
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import quote


class WineMapDataGenerator:
    """Generates GeoJSON data for Quebec wine map from enhanced producer data."""
    
    def __init__(self, 
                 input_file: str = "data/racj/racj-alcool-fabricant_enhanced.json",
                 output_file: str = "docs/assets/data/quebec-wineries.geojson",
                 grape_mapping_file: str = "data/grape_variety_mapping.yaml",
                 wine_type_mapping_file: str = "data/wine_type_mapping.yaml"):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.grape_mapping_file = Path(grape_mapping_file)
        self.wine_type_mapping_file = Path(wine_type_mapping_file)
        
        # Load grape variety and wine type mappings
        self.grape_mapping = self.load_grape_mapping()
        self.wine_type_mapping = self.load_wine_type_mapping()
        
        # Nominatim API settings (free OpenStreetMap geocoding)
        self.nominatim_base = "https://nominatim.openstreetmap.org/search"
        self.user_agent = "GrapeGeek-Quebec-Wine-Map/1.0"
        
        # Rate limiting for API calls
        self.request_delay = 1.1  # Nominatim requires >1 second between requests
        
        # Cache for geocoded addresses
        self.geocode_cache = {}
        
        # Load existing geocoding cache from previous GeoJSON output
        self.load_existing_geocoding_cache()
    
    def load_grape_mapping(self) -> Dict[str, str]:
        """Load grape variety normalization mapping."""
        if not self.grape_mapping_file.exists():
            print(f"⚠️  Grape mapping file not found: {self.grape_mapping_file}")
            return {}
        
        try:
            with open(self.grape_mapping_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                mapping = data.get('grape_variety_mapping', {})
                
                # Create reverse mapping from lowercase aliases to official names
                alias_to_official = {}
                for official_name, info in mapping.items():
                    aliases = info.get('aliases', [])
                    for alias in aliases:
                        alias_to_official[alias.lower()] = official_name
                
                print(f"🍇 Loaded {len(alias_to_official)} grape variety aliases for {len(mapping)} official varieties")
                return alias_to_official
                
        except Exception as e:
            print(f"❌ Error loading grape mapping: {str(e)}")
            return {}
    
    def load_existing_geocoding_cache(self) -> None:
        """Load existing geocoding cache from previous GeoJSON output."""
        if not self.output_file.exists():
            print("🔍 No existing GeoJSON found, starting with empty geocoding cache")
            return
            
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
                
            features = geojson_data.get('features', [])
            cache_hits = 0
            
            for feature in features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                coordinates = geometry.get('coordinates', [])
                
                if len(coordinates) == 2 and properties.get('address') and properties.get('city'):
                    address = properties['address']
                    city = properties['city']
                    province = "Quebec"
                    
                    # Create the same cache key format as geocode_address method
                    cache_key = f"{address}, {city}, {province}".strip()
                    
                    # GeoJSON uses [longitude, latitude], convert to (latitude, longitude)
                    lon, lat = coordinates
                    self.geocode_cache[cache_key] = (lat, lon)
                    cache_hits += 1
            
            print(f"📍 Loaded {cache_hits} cached geocoding results from existing GeoJSON")
            
        except Exception as e:
            print(f"⚠️  Error loading existing geocoding cache: {str(e)}")
            print("🔍 Starting with empty geocoding cache")
    
    def load_wine_type_mapping(self) -> Dict[str, str]:
        """Load wine type normalization mapping."""
        if not self.wine_type_mapping_file.exists():
            print(f"⚠️  Wine type mapping file not found: {self.wine_type_mapping_file}")
            return {}
        
        try:
            with open(self.wine_type_mapping_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                mapping = data.get('wine_type_mapping', {})
                
                # Create reverse mapping from lowercase aliases to official names
                alias_to_official = {}
                for official_name, info in mapping.items():
                    aliases = info.get('aliases', [])
                    for alias in aliases:
                        alias_to_official[alias.lower()] = official_name
                
                print(f"🍷 Loaded {len(alias_to_official)} wine type aliases for {len(mapping)} official types")
                return alias_to_official
                
        except Exception as e:
            print(f"❌ Error loading wine type mapping: {str(e)}")
            return {}
    
    def normalize_grape_variety(self, variety: str) -> str:
        """Normalize a grape variety name using the mapping."""
        if not variety or not variety.strip():
            return variety
        
        # Lowercase lookup
        normalized_key = variety.strip().lower()
        return self.grape_mapping.get(normalized_key, variety.strip())
    
    def normalize_wine_type(self, wine_type: str) -> str:
        """Normalize a wine type name using the mapping."""
        if not wine_type or not wine_type.strip():
            return wine_type
        
        # Lowercase lookup
        normalized_key = wine_type.strip().lower()
        return self.wine_type_mapping.get(normalized_key, wine_type.strip())
    
    def clean_address(self, address: str) -> str:
        """Clean address by extracting only the first civic number when multiple numbers exist."""
        if not address or not address.strip():
            return address
        
        # Pattern to match addresses like "220 ET 239" or "123 & 125" or "100 et 110"
        # Captures the first number and everything after the connector
        pattern = r'^(\d+)\s*(?:ET|et|&|AND|and)\s*\d+(.*)$'
        
        match = re.match(pattern, address.strip())
        if match:
            # Return first number + rest of address (street name, etc.)
            first_number = match.group(1)
            rest_of_address = match.group(2)
            cleaned = f"{first_number}{rest_of_address}".strip()
            print(f"  Cleaned address: '{address}' → '{cleaned}'")
            return cleaned
        
        return address.strip()
        
    def load_enhanced_data(self) -> Dict[str, Any]:
        """Load the enhanced wine producers data."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Enhanced data file not found: {self.input_file}")
            
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def geocode_address(self, address: str, city: str, province: str = "Quebec") -> Optional[Tuple[float, float]]:
        """
        Geocode an address using OpenStreetMap Nominatim API.
        
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        # Clean address to handle multiple civic numbers
        cleaned_address = self.clean_address(address)
        
        # Create cache key and query string
        cache_key = f"{cleaned_address}, {city}, {province}".strip()
        query_parts = [cleaned_address, city, province, "Canada"]
        query = ", ".join(part.strip() for part in query_parts if part.strip())
        
        if cache_key in self.geocode_cache:
            cached_result = self.geocode_cache[cache_key]
            if cached_result:
                lat, lon = cached_result
                print(f"  Using cached: {query} → {lat:.4f}, {lon:.4f}")
            else:
                print(f"  Using cached: {query} → (failed)")
            return cached_result
        
        # Make API request
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'ca',  # Canada only
            'bounded': 1,
            'viewbox': '-84.0,43.0,-55.0,53.0',  # Expanded Quebec bounding box
        }
        
        headers = {
            'User-Agent': self.user_agent
        }
        
        try:
            print(f"  Geocoding: {query}")
            time.sleep(self.request_delay) # Rate limiting only when doing the call
            response = requests.get(self.nominatim_base, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                
                # Validate coordinates are in expanded Quebec bounds
                if 43.0 <= lat <= 53.0 and -84.0 <= lon <= -55.0:
                    coords = (lat, lon)
                    self.geocode_cache[cache_key] = coords
                    print(f"    → {lat:.4f}, {lon:.4f}")
                    return coords
                else:
                    print(f"    → Coordinates outside Quebec bounds: {lat}, {lon}")
            else:
                print(f"    → No results found")
                
        except Exception as e:
            print(f"    → Geocoding error: {e}")
            
        # Fallback: try without street address, just city + province
        if cleaned_address.strip():
            print(f"  Fallback: trying city only...")
            fallback_query = f"{city}, {province}, Canada"
            
            try:
                time.sleep(self.request_delay)
                
                fallback_params = {
                    'q': fallback_query,
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'ca',
                    'bounded': 1,
                    'viewbox': '-84.0,43.0,-55.0,53.0',
                }
                
                response = requests.get('https://nominatim.openstreetmap.org/search', 
                                      params=fallback_params, 
                                      headers={'User-Agent': self.user_agent}, 
                                      timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if data and len(data) > 0:
                    result = data[0]
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    
                    if 43.0 <= lat <= 53.0 and -84.0 <= lon <= -55.0:
                        coords = (lat, lon)
                        self.geocode_cache[cache_key] = coords
                        print(f"    → City fallback: {lat:.4f}, {lon:.4f}")
                        return coords
                    else:
                        print(f"    → City fallback outside bounds: {lat:.4f}, {lon:.4f}")
                else:
                    print("    → City fallback: No results found")
                    
            except Exception as e:
                print(f"    → City fallback error: {str(e)}")
        
        # Cache failed attempts to avoid repeated API calls
        self.geocode_cache[cache_key] = None
        return None
    
    def create_feature(self, producer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a GeoJSON feature from a producer record."""
        # Extract basic info
        name = producer.get('RaisonSociale', '')
        wine_label = producer.get('wine_label')
        city = producer.get('Ville', '')
        address = producer.get('AdresseEtabl', '')
        website = producer.get('website')
        wines = producer.get('wines', [])
        
        if not name or not city:
            return None
        
        # Geocode the address
        coords = self.geocode_address(address, city)
        if not coords:
            return None
        
        lat, lon = coords
        
        # Extract all unique cépages from wines
        all_cepages = set()
        wine_types = set()
        
        for wine in wines:
            cepages = wine.get('cepages', [])
            if isinstance(cepages, list):
                # Normalize each grape variety
                normalized_cepages = [self.normalize_grape_variety(cepage) for cepage in cepages]
                all_cepages.update(normalized_cepages)
            wine_type = wine.get('type', '')
            if wine_type:
                # Normalize wine type
                normalized_wine_type = self.normalize_wine_type(wine_type)
                wine_types.add(normalized_wine_type)
        
        # Administrative region mapping (simplified)
        region_mapping = {
            # Montérégie
            'DUNHAM': 'Montérégie', 'FRELIGHSBURG': 'Montérégie', 'SUTTON': 'Montérégie',
            'ROUGEMONT': 'Montérégie', 'SAINT-PAUL-D\'ABBOTSFORD': 'Montérégie',
            'MARIEVILLE': 'Montérégie', 'SAINTE-BARBE': 'Montérégie',
            
            # Cantons-de-l'Est (Eastern Townships)
            'SHERBROOKE': 'Cantons-de-l\'Est', 'GRANBY': 'Cantons-de-l\'Est',
            'COOKSHIRE-EATON': 'Cantons-de-l\'Est', 'SHEFFORD': 'Cantons-de-l\'Est',
            'LAC-BROME': 'Cantons-de-l\'Est', 'BROMONT': 'Cantons-de-l\'Est',
            
            # Lanaudière  
            'JOLIETTE': 'Lanaudière', 'RAWDON': 'Lanaudière', 'SAINT-JEAN-DE-MATHA': 'Lanaudière',
            
            # Laurentides
            'SAINTE-AGATHE-DES-MONTS': 'Laurentides', 'VAL-MORIN': 'Laurentides',
            'PRÉVOST': 'Laurentides', 'SAINT-JÉRÔME': 'Laurentides',
            
            # Other regions
            'QUÉBEC': 'Capitale-Nationale', 'LAVAL': 'Laval', 
            'MONTRÉAL': 'Montréal', 'GATINEAU': 'Outaouais'
        }
        
        region = region_mapping.get(city.upper(), 'Autre')
        
        # Create GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]  # GeoJSON uses [longitude, latitude]
            },
            "properties": {
                "name": name,
                "wine_label": wine_label,
                "city": city,
                "region": region,
                "address": address,
                "website": website,
                "cepages": sorted(list(all_cepages)),
                "wine_types": sorted(list(wine_types)),
                "wine_count": len(wines),
                "wines": wines[:5] if wines else []  # Limit to first 5 wines for performance
            }
        }
        
        return feature
    
    def generate_geojson(self) -> Dict[str, Any]:
        """Generate GeoJSON from enhanced producer data."""
        print("🍷 Generating Quebec Wine Map Data")
        print("=" * 50)
        
        # Load data
        data = self.load_enhanced_data()
        producers = data.get('wine_producers', [])
        
        print(f"Processing {len(producers)} wine producers...")
        
        # Process each producer
        features = []
        successful = 0
        failed = 0
        
        for i, producer in enumerate(producers, 1):
            name = producer.get('RaisonSociale', f'Producer {i}')
            city = producer.get('Ville', '')
            
            print(f"\n[{i}/{len(producers)}] {name} ({city})")
            
            feature = self.create_feature(producer)
            if feature:
                features.append(feature)
                successful += 1
            else:
                failed += 1
                
        # Create GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "metadata": {
                "title": "Quebec Wine Producers",
                "description": "Artisanal wine producers in Quebec with cépages information",
                "generated_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": str(self.input_file),
                "total_producers": len(producers),
                "geocoded_successfully": successful,
                "geocoding_failed": failed
            },
            "features": features
        }
        
        print(f"\n=== Results ===")
        print(f"Total producers: {len(producers)}")
        print(f"Successfully geocoded: {successful}")
        print(f"Failed geocoding: {failed}")
        print(f"Success rate: {successful/len(producers)*100:.1f}%")
        
        return geojson
    
    def save_geojson(self, geojson: Dict[str, Any]) -> None:
        """Save GeoJSON to file."""
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 GeoJSON saved to: {self.output_file}")
        
        # Print some statistics
        features = geojson.get('features', [])
        if features:
            all_cepages = set()
            for feature in features:
                cepages = feature.get('properties', {}).get('cepages', [])
                all_cepages.update(cepages)
            
            print(f"📊 Map will show {len(features)} wineries")
            print(f"🍇 Cépages found: {len(all_cepages)}")
            print(f"🎯 Popular cépages: {', '.join(sorted(list(all_cepages))[:8])}")
    
    def run(self) -> bool:
        """Execute the full workflow."""
        try:
            geojson = self.generate_geojson()
            self.save_geojson(geojson)
            return True
        except Exception as e:
            print(f"❌ Error generating wine map data: {e}")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate GeoJSON data for Quebec wine map')
    parser.add_argument('--input', type=str, 
                       default='data/racj/racj-alcool-fabricant_enhanced.json',
                       help='Input enhanced producers JSON file')
    parser.add_argument('--output', type=str, 
                       default='docs/assets/data/quebec-wineries.geojson',
                       help='Output GeoJSON file')
    
    args = parser.parse_args()
    
    generator = WineMapDataGenerator(input_file=args.input, output_file=args.output)
    
    if generator.run():
        print(f"\n✅ Successfully generated Quebec wine map data")
        return 0
    else:
        print("❌ Failed to generate wine map data")
        return 1


if __name__ == "__main__":
    exit(main())