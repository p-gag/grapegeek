#!/usr/bin/env python3
"""
Grape Varieties Model

Manages grape variety mappings and aliases with VIVC enrichment data.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict


@dataclass
class GrapeId:
    """Grape identifier with name and VIVC number."""
    name: Optional[str] = None
    vivc_number: Optional[str] = None
    
    def __str__(self) -> str:
        if self.name and self.vivc_number:
            return f"{self.name} ({self.vivc_number})"
        elif self.name:
            return self.name
        elif self.vivc_number:
            return f"VIVC {self.vivc_number}"
        else:
            return "Unknown"


@dataclass
class PassportData:
    """Structured passport data for a grape variety."""
    grape: GrapeId
    berry_skin_color: Optional[str] = None
    country_of_origin: Optional[str] = None
    species: Optional[str] = None
    parent1: Optional[GrapeId] = None
    parent2: Optional[GrapeId] = None
    sex_of_flower: Optional[str] = None
    number_of_photos: Optional[str] = None
    year_of_crossing: Optional[str] = None
    synonyms: Optional[List[str]] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON format."""
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class GrapeVariety:
    """Model for a grape variety with its aliases and VIVC data."""
    name: str
    aliases: List[str]
    grape: bool = True  # True if it's a grape, False if fruit/other
    vivc: Optional[Dict] = None  # VIVC passport data as dict
    vivc_assignment_status: Optional[str] = None  # found, not_found, error, skipped_not_grape
    notes: Optional[str] = None  # Additional notes
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return asdict(self)
    
    def to_jsonl_entry(self) -> str:
        """Convert to JSONL format."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class GrapeVarietiesModel:
    """Model for managing grape variety data."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.jsonl_file = self.data_dir / "grape_variety_mapping.jsonl"
        self.varieties: Dict[str, GrapeVariety] = {}
        self._alias_to_variety: Dict[str, str] = {}
        
        # Load data
        self._load_jsonl()
    
    def _load_jsonl(self):
        """Load grape varieties from JSONL file."""
        self.varieties = {}
        self._alias_to_variety = {}
        
        if not self.jsonl_file.exists():
            return
        
        with open(self.jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        variety_data = json.loads(line)
                        
                        # Handle both old and new format
                        if 'grape' not in variety_data:
                            variety_data['grape'] = True  # Default to True for old format
                        
                        # Ensure aliases is a list
                        if 'aliases' not in variety_data:
                            variety_data['aliases'] = []
                        elif variety_data['aliases'] is None:
                            variety_data['aliases'] = []
                        
                        # Handle VIVC data
                        if 'vivc' not in variety_data:
                            variety_data['vivc'] = None
                        
                        # Handle VIVC assignment status
                        if 'vivc_assignment_status' not in variety_data:
                            variety_data['vivc_assignment_status'] = None
                        
                        # Handle notes field
                        if 'notes' not in variety_data:
                            variety_data['notes'] = None
                        
                        variety = GrapeVariety(**variety_data)
                        
                        # Store variety by name
                        self.varieties[variety.name] = variety
                        
                        # Build alias lookup
                        for alias in variety.aliases:
                            alias_lower = alias.lower().strip()
                            if alias_lower:
                                self._alias_to_variety[alias_lower] = variety.name
                    
                    except json.JSONDecodeError as e:
                        print(f"Warning: Skipping malformed JSON on line {line_num}: {e}")
                        continue
                    except Exception as e:
                        print(f"Warning: Error processing line {line_num}: {e}")
                        continue
    
    def get_variety(self, name: str) -> Optional[GrapeVariety]:
        """Get a variety by name."""
        return self.varieties.get(name)
    
    def get_all_varieties(self) -> List[GrapeVariety]:
        """Get all varieties."""
        return list(self.varieties.values())
    
    def get_variety_names(self) -> List[str]:
        """Get all variety names."""
        return list(self.varieties.keys())
    
    def get_grape_varieties(self) -> List[GrapeVariety]:
        """Get only grape varieties (not fruit)."""
        return [v for v in self.varieties.values() if v.grape]
    
    def get_fruit_varieties(self) -> List[GrapeVariety]:
        """Get only fruit varieties (not grapes)."""
        return [v for v in self.varieties.values() if not v.grape]
    
    def normalize_variety_name(self, input_name: str) -> Optional[str]:
        """Normalize a variety name using aliases.
        
        Args:
            input_name: Input variety name to normalize
            
        Returns:
            Normalized variety name or None if not found
        """
        input_lower = input_name.lower().strip()
        
        # First check direct match with variety names
        for variety_name in self.varieties:
            if variety_name.lower() == input_lower:
                return variety_name
        
        # Then check aliases
        return self._alias_to_variety.get(input_lower)
    
    def search_varieties(self, query: str) -> List[str]:
        """Search for varieties by partial name match.
        
        Args:
            query: Search query
            
        Returns:
            List of matching variety names
        """
        query_lower = query.lower().strip()
        matches = []
        
        for variety_name in self.varieties:
            # Check variety name
            if query_lower in variety_name.lower():
                matches.append(variety_name)
                continue
            
            # Check aliases
            variety = self.varieties[variety_name]
            for alias in variety.aliases:
                if query_lower in alias.lower():
                    matches.append(variety_name)
                    break
        
        return sorted(list(set(matches)))
    
    def get_aliases(self, variety_name: str) -> List[str]:
        """Get all aliases for a variety."""
        variety = self.get_variety(variety_name)
        return variety.aliases if variety else []
    
    def add_variety(self, name: str, aliases: List[str] = None):
        """Add a new variety (for programmatic updates)."""
        if aliases is None:
            aliases = []
        
        variety = GrapeVariety(name=name, aliases=aliases)
        self.varieties[name] = variety
        
        # Update alias lookup
        for alias in aliases:
            alias_lower = alias.lower().strip()
            if alias_lower:
                self._alias_to_variety[alias_lower] = name
    
    def save_jsonl(self):
        """Save current varieties to JSONL file."""
        with open(self.jsonl_file, 'w', encoding='utf-8') as f:
            for variety in self.varieties.values():
                f.write(variety.to_jsonl_entry() + '\n')
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the variety data."""
        total_varieties = len(self.varieties)
        grape_varieties = len([v for v in self.varieties.values() if v.grape])
        fruit_varieties = len([v for v in self.varieties.values() if not v.grape])
        total_aliases = sum(len(v.aliases) for v in self.varieties.values())
        
        # VIVC stats
        vivc_found = len([v for v in self.varieties.values() if v.vivc_assignment_status == "found"])
        vivc_not_found = len([v for v in self.varieties.values() if v.vivc_assignment_status == "not_found"])
        vivc_error = len([v for v in self.varieties.values() if v.vivc_assignment_status == "error"])
        vivc_skipped = len([v for v in self.varieties.values() if v.vivc_assignment_status == "skipped_not_grape"])
        
        return {
            "total_varieties": total_varieties,
            "grape_varieties": grape_varieties,
            "fruit_varieties": fruit_varieties,
            "total_aliases": total_aliases,
            "average_aliases_per_variety": total_aliases / total_varieties if total_varieties > 0 else 0,
            "vivc_found": vivc_found,
            "vivc_not_found": vivc_not_found,
            "vivc_error": vivc_error,
            "vivc_skipped": vivc_skipped
        }
    
    def consolidate_duplicates(self) -> 'GrapeVarietiesModel':
        """Consolidate varieties that have the same VIVC number."""
        consolidated_varieties = {}
        vivc_to_varieties = {}
        
        # Group varieties by VIVC number
        for name, variety in self.varieties.items():
            vivc_number = None
            
            # Extract VIVC number if available
            if variety.vivc and isinstance(variety.vivc, dict):
                grape_info = variety.vivc.get('grape', {})
                if isinstance(grape_info, dict):
                    vivc_number = grape_info.get('vivc_number')
            
            if vivc_number and vivc_number.strip():
                if vivc_number not in vivc_to_varieties:
                    vivc_to_varieties[vivc_number] = []
                vivc_to_varieties[vivc_number].append((name, variety))
            else:
                # No VIVC number, keep as is
                consolidated_varieties[name] = variety
        
        # Consolidate varieties with the same VIVC number
        for vivc_number, variety_list in vivc_to_varieties.items():
            if len(variety_list) == 1:
                # Only one variety with this VIVC number
                name, variety = variety_list[0]
                consolidated_varieties[name] = variety
            else:
                # Multiple varieties with same VIVC number - merge them
                print(f"  Consolidating {len(variety_list)} varieties with VIVC {vivc_number}")
                
                # Use the first variety as the base
                primary_name, primary_variety = variety_list[0]
                merged_aliases = set(primary_variety.aliases)
                
                # Add all names and aliases from other varieties
                for name, variety in variety_list:
                    # Add the variety name as an alias (normalize case for consistency)
                    if name != primary_name:  # Don't add primary name as alias to itself
                        merged_aliases.add(name.lower())
                    merged_aliases.update(variety.aliases)
                    print(f"    - {name} (aliases: {len(variety.aliases)})")
                
                # Remove the primary name from aliases if it's there (including any case variations)
                merged_aliases.discard(primary_name)
                merged_aliases.discard(primary_name.lower())
                
                # Create consolidated variety
                consolidated_variety = GrapeVariety(
                    name=primary_name,
                    aliases=sorted(list(merged_aliases)),
                    grape=primary_variety.grape,
                    vivc=primary_variety.vivc,
                    vivc_assignment_status=primary_variety.vivc_assignment_status
                )
                
                consolidated_varieties[primary_name] = consolidated_variety
                print(f"    → Merged into '{primary_name}' with {len(merged_aliases)} total aliases")
        
        # Create new model with consolidated data
        consolidated_model = GrapeVarietiesModel.__new__(GrapeVarietiesModel)
        consolidated_model.data_dir = self.data_dir
        consolidated_model.jsonl_file = self.data_dir / (self.jsonl_file.stem + "_consolidated.jsonl")
        consolidated_model.varieties = consolidated_varieties
        consolidated_model._alias_to_variety = {}
        
        # Rebuild alias lookup
        for variety_name, variety in consolidated_varieties.items():
            for alias in variety.aliases:
                alias_lower = alias.lower().strip()
                if alias_lower:
                    consolidated_model._alias_to_variety[alias_lower] = variety_name
        
        return consolidated_model


# Global instance for easy access
_grape_varieties_model = None


def get_grape_varieties_model() -> GrapeVarietiesModel:
    """Get the global grape varieties model instance."""
    global _grape_varieties_model
    if _grape_varieties_model is None:
        _grape_varieties_model = GrapeVarietiesModel()
    return _grape_varieties_model


# Convenience functions for common operations
def normalize_variety_name(input_name: str) -> Optional[str]:
    """Normalize a variety name using the global model."""
    return get_grape_varieties_model().normalize_variety_name(input_name)


def search_varieties(query: str) -> List[str]:
    """Search for varieties using the global model."""
    return get_grape_varieties_model().search_varieties(query)


def get_variety_aliases(variety_name: str) -> List[str]:
    """Get aliases for a variety using the global model."""
    return get_grape_varieties_model().get_aliases(variety_name)


def main():
    """CLI interface for the grape varieties model."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Grape Varieties Model CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search varieties')
    search_parser.add_argument('query', help='Search query')
    
    # Normalize command
    normalize_parser = subparsers.add_parser('normalize', help='Normalize variety name')
    normalize_parser.add_argument('name', help='Variety name to normalize')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all varieties')
    list_parser.add_argument('--limit', type=int, help='Limit number of results')
    
    # Consolidate command
    consolidate_parser = subparsers.add_parser('consolidate', help='Consolidate varieties with same VIVC number')
    consolidate_parser.add_argument('--dry-run', action='store_true', help='Show what would be consolidated without saving')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        model = get_grape_varieties_model()
        
        if args.command == 'search':
            matches = model.search_varieties(args.query)
            if matches:
                print(f"Found {len(matches)} matches for '{args.query}':")
                for match in matches:
                    print(f"  - {match}")
            else:
                print(f"No matches found for '{args.query}'")
        
        elif args.command == 'normalize':
            normalized = model.normalize_variety_name(args.name)
            if normalized:
                print(f"'{args.name}' -> '{normalized}'")
                aliases = model.get_aliases(normalized)
                if aliases:
                    print(f"Aliases: {', '.join(aliases[:5])}{'...' if len(aliases) > 5 else ''}")
            else:
                print(f"No normalization found for '{args.name}'")
        
        elif args.command == 'stats':
            stats = model.get_stats()
            print("Grape Varieties Statistics:")
            print(f"  Total varieties: {stats['total_varieties']}")
            print(f"  Grape varieties: {stats['grape_varieties']}")
            print(f"  Fruit varieties: {stats['fruit_varieties']}")
            print(f"  Total aliases: {stats['total_aliases']}")
            print(f"  Average aliases per variety: {stats['average_aliases_per_variety']:.1f}")
            
            if stats['vivc_found'] > 0 or stats['vivc_not_found'] > 0:
                print(f"\n  VIVC Assignment:")
                print(f"  Found: {stats['vivc_found']}")
                print(f"  Not found: {stats['vivc_not_found']}")
                print(f"  Errors: {stats['vivc_error']}")
                print(f"  Skipped: {stats['vivc_skipped']}")
        
        elif args.command == 'consolidate':
            print("🔄 Consolidating varieties with duplicate VIVC numbers...")
            consolidated_model = model.consolidate_duplicates()
            
            if not args.dry_run:
                consolidated_model.save_jsonl()
                print(f"✅ Consolidated data saved to: {consolidated_model.jsonl_file}")
            else:
                print("✅ Dry run completed - no files saved")
            
            # Show before/after stats
            original_stats = model.get_stats()
            consolidated_stats = consolidated_model.get_stats()
            
            print(f"\n📊 Consolidation Results:")
            print(f"  Original varieties: {original_stats['total_varieties']}")
            print(f"  Consolidated varieties: {consolidated_stats['total_varieties']}")
            print(f"  Varieties merged: {original_stats['total_varieties'] - consolidated_stats['total_varieties']}")
            print(f"  Total aliases: {original_stats['total_aliases']} → {consolidated_stats['total_aliases']}")
        
        elif args.command == 'list':
            varieties = model.get_variety_names()
            if args.limit:
                varieties = varieties[:args.limit]
            
            print(f"Grape varieties ({len(varieties)} shown):")
            for variety in varieties:
                aliases_count = len(model.get_aliases(variety))
                print(f"  - {variety} ({aliases_count} aliases)")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()