#!/usr/bin/env python3
"""
Site Build Pipeline - Site management and translation orchestration

Handles index updates, French synchronization, and site building.
"""

import argparse
import sys
import subprocess
from pathlib import Path

def run_update_indexes():
    """Update site indexes."""
    print("📚 Updating site indexes...")
    result = subprocess.run([sys.executable, "site/update_indexes.py"], cwd=Path.cwd())
    return result.returncode == 0

def run_sync_french():
    """Sync French translations."""
    print("🇫🇷 Syncing French translations...")
    result = subprocess.run([sys.executable, "site/sync_french.py"], cwd=Path.cwd())
    return result.returncode == 0

def run_mkdocs_build():
    """Build MkDocs site."""
    print("🏗️  Building MkDocs site...")
    result = subprocess.run(["mkdocs", "build"], cwd=Path.cwd())
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Site management and build pipeline")
    parser.add_argument("--update-indexes", action="store_true", help="Update site indexes")
    parser.add_argument("--sync-french", action="store_true", help="Sync French translations")
    parser.add_argument("--build", action="store_true", help="Build MkDocs site")
    parser.add_argument("--all", action="store_true", help="Run complete site build pipeline")
    
    args = parser.parse_args()
    
    if not any([args.update_indexes, args.sync_french, args.build, args.all]):
        parser.print_help()
        return
    
    print("🌐 Starting Site Build Pipeline")
    print("=" * 50)
    
    success = True
    
    if args.all or args.update_indexes:
        success &= run_update_indexes()
        
    if success and (args.all or args.sync_french):
        success &= run_sync_french()
        
    if success and (args.all or args.build):
        success &= run_mkdocs_build()
    
    if success:
        print("\n✅ Site build completed successfully!")
    else:
        print("\n❌ Site build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()