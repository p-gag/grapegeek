import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GrapeArticleGenerator:
    """Generate magazine-style articles about cold-climate grape varieties using OpenAI with web search."""
    
    def __init__(self, base_path: str = None):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.prompts_path = self.base_path / "prompts"
        self.output_path = self.base_path / "output"
        
        # Ensure output directories exist
        (self.output_path / "articles").mkdir(parents=True, exist_ok=True)
        (self.output_path / "citations").mkdir(parents=True, exist_ok=True)
    
    def load_system_prompt(self) -> str:
        """Load the general system prompt."""
        system_prompt_path = self.prompts_path / "general" / "system_prompt.md"
        if system_prompt_path.exists():
            return system_prompt_path.read_text()
        return ""
    
    def load_article_prompt(self) -> str:
        """Load the article generation prompt."""
        article_prompt_path = self.prompts_path / "grapes" / "article_prompt.md"
        if article_prompt_path.exists():
            return article_prompt_path.read_text()
        return ""
    
    def load_variety_context(self, variety_name: str) -> Dict[str, Any]:
        """Load variety-specific context from YAML frontmatter."""
        variety_file = self.prompts_path / "grapes" / "articles" / f"{variety_name.lower()}.md"
        
        if not variety_file.exists():
            return {"name": variety_name, "prompt": ""}
        
        content = variety_file.read_text()
        
        # Parse YAML frontmatter
        if content.startswith("---"):
            try:
                parts = content.split("---", 2)
                if len(parts) >= 2:
                    yaml_content = parts[1]
                    variety_data = yaml.safe_load(yaml_content)
                    return variety_data or {"name": variety_name, "prompt": ""}
            except (ValueError, yaml.YAMLError):
                pass
        
        return {"name": variety_name, "prompt": ""}
    
    def generate_article(self, variety_name: str) -> str:
        """Generate a complete article for a grape variety using OpenAI with web search."""
        
        # Load prompts and context
        system_prompt = self.load_system_prompt()
        article_prompt = self.load_article_prompt()
        variety_context = self.load_variety_context(variety_name)
        
        # Build user prompt from article prompt and variety context
        user_prompt = article_prompt
        user_prompt += f"\n\nVariety: {variety_context['name']}"
        
        if variety_context.get('prompt'):
            user_prompt += f"\nSpecific context: {variety_context['prompt']}"
        
        try:
            # Combine system and user prompts for Responses API
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.client.responses.create(
                model="gpt-5",
                tools=[{"type": "web_search"}],
                input=full_prompt
            )
            
            # Access the text content from the response
            return response.output_text
            
        except Exception as e:
            return f"Error generating article for {variety_name}: {str(e)}"
    
    def save_article(self, variety_name: str, content: str) -> Path:
        """Save the generated article to the output directory."""
        output_file = self.output_path / "articles" / f"{variety_name.lower()}.md"
        output_file.write_text(content)
        return output_file
    
    def generate_and_save(self, variety_name: str) -> Path:
        """Generate an article and save it, returning the output file path."""
        print(f"Generating article for {variety_name}...")
        article_content = self.generate_article(variety_name)
        
        print(f"Saving article...")
        output_file = self.save_article(variety_name, article_content)
        
        print(f"Article saved to: {output_file}")
        return output_file