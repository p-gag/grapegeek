#!/usr/bin/env python3
"""
Quebec Wine Producers Enrichment Script

Enriches the Quebec wine producers data with:
1. Website URLs that contain information about their wines
2. Wine label names (if different from business name)

Uses OpenAI's fast reasoning model for web research and analysis.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WineProducerEnricher:
    """Enriches Quebec wine producers with website and wine label information."""
    
    def __init__(self, input_file: str = "data/racj/racj-alcool-fabricant_vin.json", 
                 output_file: str = "data/racj/racj-alcool-fabricant_enriched.json"):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.mock_mode = False
        else:
            print("⚠️  No OPENAI_API_KEY found, running in mock mode")
            self.client = None
            self.mock_mode = True
        
        # Use gpt-5-mini model for Responses API 
        self.model = "gpt-5-mini"
        
    def load_wine_producers(self) -> Dict[str, Any]:
        """Load the wine producers data."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
            
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _generate_mock_response(self, business_name: str, city: str) -> Dict[str, Any]:
        """Generate mock enrichment data for testing."""
        name_lower = business_name.lower()
        
        # Mock website generation (70% chance for wine-focused businesses)
        website = None
        if any(word in name_lower for word in ['vignoble', 'domaine', 'château', 'clos', 'ferme']):
            # Generate plausible website based on name
            clean_name = business_name
            for prefix in ['VIGNOBLE ', 'DOMAINE ', 'CHÂTEAU ', 'CLOS ', 'FERME ']:
                clean_name = clean_name.replace(prefix, '')
            
            # Create website-friendly name
            website_name = clean_name.lower()
            website_name = website_name.replace(' ', '').replace("'", '').replace('-', '')
            website_name = website_name.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
            website_name = website_name.replace('à', 'a').replace('ç', 'c').replace('î', 'i')
            website_name = website_name[:20]  # Limit length
            website = f"https://www.{website_name}.com"
        
        # Mock wine label logic - check if business name differs from wine brand
        wine_label = None
        
        # Common patterns where business name differs from wine label
        if business_name.startswith('VIGNOBLE '):
            # Vignoble often uses just the location/family name for wine label
            wine_label = business_name.replace('VIGNOBLE ', '').replace(' INC.', '').replace(' LTÉE', '')
        elif ' INC.' in business_name and not any(word in name_lower for word in ['vignoble', 'domaine', 'château']):
            # Corporate names often have different wine labels
            wine_label = business_name.replace(' INC.', '').replace(' LTÉE', '')
            if len(wine_label.split()) > 2:  # If still long, use first part
                wine_label = ' '.join(wine_label.split()[:2])
        elif any(prefix in business_name for prefix in ['CENTRE DE', 'FERME DE', 'AU ', 'AUX ']):
            # These often use simpler wine labels
            if business_name.startswith('AU '):
                wine_label = business_name[3:]  # Remove "AU "
            elif business_name.startswith('AUX '):
                wine_label = business_name[4:]  # Remove "AUX "
            elif 'FERME DE' in business_name:
                wine_label = business_name.replace('FERME DE ', '').replace('FERME ', '')
        
        # Mock wine data generation
        wines = []
        if any(word in name_lower for word in ['vignoble', 'domaine', 'château']):
            # Generate realistic Quebec wine portfolio
            wine_types = [
                {
                    "name": f"{wine_label or business_name} Blanc",
                    "description": "Vin blanc sec aux arômes fruités et floraux, parfait pour l'apéritif",
                    "cepages": ["Frontenac Blanc", "Chardonnay"],
                    "type": "white",
                    "vintage": "2023"
                },
                {
                    "name": f"{wine_label or business_name} Rouge",
                    "description": "Vin rouge de caractère aux notes de fruits rouges et d'épices",
                    "cepages": ["Frontenac", "Marquette", "Léon Millot"],
                    "type": "red",
                    "vintage": "2022"
                }
            ]
            # Add 1-2 wines randomly
            import random
            wines = random.sample(wine_types, k=random.randint(1, 2))
        
        # Generate realistic search notes
        notes = f"Mock research for {city}, QC wine producer"
        if website:
            notes += " - Generated website based on name pattern"
        if wine_label:
            notes += " - Wine label differs from business name"
        if wines:
            notes += f" - Mock wine portfolio with {len(wines)} wines"
        
        return {
            "website": website,
            "wine_label": wine_label,
            "verified_wine_producer": True,
            "wines": wines,
            "search_notes": notes
        }
    
    def enrich_producer(self, producer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a single wine producer with website and wine label information.
        
        Args:
            producer: Original producer record
            
        Returns:
            Enriched producer record with website and wine_label fields
        """
        business_name = producer.get('RaisonSociale', '')
        city = producer.get('Ville', '')
        
        # Create enrichment prompt
        prompt = f"""
You are researching Quebec wine producers. For the following wine producer, please:

1. Find their official website URL (if they have one)
2. Determine their wine label/brand name if it differs from their business name
3. Verify they actually produce wine (not just other alcoholic beverages)
4. Find detailed information about their wines including:
   - List of wines they produce (names)
   - Description of each wine (style, tasting notes, characteristics)
   - Wine making details, if any.
   - Grape varietals (cépages) used in each wine, just the official name.

Producer Information:
- Business Name: {business_name}
- City: {city}, Quebec
- Permit Type: Production artisanale de vin

Please respond ONLY in this JSON format:
{{
    "website": "https://example.com or null if none found",
    "wine_label": "Wine Label Name or null if same as business name",
    "verified_wine_producer": true/false,
    "wines": [
        {{
            "name": "Wine Name",
            "description": "Style, tasting notes, characteristics",
            "winemaking": "Maceration for ...",
            "cepages": ["Grape Variety 1", "Grape Variety 2"],
            "type": "Red/White/Rosé/Orange/Sparkling/Fortified/Dessert/Fruit Wine/Apéritif/Other",
            "vintage": "2023 or null if not specified"
        }}
    ],
    "search_notes": "Brief notes about what you found and sources"
}}

Focus on finding legitimate, official websites. If no specific wine details are available, return an empty wines array. Use French grape variety names when available (e.g., "Chardonnay", "Cabernet Sauvignon", "Frontenac", "Marquette").

For wine types, use ONLY these exact categories: Red, White, Rosé, Orange, Sparkling, Fortified, Dessert, Fruit Wine, Apéritif, Other. Choose the most appropriate single category for each wine.
"""

        try:
            if self.mock_mode:
                # Mock response for testing
                mock_response = self._generate_mock_response(business_name, city)
                response_text = json.dumps(mock_response)
                print(f"🔍 Mock enriched: {business_name}")
                print(f"  Response: {response_text}")
            else:
                # Call OpenAI Responses API with web search tools
                full_prompt = f"""You are a research assistant specializing in Quebec wine producers. Use web search to find accurate, current information.

{prompt}"""
                
                response = self.client.responses.create(
                    model=self.model,
                    tools=[{"type": "web_search"}],
                    input=full_prompt
                )
                
                response_text = response.output_text
                print(f"✓ Enriched: {business_name}")
                print(f"  Response: {response_text}")
            
            # Try to parse JSON response
            try:
                enrichment_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, extract basic info
                enrichment_data = {
                    "website": None,
                    "wine_label": None,
                    "verified_wine_producer": True,
                    "wines": [],
                    "search_notes": "Response parsing failed"
                }
                print(f"  Warning: Could not parse JSON response")
            
            # Add enrichment data to producer record
            enriched_producer = producer.copy()
            enriched_producer.update({
                'website': enrichment_data.get('website'),
                'wine_label': enrichment_data.get('wine_label'),
                'verified_wine_producer': enrichment_data.get('verified_wine_producer', True),
                'wines': enrichment_data.get('wines', []),
                'enrichment_notes': enrichment_data.get('search_notes', ''),
                'enrichment_date': datetime.now().isoformat()
            })
            
            return enriched_producer
            
        except Exception as e:
            print(f"✗ Error enriching {business_name}: {e}")
            
            # Return original producer with error note
            enriched_producer = producer.copy()
            enriched_producer.update({
                'website': None,
                'wine_label': None,
                'verified_wine_producer': True,
                'wines': [],
                'enrichment_notes': f'Enrichment failed: {str(e)}',
                'enrichment_date': datetime.now().isoformat()
            })
            
            return enriched_producer
    
    def load_existing_enhanced_data(self) -> Dict[str, Any]:
        """Load existing enhanced data if available."""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return None

    def enrich_producers(self, limit: int = 5) -> Dict[str, Any]:
        """
        Enrich wine producers data with website and wine label information.
        
        Args:
            limit: Number of producers to process (for testing)
            
        Returns:
            Enriched data structure
        """
        print(f"🍷 Quebec Wine Producers Enrichment")
        print("=" * 50)
        
        # Load original data
        original_data = self.load_wine_producers()
        wine_producers = original_data['wine_producers']
        
        # Check for existing enhanced data
        existing_data = self.load_existing_enhanced_data()
        if existing_data:
            enriched_producers = existing_data.get('wine_producers', [])
            print(f"📁 Loaded existing enhanced data: {len(enriched_producers)} producers already processed")
        else:
            enriched_producers = []
            print(f"🆕 Starting fresh enrichment")
        
        # Find starting point
        processed_names = {p.get('RaisonSociale') for p in enriched_producers}
        start_index = len(enriched_producers)
        end_index = min(start_index + limit, len(wine_producers))
        
        print(f"📊 Status: {start_index}/{len(wine_producers)} producers processed")
        print(f"🎯 Processing {start_index + 1} to {end_index} (limit: {limit})")
        print("=" * 50)
        
        # Process remaining producers
        for i in range(start_index, end_index):
            producer = wine_producers[i]
            producer_name = producer.get('RaisonSociale', 'Unknown')
            
            print(f"\n[{i+1}/{len(wine_producers)}] Processing: {producer_name}")
            print(f"City: {producer.get('Ville', 'Unknown')}")
            
            enriched_producer = self.enrich_producer(producer)
            enriched_producers.append(enriched_producer)
            
            # Save after each producer
            temp_data = self._create_enhanced_data_structure(enriched_producers, original_data, len(wine_producers))
            self.save_enriched_data(temp_data)
            
            # Print quick summary of what was found
            website = enriched_producer.get('website')
            wines = enriched_producer.get('wines', [])
            print(f"✓ Saved: Website={'Found' if website else 'None'}, Wines={len(wines)}")
        
        # Return final enriched data structure
        return self._create_enhanced_data_structure(enriched_producers, original_data, len(wine_producers))
    
    def _create_enhanced_data_structure(self, enriched_producers, original_data, total_available):
        """Create the enhanced data structure."""
        enriched_data = {
            'metadata': original_data['metadata'].copy(),
            'enrichment_metadata': {
                'enrichment_date': datetime.now().isoformat(),
                'model_used': self.model,
                'enriched_count': len(enriched_producers),
                'total_available': total_available,
                'enrichment_fields': ['website', 'wine_label', 'verified_wine_producer', 'wines', 'enrichment_notes']
            },
            'wine_producers': enriched_producers
        }
        
        # Update metadata
        enriched_data['metadata']['wine_record_count'] = len(enriched_producers)
        
        return enriched_data
    
    def save_enriched_data(self, enriched_data: Dict[str, Any]) -> None:
        """Save enriched data to output file."""
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, indent=2, ensure_ascii=False)
        
        # Only print save message for final saves (not incremental ones)
        enriched_count = enriched_data.get('enrichment_metadata', {}).get('enriched_count', 0)
        if enriched_count % 5 == 0 or enriched_count == 1:  # Print every 5th save or first save
            print(f"💾 Progress saved: {enriched_count} producers enriched")
    
    def print_summary(self, enriched_data: Dict[str, Any]) -> None:
        """Print a summary of the enrichment results."""
        producers = enriched_data['wine_producers']
        
        # Count results
        with_website = len([p for p in producers if p.get('website')])
        with_wine_label = len([p for p in producers if p.get('wine_label')])
        verified_producers = len([p for p in producers if p.get('verified_wine_producer')])
        with_wines = len([p for p in producers if p.get('wines')])
        total_wines = sum(len(p.get('wines', [])) for p in producers)
        
        print(f"\n=== Enrichment Summary ===")
        print(f"Total processed: {len(producers)}")
        print(f"With website: {with_website}")
        print(f"With wine label: {with_wine_label}")
        print(f"Verified wine producers: {verified_producers}")
        print(f"With wine details: {with_wines}")
        print(f"Total wines found: {total_wines}")
        
        print(f"\nSample enriched producers:")
        for i, producer in enumerate(producers[:3]):
            name = producer.get('RaisonSociale', 'Unknown')
            website = producer.get('website', 'None')
            wine_label = producer.get('wine_label', 'Same as business')
            wines = producer.get('wines', [])
            print(f"  {i+1}. {name}")
            print(f"     Website: {website}")
            print(f"     Wine Label: {wine_label}")
            print(f"     Wines: {len(wines)} found")
            for j, wine in enumerate(wines[:2]):  # Show first 2 wines
                wine_name = wine.get('name', 'Unknown')
                cepages = ', '.join(wine.get('cepages', []))
                print(f"       - {wine_name} ({wine.get('type', 'unknown')})")
                if cepages:
                    print(f"         Cépages: {cepages}")
            if len(wines) > 2:
                print(f"       ... and {len(wines) - 2} more wines")
    
    def run(self, limit: int = 5) -> bool:
        """Execute the enrichment workflow."""
        try:
            # Enrich producers
            enriched_data = self.enrich_producers(limit=limit) 
            
            # Save results
            self.save_enriched_data(enriched_data)
            
            # Print summary
            self.print_summary(enriched_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Enrichment failed: {e}")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enrich Quebec wine producers with website and label information')
    parser.add_argument('--limit', type=int, default=5, help='Number of producers to process (default: 5)')
    parser.add_argument('--input', type=str, default='data/racj/racj-alcool-fabricant_vin.json', help='Input file path')
    parser.add_argument('--output', type=str, default='data/racj/racj-alcool-fabricant_enriched.json', help='Output file path')
    
    args = parser.parse_args()
    
    enricher = WineProducerEnricher(input_file=args.input, output_file=args.output)
    
    if enricher.run(limit=args.limit):
        print(f"\n✅ Successfully enriched {args.limit} wine producers")
        return 0
    else:
        print("❌ Enrichment failed")
        return 1


if __name__ == "__main__":
    exit(main())