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
                 input_file: str = "data/unified_wine_producers_final2.jsonl",
                 output_file: str = "data/grape_variety_mapping.yaml"):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def extract_grape_varieties(self) -> Counter:
        """Extract all grape varieties from final2 producer data."""
        print("🍇 Extracting grape varieties from final2 dataset...")
        
        if not self.input_file.exists():
            print(f"❌ Input file not found: {self.input_file}")
            return Counter()
        
        all_varieties = []
        producer_count = 0
        wine_count = 0
        
        # Read JSONL file line by line
        with open(self.input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                    
                try:
                    producer = json.loads(line.strip())
                    producer_count += 1
                    
                    # Get wines from enriched data
                    wines = producer.get('wines', [])
                    
                    for wine in wines:
                        wine_count += 1
                        cepages = wine.get('cepages', [])
                        
                        if isinstance(cepages, list):
                            all_varieties.extend(cepages)
                        elif isinstance(cepages, str):
                            # Handle comma-separated strings
                            varieties = [v.strip() for v in cepages.split(',') if v.strip()]
                            all_varieties.extend(varieties)
                            
                except json.JSONDecodeError as e:
                    print(f"⚠️  Error parsing line: {e}")
                    continue
        
        # Count frequencies (case insensitive)
        variety_counter = Counter()
        for variety in all_varieties:
            if variety and variety.strip():
                # Normalize for counting (lowercase, strip)
                normalized = variety.strip().lower()
                variety_counter[normalized] += 1
        
        print(f"📊 Processed {producer_count} producers, {wine_count} wines")
        print(f"🍇 Found {len(variety_counter)} unique grape varieties")
        print(f"🔢 Total occurrences: {sum(variety_counter.values())}")
        
        return variety_counter
    
    def create_variety_list_for_ai(self, variety_counter: Counter) -> str:
        """Create a formatted list of varieties with frequencies for AI processing."""
        varieties_with_freq = []
        
        for variety, count in variety_counter.most_common():
            varieties_with_freq.append(f"{variety} (appears {count} times)")
        
        return "\\n".join(varieties_with_freq)
    
    def load_existing_mapping(self) -> Dict[str, Any]:
        """Load existing grape variety mapping if it exists, merging duplicates."""
        if not self.output_file.exists():
            return {}
        
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                raw_mapping = data.get('grape_variety_mapping', {})
                
            # Merge duplicates and normalize structure
            return self.merge_duplicates(raw_mapping)
        except Exception as e:
            print(f"⚠️  Error loading existing mapping: {str(e)}")
            return {}
    
    def merge_duplicates(self, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Merge duplicate entries based on normalized keys."""
        merged = {}
        key_to_official = {}  # Maps normalized key to official name
        
        # First pass: identify official names and their normalized keys
        for official_name, info in mapping.items():
            if not isinstance(info, dict):
                continue
                
            normalized_key = official_name.lower().strip()
            
            if normalized_key in key_to_official:
                print(f"🔄 Merging duplicate: {official_name} -> {key_to_official[normalized_key]}")
                # Merge aliases
                existing_info = merged[key_to_official[normalized_key]]
                existing_aliases = set(existing_info.get('aliases', []))
                
                new_aliases = info.get('aliases', [])
                for alias in new_aliases:
                    if isinstance(alias, str):
                        existing_aliases.add(alias.lower())
                
                existing_info['aliases'] = sorted(list(existing_aliases))
            else:
                key_to_official[normalized_key] = official_name
                # Clean aliases to ensure they're strings and lowercase
                aliases = info.get('aliases', [])
                clean_aliases = []
                for alias in aliases:
                    if isinstance(alias, str):
                        clean_aliases.append(alias.lower())
                
                merged[official_name] = {
                    'aliases': sorted(clean_aliases)
                }
        
        return merged
    
    def find_unmapped_varieties(self, variety_counter: Counter, existing_mapping: Dict[str, Any], limit: int = 20) -> Counter:
        """Find varieties that don't have mappings yet, limited to specified number."""
        # Create set of all existing aliases (lowercase)
        existing_aliases = set()
        for official_name, info in existing_mapping.items():
            aliases = info.get('aliases', [])
            
            # Safe processing with type checking for robustness
            for alias in aliases:
                if isinstance(alias, str):
                    existing_aliases.add(alias.lower())
                else:
                    print(f"⚠️  Non-string alias found in {official_name}: {alias} (skipping)")
        
        # Find varieties not in existing mapping
        unmapped = Counter()
        for variety, count in variety_counter.items():
            if variety.lower() not in existing_aliases:
                unmapped[variety] = count
        
        # Limit to specified number, ordered by frequency
        if limit and len(unmapped) > limit:
            limited_unmapped = Counter()
            for variety, count in unmapped.most_common(limit):
                limited_unmapped[variety] = count
            print(f"📊 Found {len(unmapped)} new varieties, processing top {limit} by frequency")
            return limited_unmapped
        
        print(f"📊 Found {len(unmapped)} new varieties to map (out of {len(variety_counter)} total)")
        return unmapped
    
    def generate_official_mapping(self, variety_counter: Counter) -> Dict[str, Any]:
        """Use GPT-4o to create/update official name mapping iteratively."""
        print("🤖 Generating official grape variety mapping with GPT-4o...")
        
        # Load existing mapping
        existing_mapping = self.load_existing_mapping()
        print(f"📋 Loaded {len(existing_mapping)} existing varieties from mapping")
        
        # Find unmapped varieties (limit to 20 at a time)
        unmapped_varieties = self.find_unmapped_varieties(variety_counter, existing_mapping, limit=20)
        
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
        """Save the grape variety mapping to YAML file in alphabetical order."""
        print(f"💾 Saving grape variety mapping to {self.output_file}")
        
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Sort the mapping alphabetically
        grape_mapping = mapping.get('grape_variety_mapping', {})
        sorted_mapping = {
            'grape_variety_mapping': dict(sorted(grape_mapping.items()))
        }
        
        # Also sort aliases within each variety
        for variety_info in sorted_mapping['grape_variety_mapping'].values():
            if 'aliases' in variety_info and isinstance(variety_info['aliases'], list):
                variety_info['aliases'] = sorted(variety_info['aliases'])
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            yaml.dump(sorted_mapping, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
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