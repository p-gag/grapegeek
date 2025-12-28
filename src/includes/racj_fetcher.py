#!/usr/bin/env python3
"""
RACJ (Quebec) Producer Fetcher

Extracted from 00_quebec_fetch.py for use in unified producer fetch pipeline.
Fetches and processes Quebec wine producers from RACJ permits data.
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, TypedDict


class PermitDetail(TypedDict):
    """Type definition for a permit detail within a fabricant record."""
    No: str                 # Permit number
    Catgrs: List[str]       # Product categories list
    Adrs: str              # Address
    CdVl: str              # City code
    Ville: str             # City name
    CP: str                # Postal code


class FabricantRecord(TypedDict):
    """Type definition for a fabricant (manufacturer) record."""
    Nom: str               # Business name
    Titlr: str             # Permit holder name  
    Neq: str               # Quebec Enterprise Number (NEQ)
    Permis: List[PermitDetail]  # List of permit details


class TypePermisGroup(TypedDict):
    """Type definition for a permit type group."""
    TypePermis: str                    # Type of alcohol permit
    Fabricants: List[FabricantRecord]  # List of fabricant records


class RACJDataStructure(TypedDict):
    """Type definition for the main RACJ data structure."""
    AlcoolFabricants: List[TypePermisGroup]  # List of permit type groups


class WineProducersMetadata(TypedDict):
    """Metadata for the filtered wine producers dataset."""
    source_url: str
    fetch_date: str
    raw_record_count: int
    wine_record_count: int
    filter_criteria: str
    wine_permit_types: Dict[str, int]


def fetch_quebec_producers(data_dir: str = "data/racj") -> Dict[str, Any]:
    """Fetch Quebec wine producers from RACJ data.
    
    Args:
        data_dir: Directory to save RACJ data files
        
    Returns:
        Dict with normalized producer data and metadata
    """
    fetcher = QuebecWineProducersFetcher(data_dir)
    
    # Fetch or load data
    if not fetcher.raw_file.exists():
        print("📥 Fetching fresh RACJ data...")
        if not fetcher.fetch_raw_data():
            return {"producers": [], "metadata": {"error": "Failed to fetch RACJ data"}}
    else:
        print(f"📁 Using existing RACJ data: {fetcher.raw_file}")
    
    # Process data
    return fetcher.process_wine_producers()


class QuebecWineProducersFetcher:
    """Fetches and processes Quebec wine producers from RACJ permits data."""
    
    def __init__(self, data_dir: str = "data/racj"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.source_url = "https://www.donneesquebec.ca/recherche/dataset/racj-alcool-fabricant/resource/6b143028-cb62-4f76-860c-6cf0eab8ea0b/download/racj-alcool-fabricant.json"
        self.raw_file = self.data_dir / "racj-alcool-fabricant.json"
        
    def fetch_raw_data(self) -> bool:
        """Download the raw RACJ permits JSON data."""
        try:
            print(f"Fetching data from: {self.source_url}")
            response = requests.get(self.source_url, timeout=30)
            response.raise_for_status()
            
            # Validate it's JSON
            json.loads(response.text)
            
            # Save raw data
            with open(self.raw_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
            print(f"Raw data saved to: {self.raw_file}")
            return True
            
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"Error fetching/parsing data: {e}")
            return False
    
    def load_raw_data(self) -> RACJDataStructure:
        """Load the raw JSON data."""
        if not self.raw_file.exists():
            raise FileNotFoundError(f"Raw data file not found: {self.raw_file}")
            
        with open(self.raw_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def is_wine_related_permit_type(self, type_permis: str) -> bool:
        """Check if a permit type is artisanal wine production."""
        return type_permis == 'Production artisanale de vin'
    
    def has_wine_categories(self, categories: List[str]) -> bool:
        """Check if permit categories include wine ('VIN')."""
        return 'VIN' in [cat.upper() for cat in categories]
    
    def normalize_fabricant_to_producer(self, fabricant: FabricantRecord, permit_detail: PermitDetail) -> Dict[str, Any]:
        """Convert a RACJ fabricant record to a normalized producer format."""
        return {
            'permit_id': permit_detail['No'],
            'source': 'RACJ',
            'country': 'CA',
            'state_province': 'Quebec',
            'business_name': fabricant['Nom'],
            'permit_holder': fabricant['Titlr'],
            'neq': fabricant['Neq'],
            'permit_categories': permit_detail['Catgrs'],
            'address': permit_detail['Adrs'],
            'city_code': permit_detail['CdVl'],
            'city': permit_detail['Ville'],
            'postal_code': permit_detail['CP'],
            'classification': None,
            'website': None,
            'social_media': None,
            'latitude': None,
            'longitude': None,
            'geocoding_method': None
        }
    
    def filter_wine_producers(self, data: RACJDataStructure) -> List[Dict[str, Any]]:
        """Filter the RACJ data to extract wine-related producers."""
        wine_producers = []
        wine_permit_types = {}
        
        for permit_group in data['AlcoolFabricants']:
            type_permis = permit_group['TypePermis']
            
            # Only process wine-related permit types
            if self.is_wine_related_permit_type(type_permis):
                wine_permit_types[type_permis] = wine_permit_types.get(type_permis, 0)
                
                for fabricant in permit_group['Fabricants']:
                    if 'Permis' not in fabricant:
                        continue
                    for permit_detail in fabricant['Permis']:
                        # Check if permit has wine categories
                        if self.has_wine_categories(permit_detail['Catgrs']):
                            producer = self.normalize_fabricant_to_producer(fabricant, permit_detail)
                            wine_producers.append(producer)
                            wine_permit_types[type_permis] += 1
        
        return wine_producers, wine_permit_types
    
    def process_wine_producers(self) -> Dict[str, Any]:
        """Process raw RACJ data and return wine producers with metadata."""
        raw_data = self.load_raw_data()
        wine_producers, wine_permit_types = self.filter_wine_producers(raw_data)
        
        # Count raw records
        raw_count = sum(len(group['Fabricants']) for group in raw_data['AlcoolFabricants'])
        
        # Create metadata
        metadata = {
            'source_url': self.source_url,
            'fetch_date': datetime.now().isoformat(),
            'raw_record_count': raw_count,
            'wine_record_count': len(wine_producers),
            'filter_criteria': "Production artisanale de vin with 'VIN' category",
            'wine_permit_types': wine_permit_types
        }
        
        print(f"Processed {len(wine_producers)} Quebec wine producers")
        
        return {
            'producers': wine_producers,
            'metadata': metadata
        }