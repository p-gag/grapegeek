import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class BaseGenerator:
    """Base class with shared functionality for all generators."""
    
    def __init__(self, base_path: str = None, dry_run: bool = False):
        self.dry_run = dry_run
        if not dry_run:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.client = None
            
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.prompts_path = self.base_path / "prompts"
        self.output_path = self.base_path / "output"
        self.debug_path = self.base_path / "debug"
        
        # Ensure output directories exist
        self.output_path.mkdir(parents=True, exist_ok=True)
        if dry_run:
            self.debug_path.mkdir(parents=True, exist_ok=True)
    
    def load_prompt_file(self, relative_path: str) -> str:
        """Load a prompt file from the prompts directory."""
        prompt_path = self.prompts_path / relative_path
        if prompt_path.exists():
            return prompt_path.read_text()
        return ""
    
    def load_yaml_frontmatter(self, file_path: Path, default_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load YAML frontmatter from a file."""
        if not file_path.exists():
            return default_data
        
        content = file_path.read_text()
        
        # Parse YAML frontmatter
        if content.startswith("---"):
            try:
                parts = content.split("---", 2)
                if len(parts) >= 2:
                    yaml_content = parts[1]
                    data = yaml.safe_load(yaml_content)
                    return data or default_data
            except (ValueError, yaml.YAMLError):
                pass
        
        return default_data
    
    def call_openai(self, full_prompt: str, context_info: dict = None) -> str:
        """Make a call to OpenAI API or return debug info for dry run."""
        if self.dry_run:
            debug_info = ["="*80]
            debug_info.append("🔍 DRY RUN DEBUG INFORMATION")
            debug_info.append("="*80)
            
            # Show context information if provided
            if context_info:
                debug_info.append("\n📋 CONTEXT INFORMATION:")
                debug_info.append("-" * 40)
                for key, value in context_info.items():
                    if isinstance(value, dict):
                        debug_info.append(f"• {key.upper()}:")
                        for k, v in value.items():
                            debug_info.append(f"  - {k}: {v}")
                    else:
                        debug_info.append(f"• {key.upper()}: {value}")
            
            debug_info.append("\n🔧 API CONFIGURATION:")
            debug_info.append("-" * 40)
            debug_info.append("• Model: gpt-5")
            debug_info.append("• Tools: [web_search]")
            debug_info.append("• Mode: Responses API")
            
            debug_info.append("\n📝 PROMPT STRUCTURE:")
            debug_info.append("-" * 40)
            
            # Analyze prompt structure
            sections = full_prompt.split('\n\n')
            debug_info.append(f"• Total sections: {len(sections)}")
            debug_info.append(f"• Total characters: {len(full_prompt):,}")
            debug_info.append(f"• Estimated tokens: ~{len(full_prompt) // 4:,}")
            
            # Show prompt sections
            for i, section in enumerate(sections[:5], 1):  # Show first 5 sections
                first_line = section.split('\n')[0][:60]
                debug_info.append(f"  {i}. {first_line}{'...' if len(first_line) == 60 else ''}")
            
            if len(sections) > 5:
                debug_info.append(f"  ... and {len(sections) - 5} more sections")
            
            debug_info.append("\n📄 FULL PROMPT CONTENT:")
            debug_info.append("="*80)
            debug_info.append(full_prompt)
            debug_info.append("="*80)
            debug_info.append("🔍 END DRY RUN DEBUG")
            debug_info.append("="*80)
            
            return '\n'.join(debug_info)
        
        try:
            response = self.client.responses.create(
                model="gpt-5",
                tools=[{"type": "web_search"}],
                input=full_prompt
            )
            
            return response.output_text
            
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
    
    def save_content(self, file_path: Path, content: str) -> Path:
        """Save content to a file."""
        file_path.write_text(content)
        return file_path
    
    def get_prompt_files(self) -> Dict[str, str]:
        """Return a dictionary mapping prompt names to their file paths."""
        prompt_files = {}
        for prompt_file in self.prompts_path.rglob("*.md"):
            relative_path = prompt_file.relative_to(self.prompts_path)
            prompt_files[str(relative_path)] = prompt_file.read_text()
        return prompt_files