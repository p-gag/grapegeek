#!/usr/bin/env python3
"""
Quebec Wine Producers Discovery from RACJ Permits

Fetches and filters the RACJ (Registre des titulaires de permis - fabricant d'alcool) 
dataset to extract wine-related permits from Quebec.

Source: https://www.donneesquebec.ca/recherche/dataset/racj-alcool-fabricant

Data Format:
The JSON contains an array of permit records, each with the following structure:
{
    "TypePermis": "Type of alcohol permit (e.g., 'Fabricant de vin', 'Production artisanale de vin')",
    "RaisonSociale": "Business name",
    "Titulaire": "Permit holder name", 
    "Neq": "Quebec Enterprise Number (NEQ)",
    "NoPermis": "Permit number (e.g., 'FV046', 'AV209')",
    "Categories": "Product categories (e.g., 'VIN', 'BIER', 'CID')",
    "AdresseEtabl": "Establishment address",
    "CodeVille": "City code",
    "Ville": "City name",
    "CodePostal": "Postal code"
}

Wine-related TypePermis values observed:
- "Production artisanale de vin" (Artisanal wine production)

Categories field can contain multiple values separated by commas, e.g., "BIER, CID, SPI, VIN"
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
    Titlr: str            # Permit holder name
    Neq: int              # Quebec Enterprise Number
    Permis: List[PermitDetail]  # List of permits


class TypePermisGroup(TypedDict):
    """Type definition for a permit type grouping."""
    TypePermis: str        # Type of alcohol permit (e.g., "Brasseur", "Fabricant de vin")
    Fabricants: List[FabricantRecord]  # List of manufacturers with this permit type


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


class QuebecWineProducersFetcher:
    """Fetches and processes Quebec wine producers from RACJ permits data."""
    
    def __init__(self, data_dir: str = "data/racj"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.source_url = "https://www.donneesquebec.ca/recherche/dataset/racj-alcool-fabricant/resource/6b143028-cb62-4f76-860c-6cf0eab8ea0b/download/racj-alcool-fabricant.json"
        self.raw_file = self.data_dir / "racj-alcool-fabricant.json"
        self.wine_file = self.data_dir / "racj-alcool-fabricant_vin.json"
        
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
    
    def extract_wine_records(self, data: RACJDataStructure) -> List[Dict[str, Any]]:
        """
        Extract wine-related records from the RACJ data structure.
        
        Returns a flattened list of wine producer records with the format:
        {
            "TypePermis": str,
            "RaisonSociale": str, 
            "Titulaire": str,
            "Neq": int,
            "NoPermis": str,
            "Categories": List[str],
            "AdresseEtabl": str,
            "CodeVille": str,
            "Ville": str,
            "CodePostal": str
        }
        """
        wine_records = []
        
        for permit_group in data['AlcoolFabricants']:
            type_permis = permit_group['TypePermis']
            is_wine_permit_type = self.is_wine_related_permit_type(type_permis)
            
            for fabricant in permit_group['Fabricants']:
                if 'Permis' not in fabricant:
                    continue
                for permit_detail in fabricant['Permis']:
                    # Include only if permit type is wine-related AND categories include VIN
                    if (is_wine_permit_type and 
                        self.has_wine_categories(permit_detail['Catgrs'])):
                        wine_record = {
                            'TypePermis': type_permis,
                            'RaisonSociale': fabricant['Nom'],
                            'Titulaire': fabricant['Titlr'],
                            'Neq': fabricant['Neq'],
                            'NoPermis': permit_detail['No'],
                            'Categories': permit_detail['Catgrs'],
                            'AdresseEtabl': permit_detail['Adrs'],
                            'CodeVille': permit_detail['CdVl'],
                            'Ville': permit_detail['Ville'],
                            'CodePostal': permit_detail['CP']
                        }
                        wine_records.append(wine_record)
        
        return wine_records
    
    def count_total_records(self, data: RACJDataStructure) -> int:
        """Count total number of permit records in the dataset."""
        total = 0
        for permit_group in data['AlcoolFabricants']:
            for fabricant in permit_group['Fabricants']:
                if 'Permis' in fabricant:
                    total += len(fabricant['Permis'])
        return total
    
    def analyze_wine_permit_types(self, wine_records: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze and count wine permit types."""
        permit_types = {}
        
        for record in wine_records:
            type_permis = record['TypePermis']
            permit_types[type_permis] = permit_types.get(type_permis, 0) + 1
        
        return permit_types
    
    def save_wine_data(self, wine_records: List[Dict[str, Any]], raw_count: int) -> None:
        """Save filtered wine data with comprehensive metadata."""
        permit_types = self.analyze_wine_permit_types(wine_records)
        
        metadata: WineProducersMetadata = {
            'source_url': self.source_url,
            'fetch_date': datetime.now().isoformat(),
            'raw_record_count': raw_count,
            'wine_record_count': len(wine_records),
            'filter_criteria': ('TypePermis equals "Production artisanale de vin" '
                               'AND Categories contains "VIN"'),
            'wine_permit_types': permit_types
        }
        
        output_data = {
            'metadata': metadata,
            'wine_producers': wine_records
        }
        
        with open(self.wine_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Wine producers data saved to: {self.wine_file}")
        print(f"Records: {raw_count} raw → {len(wine_records)} wine-related")
    
    def print_summary(self, wine_records: List[Dict[str, Any]]) -> None:
        """Print a comprehensive summary of wine producers data."""
        print("\n=== Quebec Wine Producers Summary ===")
        print(f"Total wine-related permits: {len(wine_records)}")
        
        permit_types = self.analyze_wine_permit_types(wine_records)
        print(f"\nWine permit types found:")
        for permit_type, count in sorted(permit_types.items()):
            print(f"  {permit_type}: {count}")
        
        # Sample some business names for context
        if wine_records:
            print(f"\nSample wine producers:")
            for i, record in enumerate(wine_records[:5]):
                business = record.get('RaisonSociale', 'Unknown')
                city = record.get('Ville', 'Unknown')
                permit_type = record.get('TypePermis', 'Unknown')
                categories = ', '.join(record.get('Categories', []))
                print(f"  {i+1}. {business} ({city}) - {permit_type} [{categories}]")
            
            if len(wine_records) > 5:
                print(f"  ... and {len(wine_records) - 5} more")
    
    def run(self) -> bool:
        """Execute the full workflow: fetch, filter, save, and summarize."""
        print("🍷 Quebec Wine Producers Discovery")
        print("=" * 50)
        
        # Step 1: Fetch raw data
        if not self.fetch_raw_data():
            return False
        
        # Step 2: Load and extract wine data  
        try:
            raw_data = self.load_raw_data()
            total_records = self.count_total_records(raw_data)
            wine_records = self.extract_wine_records(raw_data)
        except Exception as e:
            print(f"Error processing data: {e}")
            return False
        
        # Step 3: Save filtered data
        self.save_wine_data(wine_records, total_records)
        
        # Step 4: Print summary
        self.print_summary(wine_records)
        
        return True


def main():
    """Main entry point."""
    fetcher = QuebecWineProducersFetcher()
    
    if fetcher.run():
        print(f"\n✅ Successfully processed Quebec wine producers data")
        print(f"📁 Raw data: {fetcher.raw_file}")
        print(f"🍷 Wine data: {fetcher.wine_file}")
        return 0
    else:
        print("❌ Failed to process Quebec wine producers data")
        return 1


if __name__ == "__main__":
    exit(main())