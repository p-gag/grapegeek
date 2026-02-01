#!/usr/bin/env python3
"""
Extract Parent Varieties from VIVC Data

This script iterates through existing grape varieties that have VIVC passport data,
recursively extracts parent information, and adds missing parents to the grape variety mapping.

PURPOSE: Parent Data Extraction - Recursively extract parent varieties from existing VIVC data

INPUTS:
- data/grape_variety_mapping.jsonl (via GrapeVarietiesModel)

OUTPUTS:
- data/grape_variety_mapping.jsonl (updated with parent varieties and their portfolio data)

DEPENDENCIES:
- includes.vivc_client for direct VIVC passport fetching
- includes.grape_varieties.GrapeVarietiesModel

USAGE:
# Extract parents from existing VIVC data
uv run src/16_extract_parents_from_vivc.py

# Test mode - show what would be added without saving
uv run src/16_extract_parents_from_vivc.py --dry-run

# Process with recursion limit
uv run src/16_extract_parents_from_vivc.py --max-depth 3
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Set, List, Optional, Tuple
from collections import deque

# Import our modules
from includes.grape_varieties import GrapeVarietiesModel, GrapeVariety
from includes.vivc_client import get_passport_data


class ParentExtractor:
    """Extracts parent varieties recursively from existing VIVC data."""
    
    def __init__(self, data_dir: str = "data", dry_run: bool = False, max_depth: int = 5):
        self.data_dir = Path(data_dir)
        self.varieties_model = GrapeVarietiesModel(data_dir)
        self.dry_run = dry_run
        self.max_depth = max_depth
        self.processed_vivc_ids: Set[str] = set()
        self.new_varieties_added = 0
        self.errors_encountered = 0
        
        # Track existing varieties and VIVC numbers for quick lookup
        self.existing_varieties: Set[str] = set()
        self.existing_vivc_numbers: Set[str] = set()
        self._build_existing_sets()
    
    def _build_existing_sets(self):
        """Build sets of existing variety names and VIVC numbers for quick lookup."""
        print("📋 Building inventory of existing varieties...")
        
        all_varieties = self.varieties_model.get_all_varieties()
        
        for variety in all_varieties:
            # Add the main name (case insensitive)
            self.existing_varieties.add(variety.name.lower())
            
            # Add all aliases (case insensitive)  
            for alias in variety.aliases:
                self.existing_varieties.add(alias.lower())
            
            # Extract VIVC number if available in portfolio
            if variety.portfolio and isinstance(variety.portfolio, dict):
                grape_info = variety.portfolio.get('grape', {})
                if isinstance(grape_info, dict) and grape_info.get('vivc_number'):
                    self.existing_vivc_numbers.add(grape_info['vivc_number'])
        
        print(f"  Found {len(self.existing_varieties)} existing variety names/aliases")
        print(f"  Found {len(self.existing_vivc_numbers)} existing VIVC numbers")
    
    def _extract_parent_info(self, portfolio: dict) -> List[Tuple[str, str]]:
        """Extract parent name and VIVC number pairs from portfolio data."""
        parents = []
        
        for parent_key in ['parent1', 'parent2']:
            parent_data = portfolio.get(parent_key)
            if not parent_data or not isinstance(parent_data, dict):
                continue
                
            name = parent_data.get('name')
            vivc_number = parent_data.get('vivc_number')
            
            if name and vivc_number:
                parents.append((name, vivc_number))
        
        return parents
    
    def _is_parent_missing(self, name: str, vivc_number: str) -> bool:
        """Check if a parent variety is missing from our mapping."""
        # Only check VIVC number - names can be misleading due to Unknown aliases
        if vivc_number and vivc_number in self.existing_vivc_numbers:
            return False
            
        # If no VIVC number, fall back to name check
        if not vivc_number and name.lower() in self.existing_varieties:
            return False
            
        return True
    
    def update_variety_in_model(self, variety_name: str, portfolio_data: dict, status: str):
        """Update a variety's portfolio data in the model and save to file."""
        variety = self.varieties_model.get_variety(variety_name)
        if variety:
            variety.portfolio = portfolio_data
            variety.vivc_assignment_status = status
            # Save the entire model back to JSONL
            self.varieties_model.save_jsonl()
            return True
        return False
    
    def fetch_and_add_parent_variety(self, name: str, vivc_number: str) -> bool:
        """Fetch VIVC passport data and add parent variety to the model."""
        if self.dry_run:
            print(f"    [DRY RUN] Would fetch and add: {name} (VIVC: {vivc_number})")
            return True
        
        try:
            # Fetch passport data directly from VIVC
            print(f"    📋 Fetching passport data for {name} (VIVC: {vivc_number})...")
            passport_data = get_passport_data(vivc_number)
            
            # Create lowercase alias
            alias = name.lower()
            
            # Create new GrapeVariety object
            new_variety = GrapeVariety(
                name=name,
                aliases=[alias],
                grape=True,
                portfolio=passport_data.to_dict(),
                vivc_assignment_status="found",
                notes="Added as parent variety from VIVC data"
            )
            
            # Add to model
            self.varieties_model.varieties[name] = new_variety
            self.varieties_model._alias_to_variety[alias] = name
            
            # Update our tracking sets
            self.existing_varieties.add(name.lower())
            self.existing_varieties.add(alias.lower())
            self.existing_vivc_numbers.add(vivc_number)
            
            # Save to file
            self.varieties_model.save_jsonl()
            
            print(f"    ✅ Added parent variety: {name}")
            self.new_varieties_added += 1
            return True
            
        except Exception as e:
            print(f"    ⚠️  Error fetching {name} (VIVC: {vivc_number}): {e}")
            self.errors_encountered += 1
            return False
    
    def process_variety_parents(self, variety: GrapeVariety, depth: int = 0) -> List[str]:
        """Process a single variety and return list of new parent VIVC numbers to process."""
        if depth >= self.max_depth:
            print(f"    ⏭️  Max depth ({self.max_depth}) reached for {variety.name}")
            return []
        
        if not variety.portfolio or not isinstance(variety.portfolio, dict):
            return []
        
        # Extract parent information
        parents = self._extract_parent_info(variety.portfolio)
        new_parent_vivc_numbers = []
        
        for name, vivc_number in parents:
            # Skip if we already processed this VIVC ID
            if vivc_number in self.processed_vivc_ids:
                print(f"    ⏭️  Already processed VIVC {vivc_number}")
                continue
                
            # Mark as processed
            self.processed_vivc_ids.add(vivc_number)
            
            # Check if parent is missing
            if self._is_parent_missing(name, vivc_number):
                print(f"    🔍 Found missing parent: {name} (VIVC: {vivc_number})")
                
                # Fetch and add the parent
                if self.fetch_and_add_parent_variety(name, vivc_number):
                    new_parent_vivc_numbers.append(vivc_number)
            else:
                print(f"    ⏭️  Parent {name} already exists")
        
        return new_parent_vivc_numbers
    
    def process_all_varieties(self) -> int:
        """Process all varieties with portfolio data recursively to find parents."""
        print("\n🔍 Starting recursive parent extraction...")
        
        # Get initial varieties with portfolio data
        all_varieties = self.varieties_model.get_all_varieties()
        initial_varieties = [v for v in all_varieties if v.grape and v.portfolio]
        
        print(f"📊 Starting with {len(initial_varieties)} grape varieties with portfolio data...")
        print(f"🔄 Max recursion depth: {self.max_depth}")
        
        # Use a queue for breadth-first processing
        processing_queue = deque()
        
        # Add initial varieties to queue
        for variety in initial_varieties:
            processing_queue.append((variety, 0))  # (variety, depth)
        
        varieties_processed = 0
        
        while processing_queue:
            variety, depth = processing_queue.popleft()
            varieties_processed += 1
            
            print(f"\n[Depth {depth}] Processing: {variety.name}")
            
            # Process this variety's parents
            new_parent_vivc_numbers = self.process_variety_parents(variety, depth)
            
            # Add newly found parents to the queue for next level processing
            if depth < self.max_depth - 1:  # Don't queue if we're at max depth
                for vivc_number in new_parent_vivc_numbers:
                    # Find the newly added variety
                    new_variety = None
                    for v in self.varieties_model.get_all_varieties():
                        if (v.portfolio and isinstance(v.portfolio, dict) and
                            v.portfolio.get('grape', {}).get('vivc_number') == vivc_number):
                            new_variety = v
                            break
                    
                    if new_variety:
                        processing_queue.append((new_variety, depth + 1))
        
        print(f"\n📊 Processed {varieties_processed} variety records")
        return varieties_processed
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the extraction process."""
        all_varieties = self.varieties_model.get_all_varieties()
        grape_varieties = [v for v in all_varieties if v.grape]
        varieties_with_portfolio = [v for v in grape_varieties if v.portfolio]
        
        return {
            "total_varieties": len(all_varieties),
            "grape_varieties": len(grape_varieties),
            "varieties_with_portfolio": len(varieties_with_portfolio),
            "new_varieties_added": self.new_varieties_added,
            "errors_encountered": self.errors_encountered,
            "vivc_ids_processed": len(self.processed_vivc_ids)
        }
    
    def print_summary(self):
        """Print summary of the extraction process."""
        stats = self.get_stats()
        
        print(f"\n📊 Final Summary:")
        print(f"  Total varieties in mapping: {stats['total_varieties']}")
        print(f"  Grape varieties: {stats['grape_varieties']}")
        print(f"  Varieties with VIVC portfolio data: {stats['varieties_with_portfolio']}")
        print(f"  New parent varieties added: {stats['new_varieties_added']}")
        print(f"  VIVC IDs processed: {stats['vivc_ids_processed']}")
        print(f"  Errors encountered: {stats['errors_encountered']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract parent varieties recursively from existing VIVC data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/16_extract_parents_from_vivc.py                    # Extract parents recursively
  python src/16_extract_parents_from_vivc.py --dry-run         # Show what would be added
  python src/16_extract_parents_from_vivc.py --max-depth 2     # Limit recursion depth
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be added without making changes"
    )
    
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum recursion depth for parent extraction (default: 5)"
    )
    
    args = parser.parse_args()
    
    try:
        extractor = ParentExtractor(
            dry_run=args.dry_run, 
            max_depth=args.max_depth
        )
        
        # Process all varieties recursively
        processed_count = extractor.process_all_varieties()
        
        # Print summary
        extractor.print_summary()
        
        if args.dry_run:
            print(f"\n🔍 DRY RUN: Would add parent varieties and their descendants")
        else:
            print(f"\n✅ Successfully processed {processed_count} variety records")
            if extractor.new_varieties_added > 0:
                print(f"💡 Added {extractor.new_varieties_added} new parent varieties to mapping")
                print(f"💡 Tip: Run this script again to find parents of newly added varieties")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()