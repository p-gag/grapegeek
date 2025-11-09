#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
from src.grapegeek.article_generator import GrapeArticleGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate magazine-style articles about cold-climate grape varieties")
    parser.add_argument("variety", help="Name of the grape variety to generate an article for")
    parser.add_argument("--output-dir", default="output", help="Output directory for generated articles")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = GrapeArticleGenerator()
    
    try:
        # Generate and save article
        output_file = generator.generate_and_save(args.variety)
        print(f"✅ Successfully generated article for {args.variety}")
        print(f"📄 Output: {output_file}")
        
    except Exception as e:
        print(f"❌ Error generating article: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
