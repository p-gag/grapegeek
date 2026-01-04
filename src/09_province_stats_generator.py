#!/usr/bin/env python3
"""
Per-Province Wine Statistics Generator

Generates detailed wine statistics for each province/state with comprehensive 
analysis of producers, varieties, and wine types. Creates bilingual markdown
pages for regional wine insights and variety analysis.

PURPOSE: Regional Statistics - Generate comprehensive per-province wine analytics

INPUTS:
- data/05_wine_producers_final_normalized.jsonl (final production dataset)
- data/grape_variety_mapping.jsonl (via GrapeVarietiesModel - for vinifera analysis)

OUTPUTS:
- docs/en/regions/{province_slug}.md (English province statistics pages)
- docs/fr/regions/{province_slug}.md (French province statistics pages)

DEPENDENCIES:
- includes.grape_varieties.GrapeVarietiesModel for vinifera classification

USAGE:
# Generate statistics for all provinces
uv run src/09_province_stats_generator.py

# Generate for specific provinces only
uv run src/09_province_stats_generator.py --provinces "Quebec,Ontario,New York"

# Generate with minimum producer threshold
uv run src/09_province_stats_generator.py --min-producers 5

FUNCTIONALITY:
- Analyzes wine production data by province/state
- Calculates producer counts, wines, and varieties per producer
- Classifies grape varieties as vinifera vs non-vinifera using VIVC data
- Generates grape variety popularity rankings by wine appearance
- Creates wine type distribution analysis with percentages
- Produces bilingual markdown pages with comprehensive regional insights
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import re
import argparse

# Import the grape varieties model
sys.path.insert(0, str(Path(__file__).parent))
from includes.grape_varieties import GrapeVarietiesModel


class ProvinceStatsGenerator:
    """Generates detailed wine statistics for each province/region."""
    
    def __init__(self, min_producers: int = 1):
        self.min_producers = min_producers
        self.grape_model = GrapeVarietiesModel()
        
    def load_producer_data(self) -> List[Dict]:
        """Load the final wine producer dataset."""
        input_file = Path("data/05_wine_producers_final_normalized.jsonl")
        
        if not input_file.exists():
            print(f"❌ Input file not found: {input_file}")
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
    
    def is_vinifera(self, variety_name: str) -> bool:
        """Check if a grape variety is vinifera using VIVC data."""
        variety = self.grape_model.get_variety(variety_name)
        if not variety or not variety.vivc:
            return None  # Unknown
        
        vivc_data = variety.vivc
        species = vivc_data.get('species', '').upper()
        return 'VITIS VINIFERA' in species
    
    def analyze_province_data(self, producers: List[Dict], target_provinces: Set[str] = None) -> Dict[str, Dict]:
        """Analyze wine data by province."""
        province_stats = defaultdict(lambda: {
            'producer_count': 0,
            'total_wines': 0,
            'producers_with_wines': 0,
            'grape_varieties': Counter(),
            'wine_types': Counter(),
            'vinifera_varieties': Counter(),
            'non_vinifera_varieties': Counter(),
            'unknown_varieties': Counter(),
            'variety_wine_appearances': Counter(),
            'producers': []
        })
        
        for producer in producers:
            state_province = producer.get('state_province', '').strip()
            if not state_province:
                continue
            
            # Filter by target provinces if specified
            if target_provinces and state_province not in target_provinces:
                continue
            
            stats = province_stats[state_province]
            stats['producer_count'] += 1
            stats['producers'].append(producer.get('business_name', 'Unknown'))
            
            # Wine analysis
            wines = producer.get('wines', []) or []
            if wines:
                stats['producers_with_wines'] += 1
                stats['total_wines'] += len(wines)
                
                for wine in wines:
                    if isinstance(wine, dict):
                        # Wine types
                        wine_type = wine.get('type')
                        if wine_type and isinstance(wine_type, str):
                            stats['wine_types'][wine_type.strip()] += 1
                        
                        # Grape varieties analysis
                        cepages = wine.get('cepages', []) or []
                        wine_has_varieties = False
                        
                        for cepage in cepages:
                            if isinstance(cepage, str) and cepage.strip():
                                variety = cepage.strip()
                                stats['grape_varieties'][variety] += 1
                                stats['variety_wine_appearances'][variety] += 1
                                wine_has_varieties = True
                                
                                # Classify as vinifera/non-vinifera
                                is_vinifera = self.is_vinifera(variety)
                                if is_vinifera is True:
                                    stats['vinifera_varieties'][variety] += 1
                                elif is_vinifera is False:
                                    stats['non_vinifera_varieties'][variety] += 1
                                else:
                                    stats['unknown_varieties'][variety] += 1
                        
        
        # Filter provinces by minimum producer count
        filtered_stats = {
            province: stats for province, stats in province_stats.items() 
            if stats['producer_count'] >= self.min_producers
        }
        
        return dict(filtered_stats)
    
    def create_province_slug(self, province_name: str) -> str:
        """Create URL-friendly slug from province name."""
        # Replace spaces, special characters with dashes, convert to lowercase
        slug = re.sub(r'[^\w\s-]', '', province_name.lower())
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug.strip('-')
    
    def generate_markdown_content(self, province: str, stats: Dict, language: str = "en") -> str:
        """Generate markdown content for a province."""
        slug = self.create_province_slug(province)
        
        # Language-specific text
        if language == "fr":
            texts = {
                'title': f"Statistiques vinicoles - {province}",
                'overview': "Vue d'ensemble",
                'producers': "Vignobles",
                'wines_varieties': "Vins et Cépages", 
                'wine_types': "Types de vins",
                'variety_classification': "Classification des cépages",
                'popular_varieties': "Cépages populaires",
                'total_producers': "Total des vignobles",
                'producers_with_wines': "Vignobles avec vins catalogués", 
                'total_wines': "Total des vins",
                'unique_varieties': "Cépages uniques",
                'unique_wine_types': "Types de vins uniques",
                'avg_wines_producer': "Vins par vignoble (moyenne)",
                'avg_varieties_producer': "Cépages par vignoble (moyenne)",
                'vinifera_percent': "Vinifera (%)",
                'non_vinifera_percent': "Non-vinifera (%)",
                'unknown_percent': "Classification inconnue (%)",
                'variety': "Cépage",
                'wine_appearances': "Apparitions dans les vins",
                'percentage': "Pourcentage",
                'wine_type': "Type de vin",
                'count': "Nombre",
            }
        else:
            texts = {
                'title': f"Wine Statistics - {province}",
                'overview': "Overview",
                'producers': "Producers", 
                'wines_varieties': "Wines & Varieties",
                'wine_types': "Wine Types",
                'variety_classification': "Grape Variety Classification",
                'popular_varieties': "Popular Grape Varieties",
                'total_producers': "Total Producers",
                'producers_with_wines': "Producers with catalogued wines",
                'total_wines': "Total Wines",
                'unique_varieties': "Unique Grape Varieties",
                'unique_wine_types': "Unique Wine Types", 
                'avg_wines_producer': "Wines per Producer (avg)",
                'avg_varieties_producer': "Varieties per Producer (avg)",
                'vinifera_percent': "Vinifera (%)",
                'non_vinifera_percent': "Non-vinifera (%)", 
                'unknown_percent': "Unknown classification (%)",
                'variety': "Grape Variety",
                'wine_appearances': "Wine Appearances",
                'percentage': "Percentage",
                'wine_type': "Wine Type",
                'count': "Count",
            }
        
        # Calculate averages and percentages
        avg_wines = stats['total_wines'] / stats['producers_with_wines'] if stats['producers_with_wines'] > 0 else 0
        
        total_variety_mentions = sum(stats['grape_varieties'].values())
        avg_varieties = total_variety_mentions / stats['producers_with_wines'] if stats['producers_with_wines'] > 0 else 0
        
        # Vinifera classification percentages
        total_variety_classifications = sum(stats['vinifera_varieties'].values()) + sum(stats['non_vinifera_varieties'].values()) + sum(stats['unknown_varieties'].values())
        vinifera_percent = (sum(stats['vinifera_varieties'].values()) / total_variety_classifications * 100) if total_variety_classifications > 0 else 0
        non_vinifera_percent = (sum(stats['non_vinifera_varieties'].values()) / total_variety_classifications * 100) if total_variety_classifications > 0 else 0
        unknown_percent = (sum(stats['unknown_varieties'].values()) / total_variety_classifications * 100) if total_variety_classifications > 0 else 0
        
        # Generate map link
        import urllib.parse
        encoded_province = urllib.parse.quote_plus(province)
        map_link = f"[🗺️ View producers on interactive map](/producer-map/?state={encoded_province})"
        
        # Generate markdown
        lines = [
            f"# {texts['title']}",
            "",
            map_link,
            "",
            f"## {texts['overview']}",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| {texts['total_producers']} | {stats['producer_count']:,} |",
            f"| {texts['producers_with_wines']} | {stats['producers_with_wines']:,} |",
            f"| {texts['total_wines']} | {stats['total_wines']:,} |",
            f"| {texts['unique_varieties']} | {len(stats['grape_varieties'])} |",
            f"| {texts['unique_wine_types']} | {len(stats['wine_types'])} |",
            f"| {texts['avg_wines_producer']} | {avg_wines:.1f} |",
            f"| {texts['avg_varieties_producer']} | {avg_varieties:.1f} |",
            "",
        ]
        
        # Variety classification section
        if total_variety_classifications > 0:
            lines.extend([
                f"## {texts['variety_classification']}",
                "",
                f"| Classification | Percentage |",
                f"|---------------|------------|",
                f"| {texts['vinifera_percent']} | {vinifera_percent:.1f}% |",
                f"| {texts['non_vinifera_percent']} | {non_vinifera_percent:.1f}% |",
                f"| {texts['unknown_percent']} | {unknown_percent:.1f}% |",
                "",
            ])
        
        # Popular varieties section
        if stats['variety_wine_appearances']:
            lines.extend([
                f"## {texts['popular_varieties']}",
                "",
                f"| {texts['variety']} | {texts['wine_appearances']} | {texts['percentage']} |",
                f"|-------------|----------|------------|",
            ])
            
            total_wine_appearances = sum(stats['variety_wine_appearances'].values())
            for variety, appearances in stats['variety_wine_appearances'].most_common():
                percentage = (appearances / total_wine_appearances * 100) if total_wine_appearances > 0 else 0
                lines.append(f"| {variety} | {appearances} | {percentage:.1f}% |")
            
            lines.append("")
        
        # Wine types section
        if stats['wine_types']:
            lines.extend([
                f"## {texts['wine_types']}",
                "",
                f"| {texts['wine_type']} | {texts['count']} | {texts['percentage']} |",
                f"|-----------|-------|------------|",
            ])
            
            total_wines_with_types = sum(stats['wine_types'].values())
            for wine_type, count in stats['wine_types'].most_common():
                percentage = (count / total_wines_with_types * 100) if total_wines_with_types > 0 else 0
                lines.append(f"| {wine_type} | {count} | {percentage:.1f}% |")
            
            lines.append("")
        
        
        return "\n".join(lines)
    
    def generate_all_province_pages(self, province_stats: Dict[str, Dict]):
        """Generate markdown pages for all provinces in both languages."""
        print(f"📝 Generating province statistics pages...")
        
        # Ensure output directories exist
        en_dir = Path("docs/en/regions")
        fr_dir = Path("docs/fr/regions") 
        en_dir.mkdir(parents=True, exist_ok=True)
        fr_dir.mkdir(parents=True, exist_ok=True)
        
        generated_pages = []
        
        for province, stats in province_stats.items():
            slug = self.create_province_slug(province)
            
            # Generate English page
            en_content = self.generate_markdown_content(province, stats, "en")
            en_file = en_dir / f"{slug}.md"
            
            with open(en_file, 'w', encoding='utf-8') as f:
                f.write(en_content)
            
            # Generate French page  
            fr_content = self.generate_markdown_content(province, stats, "fr")
            fr_file = fr_dir / f"{slug}.md"
            
            with open(fr_file, 'w', encoding='utf-8') as f:
                f.write(fr_content)
            
            generated_pages.append((province, slug, stats['producer_count'], stats['total_wines']))
            print(f"   ✅ {province}: {stats['producer_count']} producers, {stats['total_wines']} wines")
        
        return generated_pages

    def generate_regions_index(self, province_stats: Dict[str, Dict]):
        """Generate index pages for all regions in both languages."""
        print(f"📝 Generating regions index pages...")
        
        # Ensure output directories exist
        en_dir = Path("docs/en/regions")
        fr_dir = Path("docs/fr/regions") 
        en_dir.mkdir(parents=True, exist_ok=True)
        fr_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate English index
        en_content = self.generate_index_markdown(province_stats, "en")
        en_file = en_dir / "index.md"
        
        with open(en_file, 'w', encoding='utf-8') as f:
            f.write(en_content)
        
        # Generate French index  
        fr_content = self.generate_index_markdown(province_stats, "fr")
        fr_file = fr_dir / "index.md"
        
        with open(fr_file, 'w', encoding='utf-8') as f:
            f.write(fr_content)
        
        print(f"   ✅ Index pages generated: English + French")
        
    def generate_index_markdown(self, province_stats: Dict[str, Dict], language: str = "en") -> str:
        """Generate markdown index content for regions."""
        
        # Language-specific text
        if language == "fr":
            texts = {
                'title': "Index des régions vinicoles",
                'subtitle': "*Statistiques détaillées par province et état pour les vignobles*",
                'region': "Région",
                'producers': "Vignobles", 
                'wines': "Vins",
                'non_vinifera': "Non-vinifera",
                'map_link': "Carte",
                'details': "Détails"
            }
        else:
            texts = {
                'title': "Wine Regions Index",
                'subtitle': "*Detailed statistics by province and state for wine producers*",
                'region': "Region",
                'producers': "Producers",
                'wines': "Wines", 
                'non_vinifera': "Non-vinifera",
                'map_link': "Map",
                'details': "Details"
            }
        
        lines = [
            f"# {texts['title']}",
            "",
            texts['subtitle'],
            "",
            f"| {texts['region']} | {texts['producers']} | {texts['wines']} | {texts['non_vinifera']} | {texts['map_link']} | {texts['details']} |",
            f"|----------|-----------|-------|-------------|-----|---------|"
        ]
        
        # Sort provinces by producer count (descending)
        sorted_provinces = sorted(province_stats.items(), key=lambda x: x[1]['producer_count'], reverse=True)
        
        for province, stats in sorted_provinces:
            slug = self.create_province_slug(province)
            
            # Calculate non-vinifera percentage
            total_variety_classifications = (sum(stats['vinifera_varieties'].values()) + 
                                           sum(stats['non_vinifera_varieties'].values()) + 
                                           sum(stats['unknown_varieties'].values()))
            non_vinifera_percent = (sum(stats['non_vinifera_varieties'].values()) / total_variety_classifications * 100) if total_variety_classifications > 0 else 0
            
            # Create links
            import urllib.parse
            encoded_province = urllib.parse.quote_plus(province)
            map_link = f"[🗺️](/producer-map/?state={encoded_province})"
            details_link = f"[📊]({slug})"
            
            lines.append(
                f"| **{province}** | {stats['producer_count']:,} | {stats['total_wines']:,} | {non_vinifera_percent:.1f}% | {map_link} | {details_link} |"
            )
        
        # Add totals
        total_producers = sum(stats['producer_count'] for stats in province_stats.values())
        total_wines = sum(stats['total_wines'] for stats in province_stats.values())
        
        lines.extend([
            "",
            f"**Total: {len(province_stats)} regions, {total_producers:,} producers, {total_wines:,} wines**"
        ])
        
        return "\n".join(lines)


def main():
    """Main function to generate per-province statistics."""
    parser = argparse.ArgumentParser(description="Generate per-province wine statistics")
    parser.add_argument("--provinces", help="Comma-separated list of specific provinces to generate (optional)")
    parser.add_argument("--min-producers", type=int, default=1, help="Minimum number of producers required for a province page")
    
    args = parser.parse_args()
    
    print("🍷 Per-Province Wine Statistics Generator")
    print("=" * 50)
    
    # Parse target provinces
    target_provinces = None
    if args.provinces:
        target_provinces = set(p.strip() for p in args.provinces.split(','))
        print(f"🎯 Targeting specific provinces: {', '.join(target_provinces)}")
    
    # Initialize generator
    generator = ProvinceStatsGenerator(min_producers=args.min_producers)
    
    # Load data
    print("📥 Loading wine producer dataset...")
    producers = generator.load_producer_data()
    
    if not producers:
        print("❌ No producer data found")
        return
    
    print(f"   Loaded {len(producers):,} producers")
    
    # Analyze by province
    print("📊 Analyzing data by province...")
    province_stats = generator.analyze_province_data(producers, target_provinces)
    
    if not province_stats:
        print("❌ No provinces meet the minimum producer threshold")
        return
    
    print(f"   Found {len(province_stats)} provinces with ≥{args.min_producers} producers")
    
    # Generate pages
    generated_pages = generator.generate_all_province_pages(province_stats)
    
    # Generate index pages
    generator.generate_regions_index(province_stats)
    
    # Summary
    total_producers = sum(stats['producer_count'] for stats in province_stats.values())
    total_wines = sum(stats['total_wines'] for stats in province_stats.values())
    
    print(f"\n📈 Generation Complete!")
    print(f"   Provinces processed: {len(province_stats)}")
    print(f"   Total producers: {total_producers:,}")
    print(f"   Total wines: {total_wines:,}")
    print(f"   Pages generated: {len(generated_pages) * 2} (English + French)")
    
    print(f"\n📁 Generated pages:")
    for province, slug, producer_count, wine_count in sorted(generated_pages, key=lambda x: x[2], reverse=True):
        print(f"   • {province} ({slug}) - {producer_count} producers, {wine_count} wines")


if __name__ == "__main__":
    main()