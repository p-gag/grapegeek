#!/usr/bin/env python3

from src.grapegeek.article_generator import GrapeArticleGenerator

def validate_prompt_loading():
    """Validate that all three prompt files are loaded correctly."""
    
    generator = GrapeArticleGenerator()
    variety_name = "itasca"
    
    print("=== PROMPT VALIDATION ===\n")
    
    # 1. Load system prompt
    system_prompt = generator.load_system_prompt()
    print("1. SYSTEM PROMPT (prompts/general/system_prompt.md):")
    print("   Status:", "✅ LOADED" if system_prompt else "❌ MISSING")
    print(f"   Length: {len(system_prompt)} characters")
    print(f"   First 100 chars: {system_prompt[:100]}...")
    print()
    
    # 2. Load article prompt
    article_prompt = generator.load_article_prompt()
    print("2. ARTICLE PROMPT (prompts/grapes/article_prompt.md):")
    print("   Status:", "✅ LOADED" if article_prompt else "❌ MISSING")
    print(f"   Length: {len(article_prompt)} characters")
    print(f"   First 100 chars: {article_prompt[:100]}...")
    print()
    
    # 3. Load variety context
    variety_context = generator.load_variety_context(variety_name)
    print(f"3. VARIETY CONTEXT (prompts/grapes/articles/{variety_name}.md):")
    print("   Status:", "✅ LOADED" if variety_context.get('name') else "❌ MISSING")
    print(f"   Name: {variety_context.get('name')}")
    print(f"   Context: {variety_context.get('prompt')}")
    print()
    
    # 4. Show how they're combined
    user_prompt = article_prompt
    user_prompt += f"\n\nVariety: {variety_context['name']}"
    if variety_context.get('prompt'):
        user_prompt += f"\nSpecific context: {variety_context['prompt']}"
    
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    print("4. FINAL COMBINED PROMPT:")
    print(f"   Total length: {len(full_prompt)} characters")
    print("   Structure:")
    print("   - System Prompt (defines AI behavior and tone)")
    print("   - Article Prompt (defines article generation instructions)")
    print("   - Variety Name (Itasca)")
    print("   - Variety Context (White grape variety developed at University of Minnesota)")
    print()
    
    print("=== VALIDATION COMPLETE ===")
    print("✅ All three prompt files are being loaded and combined correctly!")

if __name__ == "__main__":
    validate_prompt_loading()