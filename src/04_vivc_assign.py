#!/usr/bin/env python3
"""
VIVC Assignment Script

Assigns VIVC passport data to grape varieties using GPT-powered search with React 
tool calling for dynamic VIVC database queries.

PURPOSE: VIVC Data Assignment - Assign passport data to grape varieties using AI search

INPUTS:
- data/grape_variety_mapping.jsonl (via GrapeVarietiesModel)

OUTPUTS:
- data/grape_variety_mapping.jsonl (updated with VIVC assignments and passport data)

DEPENDENCIES:
- OPENAI_API_KEY environment variable
- OpenAI API (gpt-5 model)
- includes.vivc_client for VIVC database search
- includes.grape_varieties.GrapeVarietiesModel

USAGE:
# Test with 5 varieties
uv run src/04_vivc_assign.py --limit 5

# Process all unprocessed varieties
uv run src/04_vivc_assign.py

# Reprocess varieties previously marked as not found
uv run src/04_vivc_assign.py --reprocess-not-found

FUNCTIONALITY:
- Uses React tool calling loop where GPT can search VIVC database dynamically
- Specialized for cold-climate hybrids grown in northeastern North America
- Searches with multiple strategies: exact name, wildcard patterns, aliases
- Fetches full passport data when VIVC number found
- Updates variety records with assignment status: found/not_found/error/skipped_not_grape
"""

import argparse
import sys
import json
import os
from pathlib import Path
from typing import Optional, List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Import our modules
from includes.grape_varieties import GrapeVarietiesModel, GrapeVariety
from includes.vivc_client import search_cultivar, get_passport_data, VarietySearchResult, PassportData


class VIVCAssigner:
    """Assigns VIVC passport data to grape varieties using GPT with tool calling."""
    
    def __init__(self, data_dir: str = "data", reprocess_not_found: bool = False):
        self.data_dir = Path(data_dir)
        self.varieties_model = GrapeVarietiesModel(data_dir)
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.reprocess_not_found = reprocess_not_found
    
    def update_variety_in_model(self, variety_name: str, vivc_data: dict, status: str):
        """Update a variety's VIVC data in the model and save to file."""
        variety = self.varieties_model.get_variety(variety_name)
        if variety:
            variety.vivc = vivc_data
            variety.vivc_assignment_status = status
            # Save the entire model back to JSONL
            self.varieties_model.save_jsonl()
            return True
        return False
        
    def search_vivc_tool(self, search_term: str) -> str:
        """Tool function for VIVC search that GPT can call."""
        try:
            results = search_cultivar(search_term)
            if not results:
                return f"No results found for '{search_term}'"
            
            # Format results for GPT
            formatted_results = f"Found {len(results)} results for '{search_term}':\n"
            for i, result in enumerate(results[:10], 1):  # Limit to top 10
                formatted_results += f"{i}. {result.prime_name} (VIVC: {result.vivc_number})\n"
                if result.cultivar_name:
                    f"  Cultivar name: {result.cultivar_name}"
                if result.berry_skin_color:
                    formatted_results += f"   Berry color: {result.berry_skin_color}\n"
                if result.species:
                    formatted_results += f"   Species: {result.species}\n"
                if result.country_of_origin:
                    formatted_results += f"   Origin: {result.country_of_origin}\n"
                formatted_results += "\n"
            
            #print(formatted_results)
            return formatted_results
            
        except Exception as e:
            return f"Error searching for '{search_term}': {e}"

    def create_system_prompt(self) -> str:
        """Create system prompt for GPT with tool calling."""
        return """You are a wine expert specializing in grape varieties, particularly cold-climate hybrids grown in northeastern North America.

Your task is to find the correct VIVC (Vitis International Variety Catalogue) number for grape varieties by searching the VIVC database.

CONTEXT:
- We're working with grape varieties from Quebec and northeastern US
- Many are French-American hybrids (like Seyval Blanc, Vidal, Foch)
- Some are University of Minnesota hybrids (like Frontenac, Marquette, La Crescent)
- Some may have berry color in the name (e.g., "Frontenac Noir" vs just "Frontenac")
- VIVC search may return multiple results for the same base variety with different colors

SEARCH STRATEGY:
- Start by searching the exact variety name
- No not include 'blend' or 'style' which come from wine label. The search is an exact match, the more word, the less result.
- If no results, try removing qualitative words like colors
- Try common aliases and alternative spellings
- When searching ending with, use leading %.
- For breeder codename, always use wildcard '%' instead of '-', '.' or ' '. Ex: '%1%2%3' for anything ending with this code number. 
- If you cannot find with '%1%2%3', NEVER retry more specific search like '1-2-3'
- When multiple words, you can search a single one.
- It is possible that the name contains a typo. If nothing found at first and the name looks familiar, try a typo fix.
- Always goes from specific to generic. If 'Pinot' not found, no reason to go more restrictive with 'Pinot Noir'.
- Some varieties may not be in VIVC at all (very new hybrids, proprietary crosses)
- Look for berry color matches when multiple results exist

INSTRUCTIONS:
1. Use the search_vivc tool to search for the variety
2. Analyze the results to find the best match
3. Try different search terms if needed
4. When you find a good match, respond with just the VIVC number
5. If you cannot find any good match after reasonable attempts, respond with "NOT_FOUND"

Be thorough but efficient. Don't search for obviously unrelated terms.
IMPORTANT: Always favor the "Prime name" for selecting the associated VIVC number.
"""

    def find_vivc_for_variety(self, variety: GrapeVariety) -> Optional[str]:
        """Find VIVC number using React tool calling loop."""
        print(f"\n🔍 Processing: {variety.name}")
        
        # Prepare initial message with variety info
        initial_message = f"""Find the VIVC number for the grape variety: "{variety.name}"

Known aliases: {', '.join(variety.aliases[:10])}{'...' if len(variety.aliases) > 10 else ''}

Use the search_vivc tool to search the VIVC database. Try different search terms as needed.
When you find the correct variety, respond with just the VIVC number.
If you cannot find it after reasonable attempts, respond with "NOT_FOUND"."""

        messages = [
            {"role": "system", "content": self.create_system_prompt()},
            {"role": "user", "content": initial_message}
        ]
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            example_search: """
                'Pinot' will match 'Pinot Noir'
                'Noir' wont match 'Pinot Noir'
                '%Noir' will match 'Pinot Noir' # Always use leading wildcard for ending with
                'Seyve%Villard 5%276' will match 'Seyve Villard 5-276'
                '%5%276 will match 'Seyve Villard 5.276'
            """

            try:
                response = self.client.chat.completions.create(
                    model="gpt-5",
                    messages=messages,
                    tools=[{
                        "type": "function",
                        "function": {
                            "name": "search_vivc",
                            "description": "Search the VIVC database for grape varieties. For searching complex names, eg. with numbers use the wildcard %. Example: Seibel%616 instead of ' ' or '-' " ,
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "search_term": {
                                        "type": "string",
                                        "description": "The search string to look for in VIVC. (case insensitive). Examples: {example_search}"
                                    }
                                },
                                "required": ["search_term"]
                            }
                        }
                    }],
                    #temperature=0
                )
                
                message = response.choices[0].message
                
                # Check if GPT wants to call a tool
                if message.tool_calls:
                    # Add the assistant message first
                    messages.append(message)
                    
                    # Handle all tool calls
                    for tool_call in message.tool_calls:
                        if tool_call.function.name == "search_vivc":
                            args = json.loads(tool_call.function.arguments)
                            search_term = args["search_term"]
                            
                            print(f"  🔍 GPT searching: '{search_term}'")
                            search_result = self.search_vivc_tool(search_term)
                            
                            # Add tool result to conversation
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": search_result
                            })
                    
                    continue  # Continue the loop to get GPT's response
                
                # GPT provided a final answer
                if message.content:
                    content = message.content.strip()
                    
                    if content == "NOT_FOUND":
                        print(f"  ❌ GPT could not find VIVC number")
                        return None
                    
                    # Check if it's a VIVC number (should be digits)
                    if content.isdigit():
                        print(f"  ✅ GPT found VIVC: {content}")
                        return content
                    
                    # If it's not a number, it might be explanatory text
                    # Look for numbers in the response
                    import re
                    numbers = re.findall(r'\b\d{4,6}\b', content)
                    if numbers:
                        vivc_num = numbers[0]
                        print(f"  ✅ GPT found VIVC: {vivc_num}")
                        return vivc_num
                    
                    print(f"  ❌ GPT response unclear: {content}")
                    return None
                
            except Exception as e:
                print(f"  ⚠️  Error in tool calling loop: {e}")
                return None
        
        print(f"  ❌ Max iterations reached")
        return None

    def enrich_variety(self, variety: GrapeVariety) -> bool:
        """Enrich a single variety with VIVC data and update the model."""
        print(f"🔍 Processing: {variety.name}")
        
        if not variety.grape:
            self.update_variety_in_model(variety.name, None, "skipped_not_grape")
            print(f"  ⏭️  Skipped (not a grape variety)")
            return True
        
        try:
            vivc_number = self.find_vivc_for_variety(variety)
            
            if vivc_number:
                print(f"  📋 Fetching passport data...")
                passport_data = get_passport_data(vivc_number)
                self.update_variety_in_model(variety.name, passport_data.to_dict(), "found")
                print(f"  ✅ Successfully enriched {variety.name}")
                return True
            else:
                self.update_variety_in_model(variety.name, None, "not_found")
                print(f"  ❌ Could not find VIVC for {variety.name}")
                return True
                
        except Exception as e:
            self.update_variety_in_model(variety.name, None, "error")
            print(f"  ⚠️  Error enriching {variety.name}: {e}")
            return False

    def process_all_varieties(self, limit: Optional[int] = None) -> int:
        """Process all grape varieties."""
        all_varieties = self.varieties_model.get_grape_varieties()
        
        # By default, skip varieties with not_found/error status unless reprocessing
        if not self.reprocess_not_found:
            grape_varieties = [v for v in all_varieties 
                             if not (hasattr(v, 'vivc_assignment_status') and 
                                     v.vivc_assignment_status in ['not_found', 'error', 'found'])]
        else:
            grape_varieties = all_varieties
        
        # Apply limit to varieties to process
        if limit:
            grape_varieties = grape_varieties[:limit]
        
        total_varieties = len(all_varieties)
        to_process = len(grape_varieties)
        
        print(f"🚀 Total varieties: {total_varieties}, To process: {to_process}")
        
        processed_count = 0
        
        for i, variety in enumerate(grape_varieties, 1):
            print(f"\n[{i}/{to_process}] ")
            if self.enrich_variety(variety):
                processed_count += 1
        
        return processed_count

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about all varieties in the model."""
        all_varieties = self.varieties_model.get_all_varieties()
        stats = {
            "total": len(all_varieties),
            "found": len([v for v in all_varieties if hasattr(v, 'vivc_assignment_status') and v.vivc_assignment_status == "found"]),
            "not_found": len([v for v in all_varieties if hasattr(v, 'vivc_assignment_status') and v.vivc_assignment_status == "not_found"]),
            "error": len([v for v in all_varieties if hasattr(v, 'vivc_assignment_status') and v.vivc_assignment_status == "error"]),
            "skipped": len([v for v in all_varieties if hasattr(v, 'vivc_assignment_status') and v.vivc_assignment_status == "skipped_not_grape"]),
            "unprocessed": len([v for v in all_varieties if not hasattr(v, 'vivc_assignment_status') or v.vivc_assignment_status is None])
        }
        return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Assign VIVC passport data to grape varieties",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/04_vivc_assign.py --limit 5     # Process first 5 varieties
  python src/04_vivc_assign.py               # Process all varieties
        """
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of varieties to process (for testing)"
    )
    
    parser.add_argument(
        "--reprocess-not-found",
        action="store_true",
        help="Reprocess varieties with not_found status (default: skip them)"
    )
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    try:
        assigner = VIVCAssigner(reprocess_not_found=args.reprocess_not_found)
        processed_count = assigner.process_all_varieties(args.limit)
        
        # Show statistics
        stats = assigner.get_stats()
        print(f"\n📊 Results:")
        print(f"  Varieties processed this run: {processed_count}")
        print(f"  Total varieties: {stats['total']}")
        print(f"  VIVC found: {stats['found']}")
        print(f"  Not found: {stats['not_found']}")
        print(f"  Errors: {stats['error']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Unprocessed: {stats['unprocessed']}")
        
        success_rate = stats['found'] / (stats['total'] - stats['skipped'] - stats['unprocessed']) * 100 if (stats['total'] - stats['skipped'] - stats['unprocessed']) > 0 else 0
        print(f"  Success rate: {success_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()