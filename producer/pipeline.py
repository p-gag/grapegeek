#!/usr/bin/env python3
"""
Producer Pipeline - Complete wine producer data processing workflow

Orchestrates the full pipeline from RACJ data fetching to GeoJSON map generation.
"""

import argparse
import sys
from pathlib import Path

def run_fetch_producers():
    """Run the producer data fetching step."""
    print("🗂️  Fetching RACJ producer data...")
    import subprocess
    result = subprocess.run([sys.executable, "producer/fetch_producers.py"], cwd=Path.cwd())
    return result.returncode == 0

def run_enrich_data(limit=None):
    """Run the data enrichment step."""
    print("🤖 Enriching producer data...")
    import subprocess
    cmd = [sys.executable, "producer/enrich_data.py"]
    if limit:
        cmd.extend(["--limit", str(limit)])
    result = subprocess.run(cmd, cwd=Path.cwd())
    return result.returncode == 0

def run_generate_map():
    """Run the map generation step."""
    print("🗺️  Generating GeoJSON map data...")
    import subprocess
    result = subprocess.run([sys.executable, "producer/generate_map.py"], cwd=Path.cwd())
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Run the complete producer data pipeline")
    parser.add_argument("--fetch", action="store_true", help="Fetch RACJ producer data")
    parser.add_argument("--enrich", action="store_true", help="Enrich producer data")
    parser.add_argument("--enrich-limit", type=int, help="Limit number of producers to enrich")
    parser.add_argument("--map", action="store_true", help="Generate map data")
    parser.add_argument("--full", action="store_true", help="Run complete pipeline")
    
    args = parser.parse_args()
    
    if not any([args.fetch, args.enrich, args.map, args.full]):
        parser.print_help()
        return
    
    print("🍷 Starting Producer Data Pipeline")
    print("=" * 50)
    
    success = True
    
    if args.full or args.fetch:
        success &= run_fetch_producers()
        
    if success and (args.full or args.enrich):
        success &= run_enrich_data(args.enrich_limit)
        
    if success and (args.full or args.map):
        success &= run_generate_map()
    
    if success:
        print("\n✅ Pipeline completed successfully!")
    else:
        print("\n❌ Pipeline failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()