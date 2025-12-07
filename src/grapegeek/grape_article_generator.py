from pathlib import Path
from typing import Dict, Any
from .base import BaseGenerator


class GrapeArticleGenerator(BaseGenerator):
    """Generate magazine-style articles about grape varieties."""
    
    def __init__(self, base_path: str = None, dry_run: bool = False):
        super().__init__(base_path, dry_run)
    
    def load_variety_context(self, variety_name: str) -> Dict[str, Any]:
        """Load variety-specific context from YAML frontmatter."""
        variety_file = self.prompts_path / "grapes" / "articles" / f"{variety_name.lower()}.md"
        default_data = {"name": variety_name, "prompt": ""}
        return self.load_yaml_frontmatter(variety_file, default_data)
    
    def generate_technical_article(self, variety_name: str) -> str:
        """Generate a technical article for a grape variety."""
        system_prompt = self.load_prompt_file("general/system_prompt.md")
        content_prompt = self.load_prompt_file("grapes/technical_prompt.md")
        variety_context = self.load_variety_context(variety_name)
        
        user_prompt = content_prompt
        user_prompt += f"\n\nVariety: {variety_context['name']}"
        
        if variety_context.get('prompt'):
            user_prompt += f"\nSpecific context: {variety_context['prompt']}"
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Prepare debug context
        context_info = {
            "use_case": "Technical Grape Article Generation",
            "variety_name": variety_name,
            "variety_context": variety_context,
            "prompts_loaded": {
                "system_prompt": "✓ Loaded" if system_prompt else "✗ Missing",
                "technical_prompt": "✓ Loaded" if content_prompt else "✗ Missing",
                "variety_context_file": f"grapes/articles/{variety_name.lower()}.md"
            }
        }
        
        return self.call_openai(full_prompt, context_info)
    
    def generate_story_article(self, variety_name: str) -> str:
        """Generate a winemaking story article for a grape variety."""
        system_prompt = self.load_prompt_file("general/system_prompt.md")
        content_prompt = self.load_prompt_file("grapes/art_prompt.md")
        variety_context = self.load_variety_context(variety_name)
        
        user_prompt = content_prompt
        user_prompt += f"\n\nVariety: {variety_context['name']}"
        
        if variety_context.get('prompt'):
            user_prompt += f"\nSpecific context: {variety_context['prompt']}"
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Prepare debug context
        context_info = {
            "use_case": "Winemaking Story Article Generation",
            "variety_name": variety_name,
            "variety_context": variety_context,
            "prompts_loaded": {
                "system_prompt": "✓ Loaded" if system_prompt else "✗ Missing",
                "story_prompt": "✓ Loaded" if content_prompt else "✗ Missing",
                "variety_context_file": f"grapes/articles/{variety_name.lower()}.md"
            }
        }
        
        return self.call_openai(full_prompt, context_info)
    
    def save_article(self, variety_name: str, content: str, article_type: str = "technical") -> Path:
        """Save the generated article to the appropriate directory."""
        if self.dry_run:
            # Save to debug directory during dry runs
            if article_type == "story":
                output_file = self.debug_path / f"{variety_name.lower()}_story_debug.md"
            else:
                output_file = self.debug_path / f"{variety_name.lower()}_technical_debug.md"
        else:
            # Save to normal output directory
            (self.output_path / "articles").mkdir(parents=True, exist_ok=True)
            if article_type == "story":
                output_file = self.output_path / "articles" / f"{variety_name.lower()}_winemaking_stories.md"
            else:
                output_file = self.output_path / "articles" / f"{variety_name.lower()}.md"
        
        return self.save_content(output_file, content)
    
    def publish_to_site(self, variety_name: str, content: str) -> Path:
        """Publish technical article to MkDocs site and update index."""
        # Create docs/varieties directory if it doesn't exist
        site_varieties_dir = self.base_path / "docs" / "varieties"
        site_varieties_dir.mkdir(parents=True, exist_ok=True)
        
        # Save article to site
        site_file = site_varieties_dir / f"{variety_name.lower()}.md"
        site_file.write_text(content)
        
        # Update varieties index
        self.update_varieties_index(variety_name)
        
        return site_file
    
    def update_varieties_index(self, variety_name: str):
        """Update docs/varieties/index.md to include the new variety."""
        index_file = self.base_path / "docs" / "varieties" / "index.md"
        
        if not index_file.exists():
            return
        
        content = index_file.read_text()
        
        # Check if variety is already listed  
        # Format: "Acadie Blanc" → "Acadie Blanc" (display) + "acadie_blanc.md" (file)
        display_name = variety_name.replace('_', ' ').title()
        file_name = variety_name.lower().replace(' ', '_')
        variety_link = f"- **[{display_name}]({file_name}.md)**"
        if variety_link in content or f"[{display_name}]" in content:
            return  # Already listed
        
        # Find where to insert the new variety (after "## Available Varieties")
        lines = content.split('\n')
        insert_index = None
        
        for i, line in enumerate(lines):
            if line.startswith("*New grape variety articles"):
                insert_index = i
                break
        
        if insert_index is not None:
            # Insert new variety link before the "New grape variety articles" line
            lines.insert(insert_index, variety_link)
            lines.insert(insert_index + 1, "")  # Add blank line
            
            # Update the file
            index_file.write_text('\n'.join(lines))

    def generate_and_save(self, variety_name: str, article_type: str = "technical", publish: bool = False) -> Path:
        """Generate an article and save it, optionally publishing to site."""
        if not self.dry_run:
            type_desc = "winemaking stories" if article_type == "story" else "technical article"
            print(f"Generating {type_desc} for {variety_name}...")
        
        if article_type == "story":
            content = self.generate_story_article(variety_name)
        else:
            content = self.generate_technical_article(variety_name)
        
        if not self.dry_run:
            print(f"Saving article...")
        
        output_file = self.save_article(variety_name, content, article_type)
        
        # Publish to site if requested (only for technical articles)
        if publish and article_type == "technical" and not self.dry_run:
            print(f"Publishing to MkDocs site...")
            self.publish_to_site(variety_name, content)
        
        if not self.dry_run:
            print(f"Article saved to: {output_file}")
        
        return output_file