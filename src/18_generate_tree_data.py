#!/usr/bin/env python3
"""
Grape Variety Tree Data Generator for React Flow

Generates JSON data for grape variety family trees to be consumed by React Flow.
Extracts data generation logic from the main tree viewer generator.

PURPOSE: Data Extraction - Generate tree data for React Flow consumption

INPUTS:
- data/grape_variety_mapping.jsonl (via GrapeVarietiesModel)

OUTPUTS:
- grape-tree-react/src/data/tree-data.json (tree data for React Flow)

USAGE:
# Generate tree data for React Flow
uv run src/18_generate_tree_data.py

# Output to specific location
uv run src/18_generate_tree_data.py --output custom_path.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass

# Import our modules
from includes.grape_varieties import GrapeVarietiesModel


@dataclass
class TreeNode:
    """Represents a node in the grape variety tree."""
    name: str
    vivc_number: Optional[str] = None
    berry_color: Optional[str] = None
    country: Optional[str] = None
    species: Optional[str] = None
    sex: Optional[str] = None
    breeder: Optional[str] = None
    year_crossing: Optional[str] = None
    parent1: Optional['TreeNode'] = None
    parent2: Optional['TreeNode'] = None
    is_duplicate: bool = False
    original_reference: Optional[str] = None


class TreeDataGenerator:
    """Generates tree data for grape varieties for React Flow consumption."""
    
    # Country to ISO code mapping for flag icons
    COUNTRY_FLAGS = {
        'CANADA': 'ca',
        'USA': 'us',
        'UNITED STATES': 'us',
        'UNITED STATES OF AMERICA': 'us',
        'US': 'us',
        'FRANCE': 'fr',
        'GERMANY': 'de',
        'DEUTSCHE': 'de',
        'ITALY': 'it',
        'ITALIA': 'it',
        'SPAIN': 'es',
        'ESPAÑA': 'es',
        'PORTUGAL': 'pt',
        'AUSTRIA': 'at',
        'SWITZERLAND': 'ch',
        'SUISSE': 'ch',
        'HUNGARY': 'hu',
        'ROMANIA': 'ro',
        'BULGARIA': 'bg',
        'GREECE': 'gr',
        'TURKEY': 'tr',
        'GEORGIA': 'ge',
        'MOLDOVA': 'md',
        'UKRAINE': 'ua',
        'RUSSIA': 'ru',
        'RUSSIAN FEDERATION': 'ru',
        'KAZAKHSTAN': 'kz',
        'UZBEKISTAN': 'uz',
        'ARMENIA': 'am',
        'AZERBAIJAN': 'az',
        'CROATIA': 'hr',
        'SLOVENIA': 'si',
        'SERBIA': 'rs',
        'MONTENEGRO': 'me',
        'BOSNIA AND HERZEGOVINA': 'ba',
        'NORTH MACEDONIA': 'mk',
        'ALBANIA': 'al',
        'CYPRUS': 'cy',
        'ISRAEL': 'il',
        'LEBANON': 'lb',
        'SYRIA': 'sy',
        'EUROPE': 'eu',
        'ALGERIA': 'dz',
        'MOROCCO': 'ma',
        'TUNISIA': 'tn',
        'EGYPT': 'eg',
        'CHINA': 'cn',
        'JAPAN': 'jp',
        'SOUTH KOREA': 'kr',
        'AUSTRALIA': 'au',
        'NEW ZEALAND': 'nz',
        'SOUTH AFRICA': 'za',
        'CHILE': 'cl',
        'ARGENTINA': 'ar',
        'BRAZIL': 'br',
        'URUGUAY': 'uy',
        'PERU': 'pe',
        'COLOMBIA': 'co',
        'VENEZUELA': 've',
        'UNITED KINGDOM': 'gb',
        'GREAT BRITAIN': 'gb',
        'ENGLAND': 'gb',
        'SCOTLAND': 'gb',
        'WALES': 'gb',
        'IRELAND': 'ie',
        'NETHERLANDS': 'nl',
        'BELGIUM': 'be',
        'DENMARK': 'dk',
        'SWEDEN': 'se',
        'NORWAY': 'no',
        'FINLAND': 'fi',
        'POLAND': 'pl',
        'CZECH REPUBLIC': 'cz',
        'SLOVAKIA': 'sk',
        'LITHUANIA': 'lt',
        'LATVIA': 'lv',
        'ESTONIA': 'ee'
    }
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.varieties_model = GrapeVarietiesModel(data_dir)
        self.processed_varieties: Set[str] = set()
        self.variety_nodes: Dict[str, TreeNode] = {}
        self.producer_varieties: Set[str] = set()
        self._load_producer_varieties()
    
    def _load_producer_varieties(self):
        """Load all grape varieties that are available from producers."""
        producer_file = self.data_dir / "05_wine_producers_final_normalized.jsonl"
        
        if not producer_file.exists():
            print(f"⚠️ Producer data not found at {producer_file}")
            return
        
        print("🍷 Loading producer varieties...")
        
        with open(producer_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    producer = json.loads(line.strip())
                    wines = producer.get('wines', [])
                    
                    for wine in wines:
                        cepages = wine.get('cepages', [])
                        if cepages:  # Only include wines with specified grape varieties
                            for cepage in cepages:
                                if cepage:  # Skip empty/null cepages
                                    self.producer_varieties.add(cepage)
                
                except json.JSONDecodeError:
                    continue
        
        print(f"📊 Found {len(self.producer_varieties)} unique varieties from producers")
    
    def _extract_portfolio_data(self, portfolio: dict) -> Dict[str, Any]:
        """Extract relevant data from portfolio for tree display."""
        if not portfolio:
            return {}
        
        data = {}
        
        # Berry color
        if portfolio.get('berry_skin_color'):
            data['berry_color'] = portfolio['berry_skin_color'].lower()
        
        # Country of origin
        if portfolio.get('country_of_origin'):
            data['country'] = portfolio['country_of_origin']
        
        # Species
        if portfolio.get('species'):
            data['species'] = portfolio['species']
        
        # Sex of flower
        if portfolio.get('sex_of_flower'):
            data['sex'] = portfolio['sex_of_flower']
        
        # Year of crossing
        if portfolio.get('year_of_crossing'):
            data['year_crossing'] = portfolio['year_of_crossing']
        
        # Breeder information
        if portfolio.get('breeder'):
            data['breeder'] = portfolio['breeder']
        
        # VIVC number
        grape_info = portfolio.get('grape', {})
        if isinstance(grape_info, dict) and grape_info.get('vivc_number'):
            data['vivc_number'] = grape_info['vivc_number']
        
        return data
    
    def _find_variety_by_vivc_id(self, vivc_id: str) -> Optional[str]:
        """Find variety name by VIVC ID from portfolio data."""
        if not vivc_id:
            return None
        
        all_varieties = self.varieties_model.get_all_varieties()
        for variety in all_varieties:
            if variety.portfolio and isinstance(variety.portfolio, dict):
                grape_info = variety.portfolio.get('grape', {})
                if isinstance(grape_info, dict) and grape_info.get('vivc_number') == vivc_id:
                    return variety.name
        return None
    
    def build_tree_for_variety(self, variety_name: str, max_depth: int = 10) -> Optional[TreeNode]:
        """Build a complete tree for a specific variety."""
        if max_depth <= 0:
            return None
        
        variety = self.varieties_model.get_variety(variety_name)
        if not variety or not variety.grape:
            # Try case-insensitive lookup
            for existing_name in self.varieties_model.varieties.keys():
                if existing_name.lower() == variety_name.lower():
                    variety = self.varieties_model.get_variety(existing_name)
                    variety_name = existing_name  # Use the correct casing
                    break
            
            if not variety or not variety.grape:
                return None
        
        # Check if we already processed this variety (deduplication)
        if variety_name in self.processed_varieties:
            if variety_name in self.variety_nodes:
                # Return a duplicate reference
                return TreeNode(
                    name=variety_name,
                    is_duplicate=True,
                    original_reference=variety_name
                )
            return None
        
        # Mark as processed
        self.processed_varieties.add(variety_name)
        
        # Extract portfolio data
        portfolio_data = self._extract_portfolio_data(variety.portfolio or {})
        
        # Create the node
        node = TreeNode(
            name=variety_name,
            vivc_number=portfolio_data.get('vivc_number'),
            berry_color=portfolio_data.get('berry_color'),
            country=portfolio_data.get('country'),
            species=portfolio_data.get('species'),
            sex=portfolio_data.get('sex'),
            breeder=portfolio_data.get('breeder'),
            year_crossing=portfolio_data.get('year_crossing')
        )
        
        # Store in our cache
        self.variety_nodes[variety_name] = node
        
        # Build parent trees if portfolio data exists
        if variety.portfolio and isinstance(variety.portfolio, dict):
            # Parent 1
            parent1_data = variety.portfolio.get('parent1')
            if parent1_data and isinstance(parent1_data, dict):
                parent1_vivc = parent1_data.get('vivc_number')
                parent1_name = parent1_data.get('name')
                if parent1_vivc and parent1_name and parent1_name not in ['UNKNOWN', 'UNKNOWN (SPONTANEOUS HYBRIDIZATION)']:
                    parent1_variety_name = self._find_variety_by_vivc_id(parent1_vivc)
                    if parent1_variety_name:
                        node.parent1 = self.build_tree_for_variety(parent1_variety_name, max_depth - 1)
            
            # Parent 2
            parent2_data = variety.portfolio.get('parent2')
            if parent2_data and isinstance(parent2_data, dict):
                parent2_vivc = parent2_data.get('vivc_number')
                parent2_name = parent2_data.get('name')
                if parent2_vivc and parent2_name and parent2_name not in ['UNKNOWN', 'UNKNOWN (SPONTANEOUS HYBRIDIZATION)']:
                    parent2_variety_name = self._find_variety_by_vivc_id(parent2_vivc)
                    if parent2_variety_name:
                        node.parent2 = self.build_tree_for_variety(parent2_variety_name, max_depth - 1)
        
        return node
    
    def get_all_grape_varieties(self) -> List[str]:
        """Get list of grape varieties for the dropdown (excluding varieties not used for wine)."""
        all_varieties = self.varieties_model.get_grape_varieties()
        # Filter out varieties with no_wine=1 (parent varieties not used for actual wine production)
        wine_varieties = [v for v in all_varieties if v.no_wine != 1]
        return sorted([v.name for v in wine_varieties])
    
    def convert_tree_to_react_flow_format(self, root_node: TreeNode, selected_variety: str, duplicate_parents: bool = False) -> Dict[str, Any]:
        """Convert tree structure to React Flow format with nodes and edges."""
        if duplicate_parents:
            return self._convert_tree_with_duplicated_parents(root_node, selected_variety)
        else:
            return self._convert_tree_with_merged_parents(root_node, selected_variety)
    
    def _convert_tree_with_merged_parents(self, root_node: TreeNode, selected_variety: str) -> Dict[str, Any]:
        """Convert tree with merged parent nodes (default behavior)."""
        # First pass: collect all nodes and their relationships
        all_nodes = {}
        edges = []
        
        def collect_nodes(node: TreeNode):
            if not node or node.name in all_nodes:
                return
            
            all_nodes[node.name] = node
            
            # Collect parent relationships and create edges
            if node.parent1:
                collect_nodes(node.parent1)
                edges.append({
                    'id': f"{node.parent1.name}->{node.name}",
                    'source': node.parent1.name,
                    'target': node.name,
                    'type': 'default'
                })
            
            if node.parent2:
                collect_nodes(node.parent2)
                edges.append({
                    'id': f"{node.parent2.name}->{node.name}",
                    'source': node.parent2.name,
                    'target': node.name,
                    'type': 'default'
                })
        
        # Collect all nodes and edges
        collect_nodes(root_node)
        
        # Second pass: calculate hierarchical levels
        node_levels = self._calculate_hierarchical_levels(all_nodes, edges, selected_variety)
        
        # Third pass: create React Flow nodes
        nodes = []
        for node_name, node in all_nodes.items():
            # Determine node styling based on properties
            is_selected = node_name == selected_variety
            is_duplicate = node.is_duplicate
            
            # Create React Flow node
            react_flow_node = {
                'id': node_name,
                'type': 'grapeNode',  # Custom node type
                'position': {'x': node_levels[node_name] * 300, 'y': 0},  # Will be auto-layouted
                'data': {
                    'label': node_name,
                    'vivc_number': node.vivc_number,
                    'berry_color': node.berry_color,
                    'country': node.country,
                    'country_code': self.COUNTRY_FLAGS.get(node.country.upper() if node.country else '', ''),
                    'species': node.species,
                    'sex': node.sex,
                    'breeder': node.breeder,
                    'year_crossing': node.year_crossing,
                    'is_selected': is_selected,
                    'is_duplicate': is_duplicate,
                    'level': node_levels[node_name]
                }
            }
            
            nodes.append(react_flow_node)
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def _convert_tree_with_duplicated_parents(self, root_node: TreeNode, selected_variety: str) -> Dict[str, Any]:
        """Convert tree with duplicated parent trees for crossing visualization."""
        all_nodes = {}
        edges = []
        node_counter = {}  # Track duplicates
        
        def get_unique_node_id(node_name: str) -> str:
            """Get a unique ID for potentially duplicated nodes."""
            if node_name not in node_counter:
                node_counter[node_name] = 0
                return node_name
            else:
                node_counter[node_name] += 1
                return f"{node_name}#{node_counter[node_name]}"
        
        def collect_nodes_with_duplication(node: TreeNode, path: str = "") -> str:
            """Collect nodes allowing duplication for each reference."""
            if not node:
                return None
            
            # Create unique ID for this instance
            unique_id = get_unique_node_id(node.name)
            
            # Store node data
            all_nodes[unique_id] = node
            
            # Process parents recursively
            parent1_id = None
            parent2_id = None
            
            if node.parent1:
                parent1_id = collect_nodes_with_duplication(node.parent1, f"{path}/p1")
                if parent1_id:
                    edges.append({
                        'id': f"{parent1_id}->{unique_id}",
                        'source': parent1_id,
                        'target': unique_id,
                        'type': 'default'
                    })
            
            if node.parent2:
                parent2_id = collect_nodes_with_duplication(node.parent2, f"{path}/p2")
                if parent2_id:
                    edges.append({
                        'id': f"{parent2_id}->{unique_id}",
                        'source': parent2_id,
                        'target': unique_id,
                        'type': 'default'
                    })
            
            return unique_id
        
        # Collect all nodes with duplication
        collect_nodes_with_duplication(root_node)
        
        # Calculate levels for duplicated tree
        node_levels = self._calculate_hierarchical_levels_with_duplicates(all_nodes, edges, selected_variety)
        
        # Create React Flow nodes
        nodes = []
        for unique_id, node in all_nodes.items():
            # Extract original name (remove #N suffix)
            original_name = unique_id.split('#')[0]
            is_selected = original_name == selected_variety and '#' not in unique_id
            is_duplicate = '#' in unique_id
            
            react_flow_node = {
                'id': unique_id,
                'type': 'grapeNode',
                'position': {'x': node_levels.get(unique_id, 0) * 300, 'y': 0},
                'data': {
                    'label': original_name,
                    'vivc_number': node.vivc_number,
                    'berry_color': node.berry_color,
                    'country': node.country,
                    'country_code': self.COUNTRY_FLAGS.get(node.country.upper() if node.country else '', ''),
                    'species': node.species,
                    'sex': node.sex,
                    'breeder': node.breeder,
                    'year_crossing': node.year_crossing,
                    'is_selected': is_selected,
                    'is_duplicate': is_duplicate,
                    'level': node_levels.get(unique_id, 0)
                }
            }
            
            nodes.append(react_flow_node)
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def _calculate_hierarchical_levels_with_duplicates(self, all_nodes: Dict[str, TreeNode], edges: List[Dict], selected_variety: str) -> Dict[str, int]:
        """Calculate levels for duplicated tree structure."""
        from collections import defaultdict
        
        # Build adjacency lists
        children_of = defaultdict(list)
        parents_of = defaultdict(list)
        
        # Build the graph from edges
        for edge in edges:
            parent = edge['source']
            child = edge['target']
            children_of[parent].append(child)
            parents_of[child].append(parent)
        
        # Initialize all nodes
        levels = {}
        for node_id in all_nodes.keys():
            levels[node_id] = 0
        
        # Start with selected variety at level 0 (leftmost)
        levels[selected_variety] = 0
        
        # Calculate levels top-down
        changed = True
        max_iterations = 20
        iteration = 0
        
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            
            # For each node, compute parent levels based on child levels
            for node_id in list(levels.keys()):
                if node_id in parents_of and parents_of[node_id]:
                    parents = parents_of[node_id]
                    current_level = levels[node_id]
                    required_parent_level = current_level + 1
                    
                    for parent in parents:
                        if levels[parent] < required_parent_level:
                            levels[parent] = required_parent_level
                            changed = True
        
        return levels
    
    def _calculate_hierarchical_levels(self, all_nodes: Dict[str, TreeNode], edges: List[Dict], selected_variety: str) -> Dict[str, int]:
        """Calculate genealogical levels where selected variety is leftmost (0) and parents are to the right."""
        from collections import defaultdict
        
        # Build adjacency lists
        children_of = defaultdict(list)  # parent -> [children]
        parents_of = defaultdict(list)   # child -> [parents]
        
        # Build the graph from edges
        for edge in edges:
            parent = edge['source']
            child = edge['target']
            children_of[parent].append(child)
            parents_of[child].append(parent)
        
        # Initialize all nodes
        levels = {}
        for node_name in all_nodes.keys():
            levels[node_name] = 0
        
        # Start with selected variety at level 0 (leftmost)
        levels[selected_variety] = 0
        
        # Use topological sorting approach: compute levels top-down
        # Rule: parent_level = child_level + 1 (parents go to the right)
        changed = True
        max_iterations = 20
        iteration = 0
        
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            
            # For each node, compute parent levels based on child levels
            for node_name in list(levels.keys()):
                if node_name in parents_of and parents_of[node_name]:
                    # This node has parents - move parents to the right
                    parents = parents_of[node_name]
                    current_level = levels[node_name]
                    required_parent_level = current_level + 1
                    
                    # Move parents to the right if needed
                    for parent in parents:
                        if levels[parent] < required_parent_level:
                            levels[parent] = required_parent_level
                            changed = True
        
        return levels
    
    def generate_tree_data(self) -> Dict[str, Any]:
        """Generate unified tree data for all grape varieties."""
        print("🌳 Building unified tree data for all grape varieties...")
        
        grape_varieties = self.get_all_grape_varieties()
        all_nodes = {}
        all_edges = []
        
        # Build one big graph with all varieties and their relationships
        for i, variety_name in enumerate(grape_varieties, 1):
            print(f"[{i}/{len(grape_varieties)}] Processing: {variety_name}")
            
            # Reset processed varieties for each new root
            self.processed_varieties.clear()
            self.variety_nodes.clear()
            
            tree = self.build_tree_for_variety(variety_name)
            if tree:
                # Collect all nodes from this tree
                self._collect_all_nodes_and_edges(tree, all_nodes, all_edges)
        
        # Convert to React Flow format
        unified_nodes = []
        for node_name, node in all_nodes.items():
            react_flow_node = {
                'id': node_name,
                'type': 'grapeNode',
                'position': {'x': 0, 'y': 0},  # Will be positioned by client
                'data': {
                    'label': node_name,
                    'vivc_number': node.vivc_number,
                    'berry_color': node.berry_color,
                    'country': node.country,
                    'country_code': self.COUNTRY_FLAGS.get(node.country.upper() if node.country else '', ''),
                    'species': node.species,
                    'sex': node.sex,
                    'breeder': node.breeder,
                    'year_crossing': node.year_crossing,
                    'has_producers': node_name in self.producer_varieties,  # Check if variety is available from producers
                    'is_selected': False,  # Will be set by client
                    'is_duplicate': False  # Will be set by client
                }
            }
            unified_nodes.append(react_flow_node)
        
        # Deduplicate edges
        unique_edges = []
        edge_set = set()
        for edge in all_edges:
            edge_key = f"{edge['source']}->{edge['target']}"
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                unique_edges.append(edge)
        
        print(f"📊 Generated unified graph: {len(unified_nodes)} nodes, {len(unique_edges)} edges")
        
        return {
            'varieties': grape_varieties,
            'nodes': unified_nodes,
            'edges': unique_edges,
            'country_flags': self.COUNTRY_FLAGS
        }
    
    def _collect_all_nodes_and_edges(self, node: TreeNode, all_nodes: dict, all_edges: list):
        """Recursively collect all nodes and edges from a tree."""
        if not node or node.name in all_nodes:
            return
        
        # Add node to collection
        all_nodes[node.name] = node
        
        # Process parents and create edges
        if node.parent1:
            self._collect_all_nodes_and_edges(node.parent1, all_nodes, all_edges)
            all_edges.append({
                'id': f"{node.parent1.name}->{node.name}",
                'source': node.parent1.name,
                'target': node.name,
                'type': 'default'
            })
        
        if node.parent2:
            self._collect_all_nodes_and_edges(node.parent2, all_nodes, all_edges)
            all_edges.append({
                'id': f"{node.parent2.name}->{node.name}",
                'source': node.parent2.name,
                'target': node.name,
                'type': 'default'
            })
    
    def generate_data_file(self, output_path: str = "grapegeek-nextjs/public/data/tree-data.json"):
        """Generate the JSON data file for React Flow."""
        print("🔧 Generating tree data...")
        tree_data = self.generate_tree_data()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Writing JSON data to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tree_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Tree data generated: {output_file}")
        print(f"📊 Generated unified graph: {len(tree_data['nodes'])} nodes, {len(tree_data['edges'])} edges")
        
        return output_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate grape variety tree data for React Flow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/18_generate_tree_data.py                           # Generate to grapegeek-nextjs/public/data/tree-data.json
  python src/18_generate_tree_data.py --output custom.json     # Custom output path
        """
    )

    parser.add_argument(
        "--output",
        default="grapegeek-nextjs/public/data/tree-data.json",
        help="Output JSON file path (default: grapegeek-nextjs/public/data/tree-data.json)"
    )
    
    args = parser.parse_args()
    
    try:
        generator = TreeDataGenerator()
        output_file = generator.generate_data_file(args.output)
        
        print(f"\n📁 Data file ready for React Flow:")
        print(f"{output_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()