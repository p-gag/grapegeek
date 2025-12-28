#!/usr/bin/env python3
"""
Grape Variety Normalization Script

This script processes wine producer data to normalize and classify grape varieties.
It reads from enriched producer data, identifies unknown varieties, and uses GPT-5
to classify them with a northeast grape variety expert specializing in hybrid grapes.

Usage:
    python normalize_varieties.py [--limit N] [--dry-run]
"""

import json
import yaml
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from openai import OpenAI
import os
from typing import Dict, List, Set, Tuple
import sys
from dotenv import load_dotenv

load_dotenv()

class VarietyNormalizer:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.mapping_file = Path("data/grape_variety_mapping.yaml")
        self.input_file = Path("data/enriched_producers_cache.jsonl")
        
        # Load existing mapping
        self.existing_mapping = self._load_existing_mapping()
        self.existing_aliases = self._build_alias_set()
        
    def _load_existing_mapping(self) -> Dict:
        """Load the existing grape variety mapping."""
        if not self.mapping_file.exists():
            return {"grape_variety_mapping": {}}
        
        with open(self.mapping_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _build_alias_set(self) -> Set[str]:
        """Build a set of all existing aliases for quick lookup."""
        aliases = set()
        mapping = self.existing_mapping.get("grape_variety_mapping", {})
        
        for variety_data in mapping.values():
            if isinstance(variety_data, dict) and "aliases" in variety_data:
                aliases_list = variety_data["aliases"]
                if isinstance(aliases_list, list):
                    for alias in aliases_list:
                        if isinstance(alias, str) and alias.strip():
                            aliases.add(alias.lower().strip())
        
        return aliases
    
    def _extract_varieties_from_jsonl(self) -> List[str]:
        """Extract all unique cepage varieties from the JSONL file."""
        varieties = set()
        
        if not self.input_file.exists():
            print(f"Error: Input file {self.input_file} not found")
            return []
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    
                    # Look for cepages in the wines array (correct structure)
                    if "wines" in data and data["wines"]:
                        for wine in data["wines"]:
                            if "cepages" in wine and wine["cepages"]:
                                for cepage in wine["cepages"]:
                                    if cepage and isinstance(cepage, str):
                                        varieties.add(cepage.strip())
                    
                    # Also check top-level cepages (fallback)
                    if "cepages" in data and data["cepages"]:
                        for cepage in data["cepages"]:
                            if cepage and isinstance(cepage, str):
                                varieties.add(cepage.strip())
                                
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                except Exception as e:
                    print(f"Warning: Error processing line {line_num}: {e}")
        
        return list(varieties)
    
    def _find_unknown_varieties(self, all_varieties: List[str]) -> List[str]:
        """Find varieties that are not in the existing mapping."""
        unknown = []
        
        for variety in all_varieties:
            if variety.lower().strip() not in self.existing_aliases:
                unknown.append(variety)
        
        return unknown
    
    def _build_classification_prompt(self, unknown_varieties: List[str]) -> str:
        """Build the GPT prompt for variety classification."""
        
        # Get the full mapping but strip down Fruit/Unknown to save tokens
        mapping = self.existing_mapping.get("grape_variety_mapping", {}).copy()
        
        # Replace massive Fruit/Unknown lists with just a few examples to save tokens
        fruit_examples = ["apple", "apple (fruit wine)", "blueberry", "cherry", "peach", "strawberry"]
        unknown_examples = ["blend", "red blend", "cold-hardy hybrid (unspecified)", "unknown", "proprietary blend"]
        
        # Build the mapping to send (with reduced Fruit/Unknown but full grape varieties)
        simplified_mapping = {}
        for variety_name, variety_data in mapping.items():
            if variety_name == "Fruit":
                simplified_mapping[variety_name] = {"aliases": fruit_examples}
            elif variety_name == "Unknown": 
                simplified_mapping[variety_name] = {"aliases": unknown_examples}
            else:
                # Keep all actual grape varieties intact
                simplified_mapping[variety_name] = variety_data
        
        # Convert mapping to YAML format for the prompt
        import yaml
        mapping_yaml = yaml.dump({"grape_variety_mapping": simplified_mapping}, 
                                default_flow_style=False, allow_unicode=True)
        
        prompt = f"""You are a northeast North American grape variety expert with special expertise in cold-climate hybrid grapes.

Here is the current grape variety mapping:

```yaml
{mapping_yaml}
```

For each unknown variety below, classify it by either:
1. **Adding alias to existing variety** - if it matches a known grape variety
2. **Creating new grape variety** - if it's a new specific grape variety
3. **Adding to Fruit** - if it's a non-grape fruit  
4. **Adding to Unknown** - if it's vague/unspecified (blends, "estate varieties", etc.)

Return ONLY the additions in the exact same YAML format. For example:

```yaml
Chambourcin:
  aliases:
  - chambourcin

Fruit:
  aliases:
  - new_fruit_name

Unknown:
  aliases:
  - some_vague_blend
```

**Unknown varieties to classify:**
{chr(10).join(f"- {variety}" for variety in unknown_varieties)}"""

        return prompt
    
    def _call_gpt5(self, prompt: str) -> Dict:
        """Call GPT-5 API to get variety classifications in YAML format."""
        if self.dry_run:
            print("DRY RUN - Would call GPT-5 with prompt:")
            print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
            return {}
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse YAML response
            try:
                # Try to extract YAML from response if wrapped in markdown
                if "```yaml" in content:
                    start = content.find("```yaml") + 7
                    end = content.find("```", start)
                    yaml_str = content[start:end].strip()
                    return yaml.safe_load(yaml_str) or {}
                elif "```" in content:
                    # Try generic code block
                    start = content.find("```") + 3
                    end = content.rfind("```")
                    if end > start:
                        yaml_str = content[start:end].strip()
                        return yaml.safe_load(yaml_str) or {}
                else:
                    # Try to parse the whole content as YAML
                    return yaml.safe_load(content) or {}
                    
            except yaml.YAMLError as e:
                print(f"Error parsing YAML response: {e}")
                print(f"Content: {content}")
                return {}
                    
        except Exception as e:
            print(f"Error calling GPT-5: {e}")
            return {}
    
    def _merge_classifications(self, additions: Dict) -> Dict:
        """Merge new variety additions into existing mapping."""
        updated_mapping = self.existing_mapping.copy()
        
        if "grape_variety_mapping" not in updated_mapping:
            updated_mapping["grape_variety_mapping"] = {}
        
        mapping = updated_mapping["grape_variety_mapping"]
        
        # Process each addition from the AI response
        for variety_name, variety_data in additions.items():
            if not isinstance(variety_data, dict) or "aliases" not in variety_data:
                continue
                
            aliases = variety_data["aliases"]
            if not isinstance(aliases, list):
                continue
            
            # If the variety already exists, merge the aliases
            if variety_name in mapping:
                existing_aliases = mapping[variety_name].get("aliases", [])
                for alias in aliases:
                    if alias and alias not in existing_aliases:
                        existing_aliases.append(alias)
            else:
                # Create new variety entry
                mapping[variety_name] = {
                    "aliases": [alias for alias in aliases if alias]
                }
        
        return updated_mapping
    
    def _save_mapping(self, mapping: Dict) -> None:
        """Save the updated mapping to file."""
        if self.dry_run:
            print("DRY RUN - Would save updated mapping")
            return
        
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            yaml.dump(mapping, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"Saved updated mapping to {self.mapping_file}")
    
    def process_varieties(self, limit: int = 50) -> Dict:
        """Process unknown varieties and classify them."""
        print("Loading varieties from enriched producer data...")
        all_varieties = self._extract_varieties_from_jsonl()
        print(f"Found {len(all_varieties)} total unique varieties")
        
        print("Identifying unknown varieties...")
        unknown_varieties = self._find_unknown_varieties(all_varieties)
        print(f"Found {len(unknown_varieties)} unknown varieties")
        
        if not unknown_varieties:
            print("No unknown varieties to process!")
            return {"processed": 0, "total_unknown": 0}
        
        # Limit the batch size
        batch = unknown_varieties[:limit]
        print(f"Processing batch of {len(batch)} varieties (limited to {limit})")
        
        # Show some examples
        print(f"Examples: {', '.join(batch[:10])}{'...' if len(batch) > 10 else ''}")
        
        print("Calling GPT-5 for classification...")
        prompt = self._build_classification_prompt(batch)
        additions = self._call_gpt5(prompt)
        
        if not additions:
            print("No additions received from GPT-5")
            return {"processed": 0, "total_unknown": len(unknown_varieties)}
        
        print(f"Received additions for {len(additions)} varieties")
        
        # Show addition stats
        total_new_aliases = 0
        for variety_name, variety_data in additions.items():
            if isinstance(variety_data, dict) and "aliases" in variety_data:
                alias_count = len(variety_data["aliases"])
                total_new_aliases += alias_count
                print(f"  {variety_name}: {alias_count} aliases")
        
        # Merge and save
        print("Merging additions into existing mapping...")
        updated_mapping = self._merge_classifications(additions)
        
        print("Saving updated mapping...")
        self._save_mapping(updated_mapping)
        
        # Update internal state for next iteration
        self.existing_mapping = updated_mapping
        self.existing_aliases = self._build_alias_set()
        
        return {
            "processed": total_new_aliases,
            "total_unknown": len(unknown_varieties), 
            "remaining": len(unknown_varieties) - total_new_aliases,
            "varieties_added": len(additions)
        }

def main():
    parser = argparse.ArgumentParser(description="Normalize grape varieties using GPT-5 northeast expert")
    parser.add_argument("--limit", type=int, default=50, 
                       help="Maximum number of varieties to process per iteration (default: 50)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    parser.add_argument("--iterations", type=int, default=1,
                       help="Number of iterations to run (default: 1)")
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    normalizer = VarietyNormalizer(dry_run=args.dry_run)
    
    print(f"Starting grape variety normalization with northeast hybrid expert...")
    print(f"Limit per iteration: {args.limit}")
    print(f"Iterations: {args.iterations}")
    print(f"Dry run: {args.dry_run}")
    print("-" * 50)
    
    total_processed = 0
    
    for iteration in range(args.iterations):
        print(f"\n=== ITERATION {iteration + 1} ===")
        
        stats = normalizer.process_varieties(limit=args.limit)
        
        total_processed += stats["processed"]
        
        print(f"\nIteration {iteration + 1} Results:")
        print(f"  Processed: {stats['processed']}")
        print(f"  Total unknown remaining: {stats.get('remaining', 0)}")
        
        if stats.get("categories"):
            print("  Categories:")
            for category, count in stats["categories"].items():
                print(f"    {category}: {count}")
        
        # Stop if no more varieties to process
        if stats.get("remaining", 0) == 0:
            print("\nAll unknown varieties have been processed!")
            break
    
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Total varieties processed: {total_processed}")
    print(f"Iterations completed: {min(iteration + 1, args.iterations)}")

if __name__ == "__main__":
    main()