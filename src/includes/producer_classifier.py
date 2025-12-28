#!/usr/bin/env python3
"""
Producer Classification Module

Extracted from 04_producer_search.py for use in unified research pipeline.
Classifies wine producers and searches for their web presence.
Uses structured output with Pydantic models for reliable parsing.
"""

from typing import Dict, Optional, Literal
from openai import OpenAI
from pydantic import BaseModel


class SocialMedia(BaseModel):
    Facebook: Optional[str] = None
    Instagram: Optional[str] = None


class ProducerClassification(BaseModel):
    classification: Literal[
        "wine_grower", 
        "winemaker", 
        "grape_grower", 
        "meadery", 
        "cidery", 
        "brewery", 
        "distillery", 
        "fruit_winery", 
        "unknown"
    ]
    website: Optional[str] = None
    social_media: Optional[SocialMedia] = None


def infer_from_name(producer: Dict) -> str:
    """Infer classification from business name as fallback."""
    business_name = producer.get('business_name', '').upper()
    
    # Wine-related keywords (most common)
    if any(word in business_name for word in ['WINERY', 'VINEYARD', 'WINE', 'VINERY']):
        return "wine_grower"
    
    # Farm/orchard with wine permit = likely wine grower
    if any(word in business_name for word in ['FARM', 'ORCHARD', 'ESTATE', 'ACRES']):
        return "wine_grower"
    
    # Mead producers
    if any(word in business_name for word in ['MEAD', 'MEADERY']):
        return "meadery"
    
    # Cider producers  
    if any(word in business_name for word in ['CIDER', 'CIDERY']):
        return "cidery"
    
    # Beer producers
    if any(word in business_name for word in ['BREW', 'BEER', 'ALE', 'LAGER']):
        return "brewery"
    
    # Distilleries
    if any(word in business_name for word in ['DISTILL', 'SPIRITS', 'WHISKEY', 'VODKA']):
        return "distillery"
    
    # Default for wine permit holders
    return "winemaker"


def create_system_prompt() -> str:
    """Create system prompt for producer classification."""
    return """You are classifying wine industry businesses. Your task is to:
1. Determine their PRIMARY business category based on products advertised
2. Find their main website and social media presence

Categories (choose ONE):
- wine_grower: Grows grapes AND makes wine (vineyards, wine farms)
- winemaker: Makes wine FROM GRAPES but doesn't grow grapes. You should see grape cepage/variety on the site.
- grape_grower: Only grows grapes, sells to others
- meadery: Makes mead (honey wine)
- cidery: Makes hard cider
- brewery: Makes beer
- distillery: Makes spirits, can be from fruits
- fruit_winery: Makes wine from fruits other than grapes
- unknown: Cannot determine despite having wine permit

Be decisive - avoid "unknown" unless you're certain they don't make wine despite having a permit.
Find their official website and main social media presence (Facebook, Instagram are most common)."""


def create_user_prompt(producer: Dict) -> str:
    """Create user prompt for a producer."""
    business_name = producer.get('business_name', '')
    city = producer.get('city', '')
    state = producer.get('state_province', '')
    country = producer.get('country', '')
    
    return f"""Search for "{business_name}" in {city}, {state} - {country}.

Classify this business and find their web presence."""


def classify_producer(producer: Dict, client: OpenAI) -> Dict:
    """Classify a single producer and search for web presence.
    
    Args:
        producer: Producer data dict
        client: OpenAI client instance
        
    Returns:
        Dict with classification, website, social_media fields
    """
    try:
        response = client.responses.parse(
            model="gpt-4o-2024-08-06",
            tools=[{"type": "web_search"}],
            input=[
                {"role": "system", "content": create_system_prompt()},
                {"role": "user", "content": create_user_prompt(producer)}
            ],
            text_format=ProducerClassification,
            temperature=0  # Keep deterministic
        )
        
        result = response.output_parsed
        
        # Convert to dict format for compatibility
        return {
            "classification": result.classification,
            "website": result.website,
            "social_media": result.social_media.model_dump() if result.social_media else None
        }
            
    except Exception as e:
        print(f"⚠️  Classification error for {producer.get('business_name')}: {e}")
        # Fallback to name-based classification
        return {
            "classification": infer_from_name(producer),
            "website": None,
            "social_media": None
        }