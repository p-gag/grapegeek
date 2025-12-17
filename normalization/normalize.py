#!/usr/bin/env python3
"""
Normalization Pipeline - Data normalization orchestration

Runs grape variety and wine type normalization processes.
"""

import argparse
import sys
import subprocess
from pathlib import Path

def run_grape_normalization():
    """Run grape variety normalization."""
    print("🍇 Running grape variety normalization...")
    result = subprocess.run([sys.executable, "normalization/grape_varieties.py"], cwd=Path.cwd())
    return result.returncode == 0

def run_wine_type_normalization():
    """Run wine type normalization (placeholder for future implementation)."""
    print("🍷 Wine type normalization not yet implemented")
    return True

def main():
    parser = argparse.ArgumentParser(description="Run data normalization processes")
    parser.add_argument("--grapes", action="store_true", help="Normalize grape varieties")
    parser.add_argument("--wine-types", action="store_true", help="Normalize wine types")
    parser.add_argument("--all", action="store_true", help="Run all normalization processes")
    
    args = parser.parse_args()
    
    if not any([args.grapes, args.wine_types, args.all]):
        parser.print_help()
        return
    
    print("🎯 Starting Data Normalization")
    print("=" * 50)
    
    success = True
    
    if args.all or args.grapes:
        success &= run_grape_normalization()
        
    if args.all or args.wine_types:
        success &= run_wine_type_normalization()
    
    if success:
        print("\n✅ Normalization completed successfully!")
    else:
        print("\n❌ Normalization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()