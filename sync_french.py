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
        self.english_dir = self.base_path / "docs" / "en" / "varieties"
        self.french_dir = self.base_path / "docs" / "fr" / "varieties"
        
        # Main site directories
        self.docs_dir = self.base_path / "docs" / "en"
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
- Keep all internal links identical to English (same filenames and paths)
- Translate section names and display text but keep URLs the same

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
    
    
    def update_french_index(self):
        """Update French varieties index using the centralized script."""
        if self.dry_run:
            return "SKIP - Index update (dry run)"
        
        # Import and use the centralized index generator
        from update_varieties_index import generate_varieties_index, scan_varieties_directory
        
        try:
            generate_varieties_index("fr")
            
            # Count varieties for reporting
            variety_count = len(scan_varieties_directory("fr"))
            return f"UPDATED - French index with {variety_count} varieties"
        except Exception as e:
            return f"ERROR - Failed to update French index: {e}"
    
    def sync_file_to_french(self, english_file: Path, french_file: Path, is_variety: bool = False) -> str:
        """Sync any English file to French with identical structure."""
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
            return f"[DRY RUN] French translation would be generated"
        
        # Translate content
        if is_variety:
            variety_name = english_file.stem
            french_content = self.translate_to_french(english_content, variety_name)
        else:
            french_content = self.translate_site_content(english_content, english_file.name)
        
        # Create French frontmatter
        if is_variety:
            french_frontmatter = {
                "english_hash": english_hash,
                "translated_from": f"docs/varieties/{english_file.name}",
                "variety": english_file.stem.replace('_', ' ').title()
            }
        else:
            french_frontmatter = {
                "english_hash": english_hash,
                "translated_date": datetime.now().strftime("%Y-%m-%d")
            }
        
        # Save French file
        self.create_french_file(french_frontmatter, french_content, french_file)
            
        action = "CREATE" if not french_file.exists() else "UPDATE"
        return f"{action} - Content translated"

    def sync_all(self):
        """Sync all English variety files and main site content to French."""
        print(f"🔄 Starting French sync {'(DRY RUN)' if self.dry_run else ''}")
        print(f"📂 English source: docs/en/")
        print(f"📂 French target: docs/fr/")
        print(f"📂 Varieties: en/varieties/ → fr/varieties/")
        print(f"📂 Main site: en/*.md → fr/*.md")
        print("-" * 60)
        
        # Sync all main site markdown files (identical structure)
        main_site_files = [f for f in self.docs_dir.glob("*.md") if f.name != "README.md"]
        
        for english_file in main_site_files:
            french_file = self.french_docs_dir / english_file.name
            print(f"📄 {english_file.name}")
            action = self.sync_file_to_french(english_file, french_file, is_variety=False)
            print(f"   {action}")
        
        print()
        
        # Sync all variety files (identical structure)
        variety_files = [f for f in self.english_dir.glob("*.md") if f.name != "index.md"]
        
        if not variety_files:
            print("⚠️  No English variety files found")
        else:
            for english_file in variety_files:
                french_file = self.french_dir / english_file.name
                print(f"🍇 {english_file.name}")
                action = self.sync_file_to_french(english_file, french_file, is_variety=True)
                print(f"   {action}")
        
        print()
        
        # Update French varieties index
        print("-" * 60)
        if not self.dry_run and variety_files:
            index_action = self.update_french_index()
            print(f"📑 index.md                     {index_action}")
        else:
            print(f"📑 index.md                     SKIP - Index update (dry run)")
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