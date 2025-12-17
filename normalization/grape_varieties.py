#!/usr/bin/env python3
"""
Grape Variety Normalization Script

Analyzes grape varieties from enhanced wine producer data to:
1. Extract all unique grape variety names (case insensitive)
2. Calculate frequency of each variety
3. Use GPT-5 to create official name mapping with aliases
4. Save the mapping as YAML for use in data processing
"""

import json
import yaml
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class GrapeVarietyNormalizer:
    """Normalizes grape variety names using frequency analysis and AI mapping."""
    
    def __init__(self, 
                 input_file: str = "data/racj/racj-alcool-fabricant_enhanced.json",
                 output_file: str = "data/grape_variety_mapping.yaml"):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def extract_grape_varieties(self) -> Counter:
        """Extract all grape varieties from enhanced producer data."""
        print("🍇 Extracting grape varieties from enhanced data...")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            producers = data.get('wine_producers', [])
        
        all_varieties = []
        
        for producer in producers:
            wines = producer.get('wines', [])
            for wine in wines:
                cepages = wine.get('cepages', [])
                if isinstance(cepages, list):
                    all_varieties.extend(cepages)
                elif isinstance(cepages, str):
                    # Handle comma-separated strings
                    varieties = [v.strip() for v in cepages.split(',') if v.strip()]
                    all_varieties.extend(varieties)
        
        # Count frequencies (case insensitive)
        variety_counter = Counter()
        for variety in all_varieties:
            if variety and variety.strip():
                # Normalize for counting (lowercase, strip)
                normalized = variety.strip().lower()
                variety_counter[normalized] += 1
        
        print(f"📊 Found {len(variety_counter)} unique grape varieties")
        print(f"🔢 Total occurrences: {sum(variety_counter.values())}")
        
        return variety_counter
    
    def create_variety_list_for_ai(self, variety_counter: Counter) -> str:
        """Create a formatted list of varieties with frequencies for AI processing."""
        varieties_with_freq = []
        
        for variety, count in variety_counter.most_common():
            varieties_with_freq.append(f"{variety} (appears {count} times)")
        
        return "\\n".join(varieties_with_freq)
    
    def load_existing_mapping(self) -> Dict[str, Any]:
        """Load existing grape variety mapping if it exists."""
        if not self.output_file.exists():
            return {}
        
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('grape_variety_mapping', {})
        except Exception as e:
            print(f"⚠️  Error loading existing mapping: {str(e)}")
            return {}
    
    def find_unmapped_varieties(self, variety_counter: Counter, existing_mapping: Dict[str, Any]) -> Counter:
        """Find varieties that don't have mappings yet."""
        # Create set of all existing aliases (lowercase)
        existing_aliases = set()
        for official_name, info in existing_mapping.items():
            aliases = info.get('aliases', [])
            existing_aliases.update(alias.lower() for alias in aliases)
        
        # Find varieties not in existing mapping
        unmapped = Counter()
        for variety, count in variety_counter.items():
            if variety.lower() not in existing_aliases:
                unmapped[variety] = count
        
        print(f"📊 Found {len(unmapped)} new varieties to map (out of {len(variety_counter)} total)")
        return unmapped
    
    def generate_official_mapping(self, variety_counter: Counter) -> Dict[str, Any]:
        """Use GPT-5 to create/update official name mapping iteratively."""
        print("🤖 Generating official grape variety mapping with GPT-5...")
        
        # Load existing mapping
        existing_mapping = self.load_existing_mapping()
        print(f"📋 Loaded {len(existing_mapping)} existing varieties from mapping")
        
        # Find unmapped varieties
        unmapped_varieties = self.find_unmapped_varieties(variety_counter, existing_mapping)
        
        if not unmapped_varieties:
            print("✅ All varieties already mapped!")
            return {"grape_variety_mapping": existing_mapping}
        
        # Create variety list for AI (only unmapped ones)
        unmapped_list = self.create_variety_list_for_ai(unmapped_varieties)
        
        # Create existing mapping summary for context
        existing_summary = ""
        if existing_mapping:
            existing_names = list(existing_mapping.keys())[:10]  # Show first 10 for context
            existing_summary = f"\nExisting official varieties (for reference): {', '.join(existing_names)}"
            if len(existing_mapping) > 10:
                existing_summary += f" ... and {len(existing_mapping) - 10} more"
        
        prompt = f"""
You are a viticulture expert specializing in cold-climate grape varieties, particularly hybrid varieties grown in Quebec and northeastern North America.

I have an existing grape variety mapping and need to add NEW varieties that aren't mapped yet.
{existing_summary}

Here are the NEW grape varieties that need mapping:
{unmapped_list}

Please EXTEND my existing mapping by adding these new varieties or alias. Return the COMPLETE mapping including both existing and new varieties.

Mapping rules:
- Use the most common/official spelling as the "official_name"
- Use proper capitalization for official names (e.g., "Frontenac Noir", "Marquette")
- IMPORTANT: All aliases should be lowercase for consistency
- Try to add variant to an existing mapping but in case of doubt, create a new entry.

ex: "belchas", "Bel-Chas", "Bel Chas" should lead: 

```yaml
grape_variety_mapping:
  Bel-Chas:
    aliases:
    - belchas
    - bel chas
    - bel-chas
```

So that any of these name in lower case lead to a unique name.

Current mapping to extend:
{yaml.dump({"grape_variety_mapping": existing_mapping}, default_flow_style=False)}

Return ONLY the complete YAML structure including both existing and new mappings.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}]
            )
            
            mapping_text = response.choices[0].message.content
            
            # Extract YAML from response (remove markdown code blocks)
            if "```yaml" in mapping_text:
                start = mapping_text.find("```yaml") + 7
                end = mapping_text.find("```", start)
                mapping_text = mapping_text[start:end].strip()
            elif "```" in mapping_text:
                start = mapping_text.find("```") + 3
                end = mapping_text.rfind("```")
                mapping_text = mapping_text[start:end].strip()
            
            return yaml.safe_load(mapping_text)
            
        except Exception as e:
            print(f"❌ Error generating mapping: {str(e)}")
            return None
    
    def save_mapping(self, mapping: Dict[str, Any]) -> None:
        """Save the grape variety mapping to YAML file."""
        print(f"💾 Saving grape variety mapping to {self.output_file}")
        
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            yaml.dump(mapping, f, default_flow_style=False, allow_unicode=True, sort_keys=True)
    
    def run(self) -> None:
        """Execute the complete grape variety normalization process."""
        print("🍇 Starting Grape Variety Normalization")
        print("=" * 50)
        
        # Step 1: Extract and count varieties
        variety_counter = self.extract_grape_varieties()
        
        # Display top varieties
        print("\\n🔝 Top 10 most common varieties:")
        for variety, count in variety_counter.most_common(10):
            print(f"  {variety}: {count} occurrences")
        
        # Step 2: Generate official mapping
        mapping = self.generate_official_mapping(variety_counter)
        
        if mapping:
            # Step 3: Save mapping
            self.save_mapping(mapping)
            
            print(f"\\n✅ Grape variety normalization complete!")
            print(f"📁 Mapping saved to: {self.output_file}")
            print(f"🎯 {len(mapping.get('grape_variety_mapping', {}))} official varieties mapped")
        else:
            print("❌ Failed to generate mapping")

if __name__ == "__main__":
    normalizer = GrapeVarietyNormalizer()
    normalizer.run()