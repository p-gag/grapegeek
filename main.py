#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
from src.grapegeek.grape_article_generator import GrapeArticleGenerator
from src.grapegeek.region_researcher import RegionResearcher

def main():
    parser = argparse.ArgumentParser(description="Generate magazine-style articles about cold-climate grape varieties")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Grape variety article generation
    grape_parser = subparsers.add_parser("grape", help="Generate articles about grape varieties")
    grape_parser.add_argument("variety", help="Name of the grape variety to generate an article for")
    grape_parser.add_argument("--type", choices=["technical", "story"], default="technical", 
                             help="Type of article: 'technical' for comprehensive analysis, 'story' for winemaking stories")
    grape_parser.add_argument("--dry-run", action="store_true", help="Show prompts without calling OpenAI")
    
    # Region research
    region_parser = subparsers.add_parser("region", help="Research grape varieties in a region")
    region_parser.add_argument("region", help="Name of the region to research")
    region_parser.add_argument("--dry-run", action="store_true", help="Show prompts without calling OpenAI")
    
    # Common arguments
    parser.add_argument("--output-dir", default="output", help="Output directory for generated content")
    
    args = parser.parse_args()
    
    # If no command specified, assume it's a grape variety (backward compatibility)
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "grape":
            # Initialize grape article generator
            generator = GrapeArticleGenerator(dry_run=args.dry_run)
            
            # Generate and save article
            output_file = generator.generate_and_save(args.variety, args.type)
            
            if not args.dry_run:
                article_type = "winemaking stories" if args.type == "story" else "technical article"
                print(f"✅ Successfully generated {article_type} for {args.variety}")
                print(f"📄 Output: {output_file}")
            else:
                print(f"📄 Dry run output: {output_file}")
            
        elif args.command == "region":
            # Initialize region researcher
            researcher = RegionResearcher(dry_run=args.dry_run)
            
            # Research and save region varieties
            output_file = researcher.research_and_save(args.region)
            
            if not args.dry_run:
                print(f"✅ Successfully researched grape varieties in {args.region}")
                print(f"📄 Output: {output_file}")
            else:
                print(f"📄 Dry run output: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
