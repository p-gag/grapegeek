from pathlib import Path
from typing import Dict, Any
from shared.base import BaseGenerator


class RegionResearcher(BaseGenerator):
    """Research grape varieties in specific regions."""
    
    def __init__(self, base_path: str = None, dry_run: bool = False):
        super().__init__(base_path, dry_run)
    
    def load_region_context(self, region_name: str) -> Dict[str, Any]:
        """Load region-specific context from YAML frontmatter."""
        region_file = self.prompts_path / "regions" / f"{region_name.lower().replace(' ', '_')}.md"
        default_data = {"name": region_name}
        return self.load_yaml_frontmatter(region_file, default_data)
    
    def research_region_varieties(self, region_name: str) -> str:
        """Research grape varieties in a specific region."""
        system_prompt = "" #self.load_prompt_file("general/system_prompt.md")
        research_prompt = self.load_prompt_file("regions/region_research_prompt.md")
        region_context = self.load_region_context(region_name)
        
        user_prompt = research_prompt
        user_prompt += f"\n\nREGION TO RESEARCH: {region_context['name']}"
        
        if region_context.get('summary'):
            user_prompt += f"\nRegion Summary: {region_context['summary']}"
        
        if region_context.get('known_varieties'):
            user_prompt += f"\nKnown Varieties (for reference): {region_context['known_varieties']}"
        
        if region_context.get('trade_association_url'):
            user_prompt += f"\nTrade Association: {region_context.get('trade_association', 'Regional Association')} - {region_context['trade_association_url']}"
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Prepare debug context
        context_info = {
            "use_case": "Region Variety Research",
            "region_name": region_name,
            "region_context": region_context,
            "prompts_loaded": {
                "system_prompt": "✓ Loaded" if system_prompt else "✗ Missing",
                "research_prompt": "✓ Loaded" if research_prompt else "✗ Missing",
                "region_context_file": f"regions/{region_name.lower().replace(' ', '_')}.md"
            },
            "context_elements": {
                "has_summary": "✓" if region_context.get('summary') else "✗",
                "has_known_varieties": "✓" if region_context.get('known_varieties') else "✗",
                "has_trade_association": "✓" if region_context.get('trade_association_url') else "✗"
            }
        }
        
        return self.call_openai(full_prompt, context_info)
    
    def save_region_research(self, region_name: str, content: str) -> Path:
        """Save the region research to the appropriate directory."""
        if self.dry_run:
            # Save to debug directory during dry runs
            output_file = self.debug_path / f"{region_name.lower().replace(' ', '_')}_region_debug.md"
        else:
            # Save to normal output directory
            (self.output_path / "regions").mkdir(parents=True, exist_ok=True)
            output_file = self.output_path / "regions" / f"{region_name.lower().replace(' ', '_')}_varieties.md"
        
        return self.save_content(output_file, content)
    
    def research_and_save(self, region_name: str) -> Path:
        """Research region varieties and save the results."""
        if not self.dry_run:
            print(f"Researching grape varieties in {region_name}...")
        
        content = self.research_region_varieties(region_name)
        
        if not self.dry_run:
            print(f"Saving region research...")
        
        output_file = self.save_region_research(region_name, content)
        
        if not self.dry_run:
            print(f"Region research saved to: {output_file}")
        
        return output_file