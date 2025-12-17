#!/usr/bin/env python3
"""
Update the varieties index page by scanning the varieties directory.
Generates docs/en/varieties/index.md and optionally docs/fr/varieties/index.md.
"""

import os
from pathlib import Path

def get_variety_display_name(filename):
    """Convert filename to display name (acadie_blanc.md -> Acadie Blanc)"""
    name = filename.replace('.md', '').replace('_', ' ')
    return name.title()

def scan_varieties_directory(language="en"):
    """Scan varieties directory and return sorted list of variety files"""
    varieties_dir = Path(f"docs/{language}/varieties")
    
    if not varieties_dir.exists():
        print(f"Error: {varieties_dir} not found")
        return []
    
    # Get all .md files except index.md
    variety_files = []
    for file in varieties_dir.glob("*.md"):
        if file.name != "index.md":
            variety_files.append(file.name)
    
    # Sort alphabetically
    variety_files.sort()
    return variety_files

def get_content_templates(language="en"):
    """Get intro and footer content for specified language"""
    if language == "fr":
        intro = """# Variétés de Raisin

Vous trouverez ici des articles détaillés sur les variétés de raisins hybrides qui prospèrent dans les climats froids. Chaque page de variété inclut :

- **Information de culture** : Adaptation climatique, résistance aux maladies et détails de cultivation
- **Histoires de vignerons** : Expériences réelles de vignerons et vinificateurs
- **Citations et ressources** : Liens pour découvrir plus sur chaque variété

## Variétés disponibles

"""
        footer = """
    
*De nouveaux articles sur les variétés de raisins sont ajoutés régulièrement. Revenez pour les mises à jour !*"""
    else:
        intro = """# Grape Varieties

Here you'll find detailed articles about hybrid grape varieties that thrive in cold climates. Each variety page includes:

- **Growing Information**: Climate adaptation, disease resistance, and cultivation details
- **Winemaker Stories**: Real experiences from growers and winemakers
- **Citations and Resources**: Links to discover more about each variety

## Available Varieties

"""
        footer = """
    
*New grape variety articles are added regularly. Check back for updates!*"""
    
    return intro, footer

def generate_varieties_index(language="en"):
    """Generate the varieties index page for specified language"""
    variety_files = scan_varieties_directory(language)
    
    if not variety_files:
        print(f"No variety files found for {language}")
        return
    
    # Get content templates
    intro, footer = get_content_templates(language)
    
    # Generate variety links
    variety_links = []
    for filename in variety_files:
        display_name = get_variety_display_name(filename)
        variety_links.append(f"- **[{display_name}]({filename})**")
    
    # Combine all parts
    content = intro + "\n".join(variety_links) + footer
    
    # Write to index file
    index_file = Path(f"docs/{language}/varieties/index.md")
    index_file.write_text(content)
    
    print(f"Generated {language} index with {len(variety_files)} varieties:")
    for filename in variety_files:
        display_name = get_variety_display_name(filename)
        print(f"  - {display_name}")

def update_varieties_indexes():
    """Update both English and French varieties indexes"""
    print("Updating varieties indexes...")
    generate_varieties_index("en")
    generate_varieties_index("fr")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "fr":
        generate_varieties_index("fr")
    elif len(sys.argv) > 1 and sys.argv[1] == "both":
        update_varieties_indexes()
    else:
        generate_varieties_index("en")