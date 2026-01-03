#!/usr/bin/env python3
"""
Canadian Province Winery Research System

AI-powered system for discovering comprehensive winery lists in Canadian 
provinces where no public registry exists. Uses OpenAI web search to find 
wineries with threaded processing for efficient coverage.

PURPOSE: Canadian Winery Discovery - Research comprehensive winery lists by province

PREREQUISITES:
- None (standalone script - generates the source data for other scripts)

INPUTS:
- None (uses web search to discover wineries)
- Optional: Previous winery list for supplemental research

OUTPUTS:
- data/can/canada_province_wineries.jsonl (one winery per line with province_code)

DEPENDENCIES:
- OPENAI_API_KEY environment variable
- OpenAI API (gpt-5.2 model with web_search tool)

USAGE:
# Research specific provinces
uv run src/00_canada_province_winery_researcher.py --province "NB,NL,NS,PE" --yes --threads 4

# Supplemental research building on existing data
uv run src/00_canada_province_winery_researcher.py --province "NB,NL,NS,PE" --previous-list data/can/canada_province_wineries.jsonl --yes --threads 4

# Research all Canadian provinces  
uv run src/00_canada_province_winery_researcher.py --all-provinces --yes

FUNCTIONALITY:
- Uses AI web search to discover wineries from tourism sites, wine associations, directories
- Searches administrative sub-regions within each province for comprehensive coverage
- Supports supplemental research to find additional wineries not in existing lists
- Threaded processing for efficient multi-province research
- Deduplicates findings against existing winery lists
- Saves one winery per line in JSONL format for downstream processing
"""

import json
import os
import threading
import time
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import openai
from dotenv import load_dotenv

load_dotenv()

CANADIAN_PROVINCES = {
    'AB': 'Alberta',
    'BC': 'British Columbia', 
    'MB': 'Manitoba',
    'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador',
    'NS': 'Nova Scotia',
    'NT': 'Northwest Territories',
    'NU': 'Nunavut',
    'ON': 'Ontario',
    'PE': 'Prince Edward Island',
    'QC': 'Quebec',
    'SK': 'Saskatchewan',
    'YT': 'Yukon'
}


def create_province_winery_research_prompt(province_name: str, existing_wineries: List[Dict] = None) -> str:
    """Create research prompt for finding wineries in a Canadian province."""
    
    # Build existing wineries context if provided
    existing_context = ""
    if existing_wineries:
        existing_list = "\n".join([f"- {w.get('business_name', 'Unknown')} ({w.get('location', 'Unknown location')})" 
                                  for w in existing_wineries[:50]])  # Limit to first 50 to avoid token limits
        existing_context = f"""

EXISTING WINERIES ALREADY KNOWN:
The following wineries are already documented for {province_name}:
{existing_list}
{"... (and more)" if len(existing_wineries) > 50 else ""}

YOUR TASK: Find ADDITIONAL wineries not in the above list. Do a comprehensive second-pass search to discover any wineries that might have been missed in the initial research."""
    
    prompt = f"""
Research and find {"additional" if existing_wineries else "a comprehensive list of"} wineries, vineyards, and wine producers in {province_name}, Canada.

PRIORITY: Find the most exhaustive list possible from online sources including:
- Official tourism websites
- Wine association directories  
- List all the administrative sub-regions and for each of them, search for wineries.
- Winery trail websites
- Regional tourism boards
- Wine review sites and blogs
- Social media and business listings {existing_context}

For EACH {"additional" if existing_wineries else ""} winery/vineyard/producer found, extract ONLY these 2 fields:
1. **Business name** - Official business/winery name
2. **Location** - Location string (can be city, full address, or partial address)

IMPORTANT REQUIREMENTS:
- Focus on active, currently operating wineries/vineyards
- Include ALL types: commercial wineries, small boutique producers, farm wineries, estate wineries
- Prioritize finding business names that are searchable and verifiable
- Location can be as simple as "City, Province" or as detailed as full street address
- Exclude wine shops, liquor stores, or distributors (only producers)
- If uncertain about operation status, include it anyway
{"- Do NOT repeat wineries from the existing list above" if existing_wineries else ""}

Return results in this EXACT JSON format:

{{
    "province": "{province_name}",
    "search_date": "{time.strftime('%Y-%m-%d')}",
    "total_found": <number>,
    "wineries": [
        {{
            "business_name": "Exact official business name",
            "address": "Street address (e.g. 123 Main Road) or null if not available",
            "city": "City name only (e.g. Halifax, Moncton) or null if not specified"
        }}
    ],
    "sources_consulted": [
        "List of key websites/sources used for research"
    ]
}}

Be thorough and find as many {"additional" if existing_wineries else ""} legitimate wine producers as possible. Return only valid JSON.
"""
    
    return prompt


def research_province_wineries(province_name: str, api_key: str, request_delay: float = 2.0, existing_wineries: List[Dict] = None) -> Dict:
    """Research wineries in a specific Canadian province."""
    
    print(f"🔍 {'Supplemental' if existing_wineries else 'Initial'} research for wineries in {province_name}...")
    if existing_wineries:
        print(f"   📋 Building on {len(existing_wineries)} existing wineries")
    
    try:
        prompt = create_province_winery_research_prompt(province_name, existing_wineries)
        
        # Rate limiting
        if request_delay > 0:
            time.sleep(request_delay)
        
        # Create OpenAI client
        client = openai.OpenAI(api_key=api_key, timeout=60*60)
        
        response = client.responses.create(
            model="gpt-5.2",
            tools=[{"type": "web_search"}],
            input=prompt,
            reasoning={
                "effort": "medium"  # Use high effort for comprehensive research
            }
        )
        
        # Parse JSON response
        try:
            research_data = json.loads(response.output_text)
            
            # Add metadata
            research_data.update({
                'researched_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            winery_count = research_data.get('total_found', len(research_data.get('wineries', [])))
            search_desc = "additional" if existing_wineries else ""
            print(f"   ✅ Found {winery_count} {search_desc} wineries in {province_name}")
            
            return research_data
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing failed: {str(e)[:200]}"
            print(f"   ❌ {province_name} - {error_msg}")
            
            return {
                'province': province_name,
                'error': error_msg,
                'researched_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
    except Exception as e:
        error_msg = f"Research failed: {str(e)[:200]}"
        print(f"   ❌ {province_name} - {error_msg}")
        
        return {
            'province': province_name,
            'error': error_msg,
            'researched_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }


def load_previous_winery_list(previous_file: str, target_provinces: List[str] = None) -> Dict[str, List[Dict]]:
    """Load existing winery list from a previous research file for specific provinces."""
    province_wineries = {}
    if not os.path.exists(previous_file):
        print(f"⚠️ Previous winery file not found: {previous_file}")
        return province_wineries
    
    try:
        with open(previous_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        entry = json.loads(line.strip())
                        
                        # Check for province in different possible formats
                        province = entry.get('province')  # Old format
                        province_code = entry.get('province_code')  # New format
                        
                        # Convert province code to full name if needed
                        if province_code and not province:
                            province = CANADIAN_PROVINCES.get(province_code, province_code)
                        
                        # Handle both old format (wineries array) and new format (one per line)
                        if 'wineries' in entry:
                            # Old format: one province entry with wineries array
                            wineries = entry.get('wineries', [])
                            if province and wineries and (not target_provinces or province in target_provinces):
                                if province not in province_wineries:
                                    province_wineries[province] = []
                                province_wineries[province].extend(wineries)
                        elif 'business_name' in entry:
                            # New format: one winery per line with province_code
                            if province and (not target_provinces or province in target_provinces):
                                if province not in province_wineries:
                                    province_wineries[province] = []
                                winery = {
                                    'business_name': entry.get('business_name'),
                                    'location': f"{entry.get('city', '')}, {province_code}" if entry.get('city') else province_code
                                }
                                province_wineries[province].append(winery)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Error parsing line {line_num}: {str(e)[:100]}")
                        continue
        
        total_wineries = sum(len(wineries) for wineries in province_wineries.values())
        if province_wineries:
            print(f"📋 Loaded {total_wineries} existing wineries for {len(province_wineries)} target province(s)")
            
            # Show summary by province
            for province, wineries in province_wineries.items():
                print(f"   • {province}: {len(wineries)} wineries")
        else:
            print(f"📋 No existing wineries found for target provinces: {target_provinces}")
        
    except Exception as e:
        print(f"⚠️ Error loading previous winery list: {e}")
    
    return province_wineries


def load_existing_research(output_file: str) -> Dict[str, Dict]:
    """Load existing research results from file."""
    research_cache = {}
    if not os.path.exists(output_file):
        return research_cache
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line.strip())
                    province = entry.get('province')
                    region_focus = entry.get('region_focus')
                    cache_key = f"{province}_{region_focus or 'all'}"
                    research_cache[cache_key] = entry
        print(f"📋 Loaded {len(research_cache)} cached research entries")
    except Exception as e:
        print(f"⚠️ Error loading research cache: {e}")
    
    return research_cache


def get_province_code(province_name: str) -> str:
    """Convert full province name to 2-letter code."""
    province_codes = {
        'Alberta': 'AB',
        'British Columbia': 'BC', 
        'Manitoba': 'MB',
        'New Brunswick': 'NB',
        'Newfoundland and Labrador': 'NL',
        'Nova Scotia': 'NS',
        'Northwest Territories': 'NT',
        'Nunavut': 'NU',
        'Ontario': 'ON',
        'Prince Edward Island': 'PE',
        'Quebec': 'QC',
        'Saskatchewan': 'SK',
        'Yukon': 'YT'
    }
    return province_codes.get(province_name, province_name)


def save_wineries_to_file(research_entry: Dict, output_file: str, file_lock: threading.Lock):
    """Thread-safe save wineries to output file (one winery per line)."""
    with file_lock:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'a', encoding='utf-8') as f:
            wineries = research_entry.get('wineries', [])
            province = research_entry.get('province')
            province_code = get_province_code(province)
            researched_at = research_entry.get('researched_at')
            
            for winery in wineries:
                winery_entry = {
                    'province_code': province_code,
                    'business_name': winery.get('business_name'),
                    'address': winery.get('address'),
                    'city': winery.get('city'),
                    'researched_at': researched_at
                }
                f.write(json.dumps(winery_entry, ensure_ascii=False) + '\n')


def process_province_research(province_requests: List[Dict], api_key: str, output_file: str,
                            request_delay: float = 3.0, max_threads: int = 3, 
                            previous_wineries: Dict[str, List[Dict]] = None) -> Dict:
    """Process multiple province research requests with threading."""
    
    # Load existing research
    cache = load_existing_research(output_file)
    
    # Filter out already researched provinces (unless doing supplemental research)
    requests_to_process = []
    for req in province_requests:
        province = req['province']
        cache_key = province
        
        # If doing supplemental research, process even if cached
        if previous_wineries or cache_key not in cache:
            requests_to_process.append(req)
        else:
            print(f"📋 {province} already researched")
    
    print(f"🍷 Total research requests: {len(province_requests)}")
    print(f"📋 Already researched: {len(cache)}")
    print(f"🎯 New research needed: {len(requests_to_process)}")
    
    if not requests_to_process:
        print("✅ All provinces already researched!")
        return {
            'total_requests': len(province_requests),
            'cached_research': len(cache),
            'new_research_completed': 0,
            'processing_time_minutes': 0
        }
    
    # Threading setup
    file_lock = threading.Lock()
    
    print(f"\n🔍 Starting Canadian winery research with {max_threads} threads...")
    print(f"📊 Estimated cost: ${len(requests_to_process) * 0.15:.2f} (${0.15:.2f} per province)")
    print(f"⏱️  Estimated time: {len(requests_to_process) * request_delay / max_threads / 60:.1f} minutes")
    
    start_time = time.time()
    research_results = []
    errors = []
    
    def process_single_request(req):
        """Process a single research request."""
        try:
            # Get existing wineries for this province if available
            existing_wineries = None
            if previous_wineries:
                existing_wineries = previous_wineries.get(req['province'])
            
            result = research_province_wineries(
                req['province'], api_key, request_delay, existing_wineries
            )
            
            if 'error' not in result:
                # For supplemental research, filter out duplicates but just save new ones
                if existing_wineries:
                    new_wineries = result.get('wineries', [])
                    existing_names = {w.get('business_name', '').lower() for w in existing_wineries}
                    
                    # Filter to only truly new wineries
                    unique_new_wineries = []
                    for new_winery in new_wineries:
                        new_name = new_winery.get('business_name', '').lower()
                        if new_name and new_name not in existing_names:
                            unique_new_wineries.append(new_winery)
                    
                    # Update result to only contain new wineries
                    result['wineries'] = unique_new_wineries
                    result['total_found'] = len(unique_new_wineries)
                    result['existing_wineries_count'] = len(existing_wineries)
                    result['is_supplemental'] = True
                
                # Save wineries to file (one per line, append mode)
                save_wineries_to_file(result, output_file, file_lock)
            
            return result
            
        except Exception as e:
            error_data = {
                'province': req['province'],
                'error': f"Processing failed: {str(e)[:200]}",
                'researched_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            return error_data
    
    # Process requests concurrently
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_request = {
            executor.submit(process_single_request, req): req
            for req in requests_to_process
        }
        
        # Collect results as they complete
        for i, future in enumerate(as_completed(future_to_request), 1):
            req = future_to_request[future]
            province_name = req['province']
            
            try:
                result = future.result()
                
                if 'error' in result:
                    errors.append(result)
                    print(f"[{i}/{len(requests_to_process)}] ❌ {province_name} - {result.get('error', 'Unknown error')}")
                else:
                    research_results.append(result)
                    winery_count = result.get('total_found', len(result.get('wineries', [])))
                    
                    # Show different messages based on whether supplemental research
                    if result.get('is_supplemental'):
                        existing_count = result.get('existing_wineries_count', 0)
                        print(f"[{i}/{len(requests_to_process)}] ✅ {province_name} - {winery_count} new wineries found (adding to {existing_count} existing)")
                    else:
                        print(f"[{i}/{len(requests_to_process)}] ✅ {province_name} - {winery_count} wineries found")
                    
            except Exception as exc:
                error_data = {
                    'province': province_name,
                    'error': f"Thread exception: {str(exc)[:200]}",
                    'researched_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                errors.append(error_data)
                print(f"[{i}/{len(requests_to_process)}] ❌ {province_name} - Thread exception: {exc}")
    
    # Save errors if any
    error_file = None
    if errors:
        error_file = output_file.replace('.jsonl', '_errors.jsonl')
        with open(error_file, 'a', encoding='utf-8') as f:
            for error in errors:
                f.write(json.dumps(error, ensure_ascii=False) + '\n')
    
    # Calculate statistics
    end_time = time.time()
    duration_minutes = (end_time - start_time) / 60
    
    results = {
        'total_requests': len(province_requests),
        'cached_research': len(cache),
        'new_research_completed': len(research_results),
        'errors': len(errors),
        'success_rate': len(research_results) / len(requests_to_process) * 100 if requests_to_process else 100,
        'processing_time_minutes': round(duration_minutes, 2),
        'threads_used': max_threads,
        'output_file': output_file,
        'error_file': error_file
    }
    
    print(f"\n✅ Canadian Province Winery Research Complete!")
    print(f"🧵 Processed with {max_threads} threads")
    print(f"📁 Output saved to: {output_file}")
    print(f"🍷 New research completed: {len(research_results)}")
    print(f"📋 Total research in cache: {len(cache) + len(research_results)}")
    print(f"📊 Success rate: {results['success_rate']:.1f}%")
    print(f"⏱️  Total time: {results['processing_time_minutes']:.1f} minutes")
    
    if errors:
        print(f"⚠️  {len(errors)} errors saved to: {error_file}")
    
    return results


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Canadian Province Winery Research')
    parser.add_argument('--province', 
                       help='Specific province(s) to research (code or full name, comma-separated for multiple)')
    parser.add_argument('--all-provinces', action='store_true',
                       help='Research all Canadian provinces')
    parser.add_argument('--output', default='data/can/canada_province_wineries.jsonl',
                       help='Output file for research results')
    parser.add_argument('--delay', type=float, default=3.0,
                       help='Delay between API requests (seconds)')
    parser.add_argument('--threads', type=int, default=3,
                       help='Number of concurrent threads (default: 3)')
    parser.add_argument('--previous-list', help='Previous winery list file to build upon (supplemental research)')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return
    
    # Determine research requests
    province_requests = []
    
    if args.province:
        # Parse comma-separated provinces
        province_inputs = [p.strip() for p in args.province.split(',')]
        
        for province_input in province_inputs:
            province_name = province_input
            if province_name in CANADIAN_PROVINCES:
                province_name = CANADIAN_PROVINCES[province_name]
            elif province_name not in CANADIAN_PROVINCES.values():
                print(f"❌ Unknown province: {province_name}")
                print(f"Available provinces: {', '.join(CANADIAN_PROVINCES.values())}")
                return
            
            province_requests.append({
                'province': province_name
            })
        
    elif args.all_provinces:
        # All provinces research
        for province_name in CANADIAN_PROVINCES.values():
            province_requests.append({
                'province': province_name
            })
    else:
        parser.print_help()
        print("\n❌ Please specify --province or --all-provinces")
        return
    
    # Load previous winery list if provided (only for target provinces)
    previous_wineries = None
    if args.previous_list:
        target_provinces = [req['province'] for req in province_requests]
        previous_wineries = load_previous_winery_list(args.previous_list, target_provinces)
        if not previous_wineries:
            print("❌ No wineries loaded from previous list for target provinces")
            return
    
    # Check existing research
    cache = load_existing_research(args.output)
    
    requests_to_process = []
    for req in province_requests:
        cache_key = req['province']
        
        # If we have a previous list (supplemental research), always process even if cached
        # Otherwise, only process if not in cache
        if args.previous_list or cache_key not in cache:
            requests_to_process.append(req)
    
    estimated_cost = len(requests_to_process) * 0.15
    estimated_time = len(requests_to_process) * args.delay / args.threads / 60
    
    print(f"\n🍷 Canadian Province Winery Research Plan:")
    print(f"🎯 Total requests: {len(province_requests)}")
    print(f"📋 Already researched: {len(cache)}")
    print(f"🆕 New research needed: {len(requests_to_process)}")
    if args.previous_list:
        total_previous = sum(len(wineries) for wineries in previous_wineries.values())
        print(f"📚 Previous wineries loaded: {total_previous} (supplemental research mode)")
    print(f"🧵 Threads: {args.threads}")
    print(f"💰 Estimated cost: ${estimated_cost:.2f}")
    print(f"⏱️  Estimated time: {estimated_time:.1f} minutes")
    print(f"📁 Output file: {args.output}")
    
    if len(requests_to_process) == 0:
        print("✅ All requested research already completed!")
        return
    
    if not args.yes:
        confirm = input("\n🚀 Proceed with winery research? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Research cancelled")
            return
    
    # Process research requests
    results = process_province_research(
        province_requests, api_key, args.output, args.delay, args.threads, previous_wineries
    )
    
    print(f"\n🎉 Research completed! Results: {results}")


if __name__ == "__main__":
    main()