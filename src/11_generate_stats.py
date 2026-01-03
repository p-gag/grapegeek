#!/usr/bin/env python3
"""
Dataset Statistics Generator for Wine Producers

Analyzes the final normalized wine producer dataset to generate comprehensive 
statistics for reports, social media posts, and performance tracking.

PURPOSE: Statistics Generation - Analyze final dataset for insights and reporting

INPUTS:
- data/05_wine_producers_final_normalized.jsonl (final production dataset)

OUTPUTS:
- dataset_statistics.txt (detailed statistics summary)
- Console output with comprehensive analysis and social media posts

DEPENDENCIES:
- None (analyzes final normalized dataset)

USAGE:
# Generate comprehensive statistics
uv run src/11_generate_stats.py

# Include full grape varieties list
uv run src/11_generate_stats.py --varieties

FUNCTIONALITY:
- Analyzes geographic coverage across US states and Canadian provinces
- Counts total producers, wines, and estimated bottles
- Identifies unique grape varieties and wine types
- Tracks digital presence (websites, social media accounts)
- Generates bilingual social media post content (English/French)
- Provides comprehensive dataset quality metrics
- Creates detailed text report for reference
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set

def load_producer_data() -> List[Dict]:
    """Load the final wine producer dataset."""
    input_file = Path("data/05_wine_producers_final_normalized.jsonl")
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        print("💡 Make sure to run the pipeline first:")
        print("   1. python src/07_data_merge_enriched.py")
        print("   2. python src/09_data_normalize_final.py")
        return []
    
    producers = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    producer = json.loads(line.strip())
                    producers.append(producer)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Error parsing line: {e}")
                    continue
    
    return producers

def analyze_dataset(producers: List[Dict]) -> Dict:
    """Analyze the dataset and generate comprehensive statistics."""
    stats = {
        'total_producers': len(producers),
        'states_provinces': set(),
        'us_states': set(),
        'canadian_provinces': set(),
        'countries': Counter(),
        'total_wines': 0,
        'producers_with_wines': 0,
        'total_wine_bottles': 0,
        'grape_varieties': set(),
        'wine_types': set(),
        'websites_found': 0,
        'social_accounts': 0,
        'producers_with_location': 0,
        'open_for_visits': 0,
        'verified_wine_producers': 0,
        'wine_labels': set(),
        'activities': Counter()
    }
    
    for producer in producers:
        # Geographic analysis
        state_province = producer.get('state_province', '').strip()
        country = producer.get('country', '').strip()
        
        if state_province:
            stats['states_provinces'].add(state_province)
            
            # Classify as US state or Canadian province
            canadian_provinces = ['Quebec', 'Ontario', 'British Columbia', 'Alberta', 'Nova Scotia', 'New Brunswick']
            if state_province in canadian_provinces or country.lower() in ['canada', 'ca']:
                stats['canadian_provinces'].add(state_province)
            else:
                stats['us_states'].add(state_province)
        
        if country:
            stats['countries'][country] += 1
        
        # Location data
        if producer.get('latitude') and producer.get('longitude'):
            stats['producers_with_location'] += 1
        
        # Wine analysis
        wines = producer.get('wines', []) or []
        if wines:
            stats['producers_with_wines'] += 1
            stats['total_wines'] += len(wines)
            
            # Estimate bottles (very rough estimate: assume 100-500 bottles per wine)
            stats['total_wine_bottles'] += len(wines) * 250  # Average estimate
            
            for wine in wines:
                if isinstance(wine, dict):
                    # Grape varieties
                    cepages = wine.get('cepages', []) or []
                    for cepage in cepages:
                        if isinstance(cepage, str) and cepage.strip():
                            stats['grape_varieties'].add(cepage.strip())
                    
                    # Wine types
                    wine_type = wine.get('type')
                    if wine_type and isinstance(wine_type, str):
                        stats['wine_types'].add(wine_type.strip())
        
        # Digital presence
        if producer.get('website'):
            stats['websites_found'] += 1
        
        social_media = producer.get('social_media', []) or []
        if isinstance(social_media, list):
            stats['social_accounts'] += len(social_media)
        
        # Wine labels
        wine_label = producer.get('wine_label')
        if wine_label and isinstance(wine_label, str):
            stats['wine_labels'].add(wine_label.strip())
        
        # Activities and visits
        activities = producer.get('activities', []) or []
        if activities:
            stats['open_for_visits'] += 1
            for activity in activities:
                if isinstance(activity, str):
                    stats['activities'][activity.strip()] += 1
        
        # Verification status
        if producer.get('verified_wine_producer'):
            stats['verified_wine_producers'] += 1
    
    # Convert sets to counts
    stats['unique_states_provinces'] = len(stats['states_provinces'])
    stats['unique_us_states'] = len(stats['us_states'])
    stats['unique_canadian_provinces'] = len(stats['canadian_provinces'])
    stats['unique_grape_varieties'] = len(stats['grape_varieties'])
    stats['unique_wine_types'] = len(stats['wine_types'])
    stats['unique_wine_labels'] = len(stats['wine_labels'])
    
    return stats

def generate_social_media_posts(stats: Dict) -> Dict[str, str]:
    """Generate bilingual vertical social media post."""
    
    # Determine region description
    if stats['unique_canadian_provinces'] > 0 and stats['unique_us_states'] > 0:
        if stats['unique_canadian_provinces'] == 1:
            region_text_en = f"{stats['unique_us_states']} US states and 1 Canadian province"
            region_text_fr = f"{stats['unique_us_states']} États américains et 1 province canadienne"
        else:
            region_text_en = f"{stats['unique_us_states']} US states and {stats['unique_canadian_provinces']} Canadian provinces"
            region_text_fr = f"{stats['unique_us_states']} États américains et {stats['unique_canadian_provinces']} provinces canadiennes"
    elif stats['unique_us_states'] > 0:
        region_text_en = f"{stats['unique_us_states']} US states"
        region_text_fr = f"{stats['unique_us_states']} États américains"
    else:
        region_text_en = f"{stats['unique_canadian_provinces']} Canadian provinces"
        region_text_fr = f"{stats['unique_canadian_provinces']} provinces canadiennes"
    
    posts = {}
    
    # English vertical format
    posts['english'] = f"""🍷 NORTH-EAST WINEGROWER RESEARCH 🗺️

📍 {region_text_en}
🍇 {stats['total_producers']:,} winegrowers researched
🍾 {stats['total_wines']:,} wines catalogued  
🌿 {stats['unique_grape_varieties']} grape varieties
🌐 {stats['websites_found']} websites discovered
📱 {stats['social_accounts']} social accounts identified

#WineMapping #DataResearch #Winegrowers"""
    
    # French vertical format
    posts['french'] = f"""🍷 RECHERCHE VIGNOBLES NORD-EST 🗺️

📍 {region_text_fr}
🍇 {stats['total_producers']:,} vignobles recherchés
🍾 {stats['total_wines']:,} vins catalogués  
🌿 {stats['unique_grape_varieties']} cépages
🌐 {stats['websites_found']} sites web découverts
📱 {stats['social_accounts']} comptes sociaux identifiés

#CartographieVin #RechercheData #Vignobles"""
    
    return posts

def print_detailed_stats(stats: Dict, show_varieties: bool = False):
    """Print detailed statistics about the dataset."""
    print("🍷 WINE PRODUCER DATASET STATISTICS")
    print("=" * 50)
    
    print(f"\n📍 GEOGRAPHIC COVERAGE:")
    print(f"   Total regions: {stats['unique_states_provinces']}")
    print(f"   US states: {stats['unique_us_states']}")
    print(f"   Canadian provinces: {stats['unique_canadian_provinces']}")
    print(f"   Located producers: {stats['producers_with_location']:,}")
    
    print(f"\n🏭 PRODUCER ANALYSIS:")
    print(f"   Total producers: {stats['total_producers']:,}")
    print(f"   Verified wine producers: {stats['verified_wine_producers']:,}")
    print(f"   Producers with wines: {stats['producers_with_wines']:,}")
    print(f"   Open for visits: {stats['open_for_visits']:,}")
    
    print(f"\n🍾 WINE & VARIETY DATA:")
    print(f"   Total wines catalogued: {stats['total_wines']:,}")
    print(f"   Unique grape varieties: {stats['unique_grape_varieties']}")
    print(f"   Unique wine types: {stats['unique_wine_types']}")
    print(f"   Estimated bottles*: {stats['total_wine_bottles']:,}")
    
    if show_varieties and stats['grape_varieties']:
        print(f"\n🍇 GRAPE VARIETIES:")
        sorted_varieties = sorted(stats['grape_varieties'])
        for i, variety in enumerate(sorted_varieties):
            if i % 3 == 0:
                print()
            print(f"   {variety:<30}", end="")
        print()
    
    print(f"\n🌐 DIGITAL PRESENCE:")
    print(f"   Websites found: {stats['websites_found']:,}")
    print(f"   Social accounts: {stats['social_accounts']:,}")
    
    if stats['producers_with_wines'] > 0:
        avg_wines = stats['total_wines'] / stats['producers_with_wines']
        print(f"\n📈 AVERAGES:")
        print(f"   Wines per producer: {avg_wines:.1f}")
    
    print(f"\n📊 TOP COUNTRIES:")
    for country, count in stats['countries'].most_common(5):
        print(f"   {country}: {count:,}")
    
    if stats['activities']:
        print(f"\n🎯 TOP ACTIVITIES:")
        for activity, count in stats['activities'].most_common(5):
            print(f"   {activity}: {count}")
    
    print(f"\n* Estimated bottles assume ~250 bottles per wine (rough approximation)")

def main():
    """Main function to generate and display statistics."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate wine producer dataset statistics")
    parser.add_argument("--varieties", action="store_true", help="Show list of all grape varieties")
    args = parser.parse_args()
    
    print("Loading wine producer dataset...")
    producers = load_producer_data()
    
    if not producers:
        return
    
    print(f"Analyzing {len(producers):,} producers...")
    stats = analyze_dataset(producers)
    
    # Print detailed statistics
    print_detailed_stats(stats, show_varieties=args.varieties)
    
    # Generate social media posts
    posts = generate_social_media_posts(stats)
    
    print("\n" + "=" * 50)
    print("📱 SOCIAL MEDIA POSTS")
    print("=" * 50)
    
    print(f"\n📝 ENGLISH:")
    print("-" * 30)
    print(posts['english'])
    
    print(f"\n📝 FRANÇAIS:")
    print("-" * 30) 
    print(posts['french'])
    
    # Save to file
    output_file = Path("dataset_statistics.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("WINE PRODUCER DATASET STATISTICS\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("DETAILED STATS:\n")
        f.write(f"Total producers: {stats['total_producers']:,}\n")
        f.write(f"Geographic regions: {stats['unique_states_provinces']}\n")
        f.write(f"Total wines: {stats['total_wines']:,}\n")
        f.write(f"Grape varieties: {stats['unique_grape_varieties']}\n")
        f.write(f"Websites: {stats['websites_found']}\n")
        f.write(f"Social accounts: {stats['social_accounts']}\n\n")
        
        f.write("SOCIAL MEDIA POSTS:\n")
        f.write("-" * 20 + "\n")
        f.write(f"\nENGLISH:\n{posts['english']}\n")
        f.write(f"\nFRANÇAIS:\n{posts['french']}\n")
    
    print(f"\n✅ Statistics saved to: {output_file}")

if __name__ == "__main__":
    main()