#!/usr/bin/env python3
"""
Producer Enrichment Module

Extracted from 06_producer_enrich.py for use in unified research pipeline.
Performs deep research on wine producers for detailed wine information.
"""

import json
import threading
import time
from typing import Dict, Tuple
import openai


def create_enrichment_prompt(producer: Dict) -> str:
    """Create enrichment prompt for a wine producer."""
    name = producer.get('business_name', producer.get('name', 'Unknown'))
    city = producer.get('city', 'Unknown')
    state_province = producer.get('state_province', 'Unknown')
    country = producer.get('country', 'Unknown')
    address = producer.get('address', '')
    
    # Determine source and country context
    if country == 'CA':
        country_name = 'Canada'
    else:
        country_name = 'United States'
    
    prompt = f"""
You are researching wine producers and you have to produce the following online research for a given producer below.

1. Find their official website URL and social media presence
2. Determine their wine label/brand name if it differs from their business name
3. Check if they are open for visit and if so, list the activities if any (or null if not open for visit).
   Ex: "wine_tasting", "guided_tours", "vineyard_tours", "wine_sales", "restaurant", "events", "wedding_venue", "picnic_area", "gift_shop", "harvest_participation", "food_pairing", ...
4. Find detailed information about their wines including:
   - List of wines they produce (names)
   - Description of each wine (style, tasting notes, characteristics)  
   - Wine making details, if any.
   - Grape varietals (cépages) used in each wine, just the official name.
5. At the end, set verified_wine_producer to true if we found wine bottle products with actual grape cepages.

Please respond ONLY in this JSON format:

{{
    "website": "https://example.com or null if none found",
    "social_media": ["array", "of", "social", "media", "URLs"] or null,
    "location": "{city}, {state_province}, {country_name}",
    "activities": ["wine_tasting", "vineyard_tours", "restaurant", ...] or null,
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
    ]
}}


FOCUS ON: Wine production details, grape varieties (cépages), wine styles, and winemaking information.
- Be precise with grape variety names (Frontenac, Vidal, Seyval Blanc, Marquette, etc.)
- Include wine types (Red, White, Rosé, Ice Wine, Sparkling)
- Look for wine specialties and signature products
- Note organic/biodynamic certifications and wine awards
- Include visiting info as secondary information

PRODUCER: "{name}" located at {address} in {city}, {state_province}, {country_name}, please:

Return only valid JSON with no additional text or formatting.
"""
    
    return prompt


def enrich_producer(producer: Dict, api_key: str, request_delay: float = 1.0, 
                   print_lock: threading.Lock = None) -> Tuple[Dict, Dict]:
    """Enrich a single producer with detailed research.
    
    Args:
        producer: Producer data dict
        api_key: OpenAI API key
        request_delay: Delay between requests
        print_lock: Thread lock for printing
        
    Returns:
        Tuple of (producer_data, enrichment_data)
    """
    permit_id = producer.get('permit_id', 'unknown')
    name = producer.get('business_name', producer.get('name', 'Unknown'))
    
    try:
        # Thread-safe printing
        if print_lock:
            with print_lock:
                print(f"  🔍 Researching {name} ({permit_id})", flush=True)
        else:
            print(f"  🔍 Researching {name} ({permit_id})", flush=True)
        
        prompt = create_enrichment_prompt(producer)
        
        # Rate limiting
        if request_delay > 0:
            time.sleep(request_delay)
        
        # Create OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        response = client.responses.create(
            model="gpt-5-mini",
            tools=[{"type": "web_search"}],
            input=prompt
        )
        
        # Parse JSON response
        try:
            enrichment_data = json.loads(response.output_text)
            
            # Ensure required fields exist
            required_fields = ['website', 'social_media', 'location', 'activities', 
                             'wine_label', 'verified_wine_producer', 'wines']
            for field in required_fields:
                if field not in enrichment_data:
                    enrichment_data[field] = None
                    
            # Add metadata
            enrichment_data['permit_id'] = permit_id
            enrichment_data['enriched_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            if print_lock:
                with print_lock:
                    verified = enrichment_data.get('verified_wine_producer', False)
                    wine_count = len(enrichment_data.get('wines', []))
                    print(f"    ✅ {name} - Verified: {verified}, Wines: {wine_count}", flush=True)
            
            return producer, enrichment_data
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing failed: {str(e)}"
            if print_lock:
                with print_lock:
                    print(f"    ❌ {name} - {error_msg}", flush=True)
            
            return producer, {
                'permit_id': permit_id,
                'error': error_msg,
                'verified_wine_producer': False,
                'enriched_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
    except Exception as e:
        error_msg = f"Enrichment failed: {str(e)}"
        if print_lock:
            with print_lock:
                print(f"    ❌ {name} - {error_msg}", flush=True)
        
        return producer, {
            'permit_id': permit_id,
            'error': error_msg,
            'verified_wine_producer': False,
            'enriched_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }


def calculate_enrichment_cost(total_producers: int, cost_per_producer: float = 0.075) -> Dict[str, float]:
    """Calculate estimated enrichment costs.
    
    Args:
        total_producers: Number of producers to enrich
        cost_per_producer: Average cost per producer (default from historical data)
        
    Returns:
        Dict with cost estimates
    """
    total_cost = total_producers * cost_per_producer
    
    return {
        'total_producers': total_producers,
        'cost_per_producer': cost_per_producer,
        'estimated_total_cost': total_cost,
        'estimated_cost_range': {
            'low': total_cost * 0.7,  # 30% variance
            'high': total_cost * 1.3
        }
    }