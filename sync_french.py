#!/usr/bin/env python3

import os
import hashlib
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class FrenchSyncer:
    """Sync English articles to French with hash-based change detection."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        if not dry_run:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.client = None
        
        self.base_path = Path.cwd()
        self.english_dir = self.base_path / "docs" / "varieties"
        self.french_dir = self.base_path / "docs" / "fr" / "varietes"
        
        # Main site directories
        self.docs_dir = self.base_path / "docs"
        self.french_docs_dir = self.base_path / "docs" / "fr"
        
        # Ensure French directories exist
        self.french_dir.mkdir(parents=True, exist_ok=True)
        self.french_docs_dir.mkdir(parents=True, exist_ok=True)
    
    def compute_content_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file content."""
        content = file_path.read_text(encoding='utf-8')
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def extract_frontmatter_and_content(self, file_path: Path) -> tuple[dict, str]:
        """Extract YAML frontmatter and main content from a markdown file."""
        if not file_path.exists():
            return {}, ""
        
        content = file_path.read_text(encoding='utf-8')
        
        if content.startswith("---"):
            try:
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    yaml_content = parts[1].strip()
                    main_content = parts[2].strip()
                    frontmatter = yaml.safe_load(yaml_content) if yaml_content else {}
                    return frontmatter, main_content
            except yaml.YAMLError:
                pass
        
        return {}, content.strip()
    
    def create_french_file(self, frontmatter: dict, french_content: str, file_path: Path):
        """Create French markdown file with frontmatter."""
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        
        full_content = f"---\n{frontmatter_yaml}---\n\n{french_content}"
        file_path.write_text(full_content, encoding='utf-8')
    
    def translate_to_french(self, english_content: str, variety_name: str) -> str:
        """Translate English content to French using OpenAI."""
        if self.dry_run:
            return f"[DRY RUN] French translation of {variety_name} would be generated here"
        
        prompt = f"""
Translate the following English grape variety article to French.

Important guidelines:
- Maintain all technical terms accuracy (grape variety names, disease names, climate zones)
- Keep citations and references exactly as they are
- Preserve the casual, approachable tone
- Use Quebec French where appropriate (this is for Quebec wine growers)
- Keep the markdown formatting intact
- Don't translate proper names of people, places, wineries, or publications
- This is about the grape variety: {variety_name}

English content:
---
{english_content}
---

Provide the French translation:
"""
        
        try:
            response = self.client.responses.create(
                model="gpt-5",
                tools=[{"type": "web_search"}],
                input=prompt
            )
            return response.output_text
        except Exception as e:
            return f"Error translating content: {str(e)}"
    
    def translate_site_content(self, english_content: str, filename: str) -> str:
        """Translate general site content to French using OpenAI."""
        if self.dry_run:
            return f"[DRY RUN] French translation of {filename} would be generated here"
        
        prompt = f"""
Translate the following English content to French for a Quebec wine growing website.

Important guidelines:
- Maintain the same markdown structure 
- Use Quebec French where appropriate 
- Keep a friendly, approachable tone
- Preserve any technical terms related to viticulture
- Keep all external URLs and social media links exactly as they are
- Translate section names (like "Grape Varieties" → "Cépages")
- For internal links, update paths for French site structure:
  - varieties/index.md → varietes/index.md
  - about.md → a-propos.md  
  - ai-usage.md → usage-ia.md
- Keep directory structure English (varieties/, not cépages/) but translate the display text

English content:
{english_content}
"""

        try:
            response = self.client.responses.create(
                model="gpt-5",
                tools=[{"type": "web_search"}],
                input=prompt
            )
            return response.output_text
        except Exception as e:
            return f"Error translating content: {str(e)}"
    
    def sync_file(self, english_file: Path) -> str:
        """Sync a single English file to French. Returns action taken."""
        variety_name = english_file.stem  # Remove .md extension
        french_file = self.french_dir / f"{variety_name}.md"
        
        # Skip index files
        if english_file.name == "index.md":
            return "SKIP - Index file"
        
        # Compute current English content hash
        english_hash = self.compute_content_hash(english_file)
        english_content = english_file.read_text(encoding='utf-8')
        
        # Check if French file exists and get its stored hash
        if french_file.exists():
            french_frontmatter, french_content = self.extract_frontmatter_and_content(french_file)
            stored_hash = french_frontmatter.get('english_hash')
            
            if stored_hash == english_hash:
                return "SKIP - Hash unchanged"
            else:
                # Content changed, need to retranslate
                french_translation = self.translate_to_french(english_content, variety_name)
                
                # Update frontmatter with new hash
                french_frontmatter['english_hash'] = english_hash
                french_frontmatter['translated_from'] = str(english_file.relative_to(self.base_path))
                
                if not self.dry_run:
                    self.create_french_file(french_frontmatter, french_translation, french_file)
                
                return "UPDATED - Content changed"
        else:
            # New file, translate it
            french_translation = self.translate_to_french(english_content, variety_name)
            
            # Create frontmatter
            frontmatter = {
                'english_hash': english_hash,
                'translated_from': str(english_file.relative_to(self.base_path)),
                'variety': variety_name.replace('_', ' ').title()
            }
            
            if not self.dry_run:
                self.create_french_file(frontmatter, french_translation, french_file)
            
            return "NEW - File created"
    
    def update_french_index(self):
        """Update French varieties index with all available French articles."""
        if self.dry_run:
            return "SKIP - Index update (dry run)"
        
        french_index = self.french_dir / "index.md"
        
        # Get all French variety files
        french_files = [f for f in self.french_dir.glob("*.md") if f.name != "index.md"]
        french_files.sort()
        
        # Build varieties list
        varieties_list = []
        for french_file in french_files:
            variety_stem = french_file.stem
            frontmatter, _ = self.extract_frontmatter_and_content(french_file)
            display_name = frontmatter.get('variety', variety_stem.replace('_', ' ').title())
            varieties_list.append(f"- **[{display_name}]({french_file.name})**")
        
        # Create index content
        index_content = """# Variétés de Raisin

Vous trouverez ici des articles détaillés sur les variétés de raisins hybrides qui prospèrent dans les climats froids. Chaque page de variété inclut :

- **Information de culture** : Adaptation climatique, résistance aux maladies et détails de cultivation
- **Histoires de vignerons** : Expériences réelles de vignerons et vinificateurs
- **Citations et ressources** : Liens pour découvrir plus sur chaque variété

## Variétés disponibles

"""
        
        if varieties_list:
            index_content += "\n".join(varieties_list) + "\n\n"
        
        index_content += "*De nouveaux articles sur les variétés de raisin sont ajoutés régulièrement. Revenez consulter pour les mises à jour !*"
        
        french_index.write_text(index_content, encoding='utf-8')
        return f"UPDATED - French index with {len(varieties_list)} varieties"
    
    def sync_main_site_file(self, english_file: Path, french_filename: str) -> str:
        """Sync a main site file to French."""
        french_file = self.french_docs_dir / french_filename
        
        # Compute current English content hash
        english_hash = self.compute_content_hash(english_file)
        
        # Check if French file exists and get stored hash
        if french_file.exists():
            french_frontmatter, _ = self.extract_frontmatter_and_content(french_file)
            stored_hash = french_frontmatter.get("english_hash")
            
            if stored_hash == english_hash:
                return "SKIP - No changes detected"
        
        # Read English content and translate
        english_content = english_file.read_text(encoding='utf-8')
        
        if self.dry_run:
            french_content = f"[DRY RUN] French translation of {english_file.name} would be generated here"
        else:
            # Use a simpler translation approach for site content
            french_content = self.translate_site_content(english_content, english_file.name)
        
        # Create French frontmatter
        french_frontmatter = {
            "english_hash": english_hash,
            "translated_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Save French file
        if not self.dry_run:
            self.create_french_file(french_frontmatter, french_content, french_file)
            
        action = "CREATE" if not french_file.exists() else "UPDATE"
        return f"{action} - Content translated"

    def sync_all(self):
        """Sync all English variety files and main site content to French."""
        print(f"🔄 Starting French sync {'(DRY RUN)' if self.dry_run else ''}")
        print(f"📂 Varieties source: {self.english_dir}")
        print(f"📂 Varieties target: {self.french_dir}")
        print(f"📂 Main site source: {self.docs_dir}")
        print(f"📂 Main site target: {self.french_docs_dir}")
        print("-" * 60)
        
        # Sync main site files
        main_site_files = [
            ("index.md", "index.md"),
            ("about.md", "a-propos.md"),
            ("ai-usage.md", "usage-ia.md")
        ]
        
        for english_name, french_name in main_site_files:
            english_file = self.docs_dir / english_name
            if english_file.exists():
                print(f"📄 {english_name} → {french_name}")
                action = self.sync_main_site_file(english_file, french_name)
                print(f"   {action}")
        
        print()
        
        # Find all English variety files
        english_files = list(self.english_dir.glob("*.md"))
        
        if not english_files:
            print("⚠️  No English variety files found")
            return
        
        # Process each variety file
        for english_file in english_files:
            action = self.sync_file(english_file)
            status_icon = {
                "SKIP - Index file": "⏭️ ",
                "SKIP - Hash unchanged": "⏭️ ",
                "UPDATED - Content changed": "🔄",
                "NEW - File created": "✨"
            }.get(action.split(" - ")[0], "❓")
            
            print(f"{status_icon} {english_file.name:<30} {action}")
        
        # Update French index
        print("-" * 60)
        index_action = self.update_french_index()
        print(f"📑 index.md                     {index_action}")
        
        print("-" * 60)
        print("✅ French sync complete!")

def main():
    parser = argparse.ArgumentParser(description="Sync English grape variety articles to French")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    syncer = FrenchSyncer(dry_run=args.dry_run)
    syncer.sync_all()

if __name__ == "__main__":
    main()