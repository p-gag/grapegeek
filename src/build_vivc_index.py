#!/usr/bin/env python3
"""
VIVC Grape Varieties Index Builder

Creates bilingual markdown indices (English/French) from grape variety data,
organized by species and berry color with comprehensive links to VIVC,
interactive maps, and research articles.

PURPOSE: VIVC Index Generation - Create comprehensive grape variety reference

INPUTS:
- data/grape_variety_mapping.jsonl (via GrapeVarietiesModel - grape variety data)

OUTPUTS:
- docs/en/varieties/index.md (English VIVC index)
- docs/fr/varieties/index.md (French VIVC index) 

DEPENDENCIES:
- includes.grape_varieties.GrapeVarietiesModel for variety data access

USAGE:
# Generate VIVC indices
uv run src/build_vivc_index.py

# Custom output location
uv run src/build_vivc_index.py --output docs/en/varieties/custom-index.md

FUNCTIONALITY:
- Loads grape variety data from GrapeVarietiesModel
- Organizes varieties by species (Vinifera vs Non-vinifera) and berry color
- Creates dynamic VIVC links with variety-specific labels
- Generates producer map links with variety filtering
- Includes research article links when available
- Produces bilingual indices with localized content
- Provides comprehensive statistics and VIVC match rates
"""

import argparse
import sys
import urllib.parse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

# Import the grape varieties model
sys.path.insert(0, str(Path(__file__).parent))
from includes.grape_varieties import GrapeVarietiesModel


def load_varieties_from_model(data_dir: str = "data") -> List[Dict]:
    """Load varieties using the grape varieties model."""
    try:
        model = GrapeVarietiesModel(data_dir)
        varieties = []
        
        for variety in model.get_all_varieties():
            # Convert GrapeVariety dataclass to dict format compatible with existing code
            variety_dict = variety.to_dict()
            varieties.append(variety_dict)
        
        print(f"✅ Loaded {len(varieties)} varieties from model")
        return varieties
        
    except Exception as e:
        print(f"❌ Error loading varieties from model: {e}")
        return []


def find_research_file(variety_name: str) -> str:
    """Find research file for a variety and return relative path if found."""
    # Convert variety name to research file format (spaces to underscores, lowercase)
    research_filename = variety_name.lower().replace(' ', '_').replace('-', '_') + '.md'
    research_path = Path("docs/en/varieties/research") / research_filename
    
    if research_path.exists():
        return f"research/{research_filename}"
    return None


def create_variety_links(variety_name: str, vivc_number: str, vivc_name: str = None) -> str:
    """Create all links for a variety: VIVC, map, and research."""
    links = []
    
    # VIVC link with dynamic label
    if vivc_name and variety_name.upper() != vivc_name.upper():
        # Use "vivc (lowercase_vivc_name)" format when different
        vivc_label = f"vivc ({vivc_name.lower()})"
        vivc_link = f"[{vivc_label}](https://www.vivc.de/index.php?r=passport%2Fview&id={vivc_number})"
    else:
        # Use default "vivc" label when names are the same or no VIVC name
        vivc_link = f"[vivc](https://www.vivc.de/index.php?r=passport%2Fview&id={vivc_number})"
    
    links.append(vivc_link)
    
    # Map link
    encoded_name = urllib.parse.quote_plus(variety_name)
    map_link = f"[map](/producer-map/?grape_variety={encoded_name})"
    links.append(map_link)
    
    # Research link (if file exists)
    research_path = find_research_file(variety_name)
    if research_path:
        research_link = f"[research]({research_path})"
        links.append(research_link)
    
    return " | ".join(links)


def create_missing_variety_links(variety_name: str) -> str:
    """Create map and research links for varieties without VIVC data."""
    links = []
    
    # Map link
    encoded_name = urllib.parse.quote_plus(variety_name)
    map_link = f"[map](/producer-map/?grape_variety={encoded_name})"
    links.append(map_link)
    
    # Research link (if file exists)
    research_path = find_research_file(variety_name)
    if research_path:
        research_link = f"[research]({research_path})"
        links.append(research_link)
    
    return " | ".join(links) if links else ""


def organize_varieties_by_category(varieties: List[Dict]) -> Dict:
    """Organize varieties into three main categories: Non-vinifera, Vinifera, Missing Information."""
    organized = {
        'Non-vinifera': defaultdict(list),
        'Vinifera': defaultdict(list),
        'Missing Information': []
    }
    
    for variety in varieties:
        status = variety.get('vivc_assignment_status')
        
        if status == 'not_found' or not variety.get('vivc'):
            # Add to not found list
            organized['Missing Information'].append({
                'name': variety.get('name', 'Unknown'),
                'aliases': variety.get('aliases', [])
            })
            continue
        
        # Skip non-grape varieties
        if not variety.get('grape', True):
            continue
            
        vivc_data = variety.get('vivc', {})
        if not vivc_data:
            continue
            
        # Extract species and berry color
        species = vivc_data.get('species', 'Unknown Species')
        if not species or species.strip() == '':
            # If species is missing, add to Missing Information
            organized['Missing Information'].append({
                'name': variety.get('name', 'Unknown'),
                'aliases': variety.get('aliases', [])
            })
            continue
        
        berry_color = vivc_data.get('berry_skin_color', 'Unknown Color')
        if not berry_color or berry_color.strip() == '':
            berry_color = 'Unknown Color'
        
        grape_info = vivc_data.get('grape', {})
        vivc_name = grape_info.get('name', variety.get('name', 'Unknown'))
        vivc_number = grape_info.get('vivc_number', '')
        country = vivc_data.get('country_of_origin', 'Unknown Country')
        
        # Replace "UNITED STATES OF AMERICA" with "USA"
        if country == 'UNITED STATES OF AMERICA':
            country = 'USA'
        
        variety_data = {
            'original_name': variety.get('name', 'Unknown'),
            'vivc_name': vivc_name,
            'vivc_number': vivc_number,
            'country': country,
            'aliases': variety.get('aliases', []),
            'species': species
        }
        
        # Categorize by species
        if 'VITIS VINIFERA' in species.upper():
            organized['Vinifera'][berry_color].append(variety_data)
        else:
            organized['Non-vinifera'][berry_color].append(variety_data)
    
    return organized


def generate_markdown_index(organized: Dict, language: str = "en") -> str:
    """Generate markdown index from organized data."""
    lines = []
    
    # Localized text based on language
    if language == "fr":
        title = "# Index VIVC des Cépages"
        subtitle = "*Index des cépages organisé par catégories principales avec liens VIVC.*"
        non_vinifera_title = "## Non-vinifera"
        non_vinifera_desc = "*Cépages d'espèces non-vinifera (hybrides, indigènes américains, etc.)*"
        vinifera_title = "## Vinifera"
        vinifera_desc = "*Cépages européens classiques (Vitis vinifera)*"
        missing_title = "## Informations manquantes"
        missing_desc = "*Cépages sans données VIVC ou données incomplètes.*"
        footer_generated = "Index généré avec"
        footer_vinifera = "cépages Vinifera"
        footer_non_vinifera = "cépages Non-vinifera"
        footer_missing = "cépages avec informations manquantes"
    else:
        title = "# Grape Varieties VIVC Index"
        subtitle = "*Index of grape varieties organized by major categories with VIVC links.*"
        non_vinifera_title = "## Non-vinifera"
        non_vinifera_desc = "*Grape varieties from non-vinifera species (hybrids, American natives, etc.)*"
        vinifera_title = "## Vinifera"
        vinifera_desc = "*Classic European wine grape varieties (Vitis vinifera)*"
        missing_title = "## Missing Information"
        missing_desc = "*Varieties with no or incomplete VIVC passport data.*"
        footer_generated = "Generated index with"
        footer_vinifera = "Vinifera varieties"
        footer_non_vinifera = "Non-vinifera varieties"
        footer_missing = "varieties with missing information"
    
    # Title
    lines.append(title)
    lines.append("")
    lines.append(subtitle)
    lines.append("")
    
    
    # Non-vinifera section
    lines.append(non_vinifera_title)
    lines.append("")
    lines.append(non_vinifera_desc)
    lines.append("")
    
    sorted_colors = sorted(organized['Non-vinifera'].keys())
    for color in sorted_colors:
        lines.append(f"### {color}")
        lines.append("")
        
        # Sort varieties within color by original name
        varieties = sorted(organized['Non-vinifera'][color], key=lambda x: x['original_name'])
        
        for variety in varieties:
            # Create all links (VIVC, map, research)
            links = create_variety_links(variety['original_name'], variety['vivc_number'], variety['vivc_name'])
            
            # Format entry with original name as primary
            entry = f"- **{variety['original_name']}** ({variety['country']}) {links}"
            
            lines.append(entry)
        
        lines.append("")
    
    # Vinifera section
    lines.append(vinifera_title)
    lines.append("")
    lines.append(vinifera_desc)
    lines.append("")
    
    sorted_colors = sorted(organized['Vinifera'].keys())
    for color in sorted_colors:
        lines.append(f"### {color}")
        lines.append("")
        
        # Sort varieties within color by original name
        varieties = sorted(organized['Vinifera'][color], key=lambda x: x['original_name'])
        
        for variety in varieties:
            # Create all links (VIVC, map, research)
            links = create_variety_links(variety['original_name'], variety['vivc_number'], variety['vivc_name'])
            
            # Format entry with original name as primary
            entry = f"- **{variety['original_name']}** ({variety['country']}) {links}"
            
            lines.append(entry)
        
        lines.append("")
    
    # Missing Information section
    if organized['Missing Information']:
        lines.append(missing_title)
        lines.append("")
        lines.append(missing_desc)
        lines.append("")
        
        # Sort by name
        sorted_missing = sorted(organized['Missing Information'], key=lambda x: x['name'])
        
        for variety in sorted_missing:
            # Create map and research links
            links = create_missing_variety_links(variety['name'])
            links_str = f" {links}" if links else ""
            
            aliases_str = ""
            if variety['aliases']:
                # Show first few aliases with localized label
                aliases_label = "Aliases" if language == "en" else "Synonymes"
                shown_aliases = variety['aliases'][:5]
                if len(variety['aliases']) > 5:
                    more_text = "more" if language == "en" else "de plus"
                    aliases_str = f" - *{aliases_label}: {', '.join(shown_aliases)}... (+{len(variety['aliases'])-5} {more_text})*"
                else:
                    aliases_str = f" - *{aliases_label}: {', '.join(shown_aliases)}*"
            
            lines.append(f"- **{variety['name']}**{links_str}{aliases_str}")
        
        lines.append("")
    
    # Footer with statistics
    vinifera_count = sum(len(varieties) for varieties in organized['Vinifera'].values())
    non_vinifera_count = sum(len(varieties) for varieties in organized['Non-vinifera'].values())
    missing_count = len(organized['Missing Information'])
    total_count = vinifera_count + non_vinifera_count + missing_count
    
    lines.append("---")
    lines.append("")
    lines.append(f"*{footer_generated} {total_count} {'cépages' if language == 'fr' else 'varieties'}:*")
    lines.append(f"*- {vinifera_count} {footer_vinifera}*")
    lines.append(f"*- {non_vinifera_count} {footer_non_vinifera}*")
    lines.append(f"*- {missing_count} {footer_missing}*")
    
    return "\n".join(lines)


def get_stats(organized: Dict) -> Dict:
    """Get statistics about the organized data."""
    vinifera_count = sum(len(varieties) for varieties in organized['Vinifera'].values())
    non_vinifera_count = sum(len(varieties) for varieties in organized['Non-vinifera'].values())
    missing_count = len(organized['Missing Information'])
    total_count = vinifera_count + non_vinifera_count + missing_count
    
    # Count colors
    all_colors = set()
    all_colors.update(organized['Vinifera'].keys())
    all_colors.update(organized['Non-vinifera'].keys())
    
    return {
        'vinifera_count': vinifera_count,
        'non_vinifera_count': non_vinifera_count,
        'missing_count': missing_count,
        'total_count': total_count,
        'unique_colors': len(all_colors)
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build VIVC markdown index from grape varieties data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/build_vivc_index.py
  python src/build_vivc_index.py --output docs/en/varieties/custom-index.md
  python src/build_vivc_index.py --data-dir data
        """
    )
    
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Data directory containing grape_variety_mapping.jsonl (default: data)"
    )
    
    parser.add_argument(
        "--output",
        default="docs/en/varieties/index.md",
        help="Output markdown file (default: docs/en/varieties/index.md)"
    )
    
    args = parser.parse_args()
    
    output_file = Path(args.output)
    
    print(f"📊 Building VIVC index from {args.data_dir}/grape_variety_mapping.jsonl")
    
    # Load data using model
    varieties = load_varieties_from_model(args.data_dir)
    if not varieties:
        sys.exit(1)
    
    # Organize data
    print("🗂️  Organizing varieties into categories...")
    organized = organize_varieties_by_category(varieties)
    
    # Generate English markdown
    print("📝 Generating English markdown index...")
    english_content = generate_markdown_index(organized, "en")
    
    # Generate French markdown
    print("📝 Generating French markdown index...")
    french_content = generate_markdown_index(organized, "fr")
    
    # Save English output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(english_content)
    
    # Save French output
    french_output_file = Path(str(output_file).replace("/en/", "/fr/"))
    french_output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(french_output_file, 'w', encoding='utf-8') as f:
        f.write(french_content)
    
    # Show statistics
    stats = get_stats(organized)
    print(f"\n📊 Index Statistics:")
    print(f"  Total varieties: {stats['total_count']}")
    print(f"  Vinifera varieties: {stats['vinifera_count']}")
    print(f"  Non-vinifera varieties: {stats['non_vinifera_count']}")
    print(f"  Missing information: {stats['missing_count']}")
    print(f"  Unique colors: {stats['unique_colors']}")
    
    found_count = stats['vinifera_count'] + stats['non_vinifera_count']
    success_rate = (found_count / stats['total_count']) * 100 if stats['total_count'] > 0 else 0
    print(f"  VIVC match rate: {success_rate:.1f}%")
    
    print(f"\n✅ Indices saved to:")
    print(f"   English: {output_file}")
    print(f"   French:  {french_output_file}")


if __name__ == "__main__":
    main()