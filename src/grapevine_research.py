#!/usr/bin/env python3
"""
Grapevine Research Script

Searches VIVC (Vitis International Variety Catalogue) for grape variety information
using structured output for reliable data extraction.
"""

import argparse
import sys
from typing import Optional, List
from openai import OpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class VIVCData(BaseModel):
    prime_name: Optional[str] = None
    berry_skin_color: Optional[str] = None
    vivc_number: Optional[str] = None
    parent1: Optional[str] = None
    parent2: Optional[str] = None
    species: Optional[str] = None
    grape_photo_url: Optional[str] = None
    sources_of_info: Optional[List[str]] = None


def create_system_prompt() -> str:
    """Create system prompt for VIVC data extraction."""
    return """You are extracting grape variety information from the VIVC (Vitis International Variety Catalogue) website at vivc.de.

Your task is to search for grape variety information and extract the following data:
- prime_name: The official/primary name of the variety
- berry_skin_color: Color of the grape berries (e.g., "white", "red", "black", "rose")
- vivc_number: The VIVC catalog number
- parent1: First parent variety name (if known)
- parent2: Second parent variety name (if known) 
- species: The grape species (e.g., "Vitis vinifera", "Vitis labrusca", etc.)
- grape_photo_url: URL to any grape photo if found on the page

If any information is not found or not available, return null for that field.
Focus on finding the exact variety requested and extract data from the official VIVC entry."""


def create_user_prompt(variety_name: str) -> str:
    """Create user prompt for variety search."""
    return f"""Search for the grape variety "{variety_name}" on https://www.vivc.de/ and extract all available information about this variety.

Look for the variety's official VIVC entry and extract the requested data fields."""


def research_grape_variety(variety_name: str) -> VIVCData:
    """Research a grape variety on VIVC using structured output.
    
    Args:
        variety_name: Name of the grape variety to research
        
    Returns:
        VIVCData object with extracted information
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    try:
        response = client.responses.parse(
            model="gpt-4o",
            tools=[
                {
                    "type": "web_search",
                }
            ],
            input=[
                {"role": "system", "content": create_system_prompt()},
                {"role": "user", "content": create_user_prompt(variety_name)}
            ],
            text_format=VIVCData,
            #temperature=0  # Keep deterministic
        )
        
        return response.output_parsed
        
    except Exception as e:
        print(f"⚠️  Error researching variety '{variety_name}': {e}")
        # Return empty data object on error
        return VIVCData()


def format_output(data: VIVCData, variety_name: str) -> str:
    """Format the extracted data for display."""
    output = [f"VIVC Research Results for: {variety_name}"]
    output.append("=" * 50)
    
    fields = [
        ("Prime Name", data.prime_name),
        ("VIVC Number", data.vivc_number),
        ("Berry Skin Color", data.berry_skin_color),
        ("Species", data.species),
        ("Parent 1", data.parent1),
        ("Parent 2", data.parent2),
        ("Grape Photo URL", data.grape_photo_url),
        ("sources_of_info", data.sources_of_info)

    ]
    
    for label, value in fields:
        output.append(f"{label:17}: {value or 'Not found'}")
    
    return "\n".join(output)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Research grape varieties on VIVC (vivc.de)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/grapevine_research.py "Frontenac"
  python src/grapevine_research.py "Chardonnay"
  python src/grapevine_research.py "Marquette"
        """
    )
    
    parser.add_argument(
        "variety_name",
        help="Name of the grape variety to research"
    )
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    print(f"🔍 Researching '{args.variety_name}' on VIVC...")
    
    # Research the variety
    data = research_grape_variety(args.variety_name)
    
    # Display results
    print("\n" + format_output(data, args.variety_name))


if __name__ == "__main__":
    main()