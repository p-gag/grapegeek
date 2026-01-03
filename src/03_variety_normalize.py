#!/usr/bin/env python3
"""
Grape Variety Normalization Script

AI-powered grape variety classification using GPT-5 with northeast grape variety 
expertise specializing in cold-climate hybrid grapes.

PURPOSE: Variety Classification - Normalize and classify unknown grape varieties

INPUTS:
- data/enriched_producers_cache.jsonl (enriched producer data)
- data/grape_variety_mapping.jsonl (existing grape varieties mapping)

OUTPUTS:
- data/grape_variety_mapping.jsonl (updated with new variety classifications)

DEPENDENCIES:
- OPENAI_API_KEY environment variable
- OpenAI API (gpt-5.2 model with web_search tool)
- includes.grape_varieties.GrapeVarietiesModel

USAGE:
# Process up to 50 varieties
uv run src/03_variety_normalize.py

# Custom batch size and multiple iterations
uv run src/03_variety_normalize.py --limit 30 --iterations 3

# Dry run to see what would be processed
uv run src/03_variety_normalize.py --dry-run

FUNCTIONALITY:
- Extracts unique cepage varieties from enriched producer data
- Identifies unknown varieties not in existing mapping
- Uses GPT-5 with northeast grape expert to classify unknown varieties
- Handles four classification types: alias, new grape variety, fruit, unknown/blend
- Merges AI classifications into GrapeVarietiesModel

⚠️ MANUAL REVIEW REQUIRED: AI classification can be imprecise for new varieties
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

# Import the grape varieties model
sys.path.insert(0, str(Path(__file__).parent))
from includes.grape_varieties import GrapeVarietiesModel, GrapeVariety

class VarietyNormalizer:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.mapping_file = Path("data/grape_variety_mapping.jsonl")
        self.input_file = Path("data/enriched_producers_cache.jsonl")
        
        # Load existing mapping using GrapeVarietiesModel
        self.grape_model = GrapeVarietiesModel()
        
    
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
            # Use the grape model's normalize function to check if variety exists
            if not self.grape_model.normalize_variety_name(variety):
                unknown.append(variety)
        
        return unknown
    
    def _build_classification_prompt(self, unknown_varieties: List[str]) -> str:
        """Build the GPT prompt for variety classification.
        
        IMPORTANT: The Fruit and Unknown categories contain massive lists (hundreds of aliases)
        that would exceed token limits. We only send a few examples of these categories
        to the AI, not the full lists. This is essential to keep prompts manageable.
        """
        
        # Build the mapping using GrapeVarietiesModel
        # Override Fruit/Unknown with examples, use real aliases for grape varieties
        simplified_mapping = {}
        
        # Get all varieties from the model
        all_varieties = self.grape_model.get_all_varieties()
        
        # Override examples for massive categories to save tokens
        fruit_examples = ["apple", "apple (fruit wine)", "blueberry", "cherry", "peach", "strawberry"]
        unknown_examples = ["blend", "red blend", "cold-hardy hybrid (unspecified)", "unknown", "proprietary blend"]
        
        for variety in all_varieties:
            if variety.name == "Fruit":
                simplified_mapping[variety.name] = {"aliases": fruit_examples}
            elif variety.name == "Unknown":
                simplified_mapping[variety.name] = {"aliases": unknown_examples}
            else:
                # Keep all actual grape varieties with their real aliases
                simplified_mapping[variety.name] = {"aliases": variety.aliases}
        
        # Convert mapping to JSON format for the prompt (instead of YAML)
        mapping_json = json.dumps({"grape_variety_mapping": simplified_mapping}, 
                                 indent=2, ensure_ascii=False)
        
        prompt = f"""You are a northeast North American grape variety expert with special expertise in cold-climate hybrid grapes.

Here is the current grape variety mapping:

```json
{mapping_json}
```

For each unknown variety below, classify it by either:
1. **Adding alias to existing variety** - if it matches a known grape variety
2. **Creating new grape variety** - if it's a new specific grape variety or when the name look like grape name.
3. **Adding to Fruit** - if it's a non-grape fruit  
4. **Adding to Unknown** - if it's vague/unspecified (blends, "estate varieties", etc.). 

**IMPORTANT**: If you are uncertain about a specific grape variety, use web search to verify:
- Search for the grape variety name + "wine grape variety" or "hybrid grape"
- Check if it's a real grape variety vs. a misspelling of an existing one
- Verify the correct spelling and any common aliases

Return ONLY the additions in the exact same JSON format. For example:

```json
{{
  "Chambourcin": {{
    "aliases": ["chambourcin"]
  }},
  "Fruit": {{
    "aliases": ["new_fruit_name"]
  }},
  "Unknown": {{
    "aliases": ["some_vague_blend"]
  }}
}}
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
            response = self.client.responses.create(
                model="gpt-5.2",
                tools=[{"type": "web_search"}],
                input=prompt,
                reasoning={
                    "effort": "medium" 
                }
            )
            
            content = response.output_text.strip()
            
            # Try to parse YAML response
            try:
                # Try to extract JSON from response if wrapped in markdown
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    json_str = content[start:end].strip()
                    return json.loads(json_str) or {}
                elif "```" in content:
                    # Try generic code block
                    start = content.find("```") + 3
                    end = content.rfind("```")
                    if end > start:
                        json_str = content[start:end].strip()
                        return json.loads(json_str) or {}
                else:
                    # Try to parse the whole content as JSON
                    return json.loads(content) or {}
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Content: {content}")
                return {}
                    
        except Exception as e:
            print(f"Error calling GPT-5: {e}")
            return {}
    
    def _merge_classifications(self, additions: Dict) -> bool:
        """Merge AI classifications into the GrapeVarietiesModel."""
        if not additions:
            return False
        
        changes_made = False
        
        for variety_name, variety_data in additions.items():
            if not isinstance(variety_data, dict) or "aliases" not in variety_data:
                print(f"Warning: Skipping invalid variety data for '{variety_name}': {variety_data}")
                continue
            
            aliases = variety_data["aliases"]
            if not isinstance(aliases, list):
                print(f"Warning: Aliases for '{variety_name}' is not a list: {aliases}")
                continue
            
            # Get existing variety from model
            existing_variety = self.grape_model.get_variety(variety_name)
            
            if existing_variety:
                # Add new aliases to existing variety
                for alias in aliases:
                    if alias and alias not in existing_variety.aliases:
                        existing_variety.aliases.append(alias)
                        changes_made = True
                        print(f"  Added alias '{alias}' to '{variety_name}'")
            else:
                # Create new variety
                from includes.grape_varieties import GrapeVariety
                new_variety = GrapeVariety(
                    name=variety_name,
                    aliases=[alias for alias in aliases if alias],
                    grape=(variety_name not in ["Fruit", "Unknown"]),  # Fruit/Unknown are not grapes
                    vivc=None,
                    vivc_assignment_status=None
                )
                self.grape_model.varieties[variety_name] = new_variety
                changes_made = True
                print(f"  Created new variety '{variety_name}' with {len(new_variety.aliases)} aliases")
        
        return changes_made
    
    def _save_mapping(self) -> None:
        """Save the updated mapping to JSONL file using GrapeVarietiesModel."""
        if self.dry_run:
            print("DRY RUN - Would save updated mapping to JSONL")
            return
            
        self.grape_model.save_jsonl()
        print(f"✅ Saved updated mapping to {self.grape_model.jsonl_file}")
    
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
        changes_made = self._merge_classifications(additions)
        
        if changes_made:
            print("Saving updated mapping...")
            self._save_mapping()
        else:
            print("No changes made to mapping")
        
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