#!/usr/bin/env python3

import os
import argparse
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def translate_to_french(english_content: str, content_type: str = "article") -> str:
    """Translate English content to French using OpenAI."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""
Translate the following English grape variety {content_type} to French. 

Important guidelines:
- Maintain all technical terms accuracy (grape variety names, disease names, climate zones)
- Keep citations and references exactly as they are
- Preserve the casual, approachable tone
- Use Quebec French where appropriate (this is for Quebec wine growers)
- Keep the markdown formatting intact
- Don't translate proper names of people, places, wineries, or publications

English content:
---
{english_content}
---

Provide the French translation:
"""
    
    try:
        response = client.responses.create(
            model="gpt-5",
            tools=[{"type": "web_search"}],
            input=prompt
        )
        return response.output_text
    except Exception as e:
        return f"Error translating content: {str(e)}"

def generate_french_from_english_file(english_file_path: str, output_dir: str = "output/fr") -> str:
    """Generate French version of an existing English article."""
    english_path = Path(english_file_path)
    
    if not english_path.exists():
        raise FileNotFoundError(f"English file not found: {english_file_path}")
    
    # Read English content
    english_content = english_path.read_text()
    
    # Determine content type from filename
    content_type = "winemaking story" if "winemaking" in english_path.name else "technical article"
    
    # Translate to French
    print(f"Translating {content_type} to French...")
    french_content = translate_to_french(english_content, content_type)
    
    # Create output path
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate French filename
    french_filename = english_path.name
    if "winemaking_stories" in french_filename:
        french_filename = french_filename.replace("winemaking_stories", "histoires_vinification")
    
    french_file_path = output_path / french_filename
    
    # Save French content
    french_file_path.write_text(french_content)
    
    print(f"French translation saved to: {french_file_path}")
    return str(french_file_path)

def main():
    parser = argparse.ArgumentParser(description="Generate French translations of grape variety articles")
    parser.add_argument("english_file", help="Path to the English article file")
    parser.add_argument("--output-dir", default="output/fr", help="Output directory for French files")
    
    args = parser.parse_args()
    
    try:
        french_file = generate_french_from_english_file(args.english_file, args.output_dir)
        print(f"✅ Successfully generated French translation: {french_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()