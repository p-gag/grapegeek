#!/usr/bin/env python3
"""
Grape Variety Tree Viewer Generator

Generates a static HTML page for browsing grape variety family trees.
Uses Vis.js Network for professional graph layout and visualization.

PURPOSE: Tree Visualization - Generate interactive HTML tree viewer

INPUTS:
- data/grape_variety_mapping.jsonl (via GrapeVarietiesModel)

OUTPUTS:
- docs/grape-tree-viewer.html (static HTML with embedded data)

USAGE:
# Generate tree viewer HTML
uv run src/17_generate_tree_viewer.py

# Output to specific location
uv run src/17_generate_tree_viewer.py --output custom_path.html
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


class TreeViewerGenerator:
    """Generates HTML tree viewer for grape varieties using Vis.js."""
    
    # Color constants for species backgrounds (improved contrast)
    SPECIES_COLORS = {
        'vinifera': 'rgba(144, 238, 144, 0.85)',  # Light green - European wine grapes
        'riparia': 'rgba(135, 206, 235, 0.85)',   # Sky blue - Cold-hardy native
        'labrusca': 'rgba(186, 85, 211, 0.85)',   # Medium orchid
        'rupestris': 'rgba(255, 160, 122, 0.85)', # Light salmon - Rock grapes
        'aestivalis': 'rgba(255, 255, 0, 0.85)',  # Yellow - Summer grapes
        'amurensis': 'rgba(255, 20, 147, 0.85)',  # Deep pink - Asian cold-hardy
        'rotundifolia': 'rgba(147, 112, 219, 0.85)', # Medium slate blue - Muscadine grapes
        'hybrid': 'rgba(230, 230, 230, 0.75)',    # Pale silver - VITIS INTERSPECIFIC crosses
        'unknown': 'rgba(255, 99, 71, 0.85)'      # Tomato - Unknown/unspecified
    }
    
    # Consolidated country flag mapping
    COUNTRY_FLAGS = {
        'CANADA': '🇨🇦',
        'USA': '🇺🇸',
        'UNITED STATES': '🇺🇸',
        'UNITED STATES OF AMERICA': '🇺🇸',
        'US': '🇺🇸',
        'FRANCE': '🇫🇷',
        'GERMANY': '🇩🇪',
        'DEUTSCHE': '🇩🇪',
        'ITALY': '🇮🇹',
        'ITALIA': '🇮🇹',
        'SPAIN': '🇪🇸',
        'ESPAÑA': '🇪🇸',
        'PORTUGAL': '🇵🇹',
        'AUSTRIA': '🇦🇹',
        'SWITZERLAND': '🇨🇭',
        'SUISSE': '🇨🇭',
        'HUNGARY': '🇭🇺',
        'ROMANIA': '🇷🇴',
        'BULGARIA': '🇧🇬',
        'GREECE': '🇬🇷',
        'TURKEY': '🇹🇷',
        'GEORGIA': '🇬🇪',
        'MOLDOVA': '🇲🇩',
        'UKRAINE': '🇺🇦',
        'RUSSIA': '🇷🇺',
        'RUSSIAN FEDERATION': '🇷🇺',
        'KAZAKHSTAN': '🇰🇿',
        'UZBEKISTAN': '🇺🇿',
        'ARMENIA': '🇦🇲',
        'AZERBAIJAN': '🇦🇿',
        'CROATIA': '🇭🇷',
        'SLOVENIA': '🇸🇮',
        'SERBIA': '🇷🇸',
        'MONTENEGRO': '🇲🇪',
        'BOSNIA AND HERZEGOVINA': '🇧🇦',
        'NORTH MACEDONIA': '🇲🇰',
        'ALBANIA': '🇦🇱',
        'CYPRUS': '🇨🇾',
        'ISRAEL': '🇮🇱',
        'LEBANON': '🇱🇧',
        'SYRIA': '🇸🇾',
        'EUROPE': '🇪🇺',
        'ALGERIA': '🇩🇿',
        'MOROCCO': '🇲🇦',
        'TUNISIA': '🇹🇳',
        'EGYPT': '🇪🇬',
        'CHINA': '🇨🇳',
        'JAPAN': '🇯🇵',
        'SOUTH KOREA': '🇰🇷',
        'AUSTRALIA': '🇦🇺',
        'NEW ZEALAND': '🇳🇿',
        'SOUTH AFRICA': '🇿🇦',
        'CHILE': '🇨🇱',
        'ARGENTINA': '🇦🇷',
        'BRAZIL': '🇧🇷',
        'URUGUAY': '🇺🇾',
        'PERU': '🇵🇪',
        'COLOMBIA': '🇨🇴',
        'VENEZUELA': '🇻🇪',
        'UNITED KINGDOM': '🇬🇧',
        'GREAT BRITAIN': '🇬🇧',
        'ENGLAND': '🇬🇧',
        'SCOTLAND': '🇬🇧',
        'WALES': '🇬🇧',
        'IRELAND': '🇮🇪',
        'NETHERLANDS': '🇳🇱',
        'BELGIUM': '🇧🇪',
        'DENMARK': '🇩🇰',
        'SWEDEN': '🇸🇪',
        'NORWAY': '🇳🇴',
        'FINLAND': '🇫🇮',
        'POLAND': '🇵🇱',
        'CZECH REPUBLIC': '🇨🇿',
        'SLOVAKIA': '🇸🇰',
        'LITHUANIA': '🇱🇹',
        'LATVIA': '🇱🇻',
        'ESTONIA': '🇪🇪'
    }
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.varieties_model = GrapeVarietiesModel(data_dir)
        self.processed_varieties: Set[str] = set()
        self.variety_nodes: Dict[str, TreeNode] = {}
    
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
    
    def convert_tree_to_vis_network(self, root_node: TreeNode, selected_variety: str) -> Dict[str, Any]:
        """Convert tree structure to Vis.js network format with proper hierarchical levels."""
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
                    'from': node.parent1.name,
                    'to': node.name,
                    'arrows': 'to',
                    'color': {'color': '#999'}
                })
            
            if node.parent2:
                collect_nodes(node.parent2)
                edges.append({
                    'from': node.parent2.name,
                    'to': node.name,
                    'arrows': 'to',
                    'color': {'color': '#999'}
                })
        
        # Collect all nodes and edges
        collect_nodes(root_node)
        
        # Second pass: calculate proper levels using topological sorting
        node_levels = self._calculate_hierarchical_levels(all_nodes, edges, selected_variety)
        
        # Third pass: create vis.js nodes with proper levels
        nodes = []
        for node_name, node in all_nodes.items():
            # Determine node styling based on properties
            is_selected = node_name == selected_variety
            is_duplicate = node.is_duplicate
            
            # Base node properties  
            # Use simple label for all nodes
            label = node_name
            
            vis_node = {
                'id': node_name,
                'label': label,
                'level': node_levels[node_name],
                'title': self._create_node_tooltip(node),
                'font': {'size': 32 if not is_selected else 32, 'color': '#333'},
                'country': node.country or '',
                'sex': node.sex or '',
                'species': node.species or '',
                'berryColor': node.berry_color or '',
                'baseName': node_name
            }
            
            # Node styling
            if is_selected:
                vis_node.update({
                    'color': {'background': 'rgba(0, 123, 255, 0.85)', 'border': '#0056b3'},
                    'font': {'color': 'white', 'size': 32, 'bold': True}
                })
            elif is_duplicate:
                vis_node.update({
                    'color': {'background': 'rgba(255, 243, 205, 0.85)', 'border': '#ffeaa7'},
                    'borderDashes': [5, 5],
                    'font': {'color': '#856404', 'size': 32}
                })
            else:
                # Color by berry color (species coloring will be toggled via JavaScript)
                bg_color = self._get_node_background_color_with_transparency(node)
                vis_node.update({
                    'color': {'background': bg_color, 'border': 'rgba(222, 226, 230, 0.85)'},
                    'font': {'color': '#333', 'size': 32}
                })
            
            nodes.append(vis_node)
        
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def _calculate_hierarchical_levels(self, all_nodes: Dict[str, TreeNode], edges: List[Dict], selected_variety: str) -> Dict[str, int]:
        """Calculate genealogical levels where each parent's level = max(children's levels) + 1."""
        from collections import defaultdict
        
        # Build adjacency lists
        children_of = defaultdict(list)  # parent -> [children]
        parents_of = defaultdict(list)   # child -> [parents]
        
        # Build the graph from edges
        for edge in edges:
            parent = edge['from']
            child = edge['to']
            children_of[parent].append(child)
            parents_of[child].append(parent)
        
        # Initialize all nodes
        levels = {}
        for node_name in all_nodes.keys():
            levels[node_name] = 0
        
        # Start with selected variety at level 0
        levels[selected_variety] = 0
        
        # Use topological sorting approach: compute levels bottom-up
        # Rule: parent_level = max(all_children_levels) + 1
        changed = True
        max_iterations = 20
        iteration = 0
        
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            
            # For each node, compute its level based on its children
            for node_name in list(levels.keys()):
                if node_name in children_of and children_of[node_name]:
                    # This node has children - its level should be max(children_levels) + 1
                    children = children_of[node_name]
                    max_child_level = max(levels.get(child, 0) for child in children)
                    required_level = max_child_level + 1
                    
                    if levels[node_name] < required_level:
                        levels[node_name] = required_level
                        changed = True
        
        # Second pass: ensure selected variety stays at level 0 and adjust everything relative to it
        # Find the path from selected variety to the root ancestors
        selected_level = levels[selected_variety]
        
        # Adjust all levels so selected variety is at 0
        for node_name in levels:
            levels[node_name] -= selected_level
        
        # Third pass: ensure no negative levels (move everything up if needed)
        if levels:
            min_level = min(levels.values())
            if min_level < 0:
                for node in levels:
                    levels[node] -= min_level
        
        # No reversal needed - vis.js will correctly place:
        # - Selected variety (level 0) on the left
        # - Parents (higher levels) further to the right
        
        return levels
    
    def _create_node_tooltip(self, node: TreeNode) -> str:
        """Create tooltip content for a node."""
        tooltip_parts = [f"<b>{node.name}</b>"]
        
        if node.vivc_number:
            tooltip_parts.append(f"VIVC: {node.vivc_number}")
        
        if node.species:
            tooltip_parts.append(f"Species: {node.species}")
        
        if node.berry_color:
            color_emoji = self._get_berry_color_emoji(node.berry_color)
            tooltip_parts.append(f"Berry: {color_emoji} {node.berry_color}")
            
        if node.country:
            flag = self._get_country_flag_emoji(node.country)
            tooltip_parts.append(f"Origin: {flag} {node.country}")
            
        if node.sex:
            sex_symbol = self._get_sex_symbol(node.sex)
            tooltip_parts.append(f"Sex: {sex_symbol} {node.sex}")
            
        if node.year_crossing:
            tooltip_parts.append(f"Year: {node.year_crossing}")
            
        if node.breeder:
            tooltip_parts.append(f"Breeder: {node.breeder}")
            
        # Add parent information if available
        parent_info = []
        if node.parent1:
            parent_info.append(node.parent1.name)
        if node.parent2:
            parent_info.append(node.parent2.name)
        if parent_info:
            tooltip_parts.append(f"Parents: {' × '.join(parent_info)}")
            
        return "<br>".join(tooltip_parts)
    
    def _get_node_background_color(self, node: TreeNode) -> str:
        """Get background color for node based on berry color."""
        if not node.berry_color:
            return '#f8f9fa'
            
        color_lower = node.berry_color.lower()
        if 'blanc' in color_lower or 'white' in color_lower:
            return '#f0f8ff'  # Alice blue
        elif 'rouge' in color_lower or 'red' in color_lower or 'noir' in color_lower or 'black' in color_lower:
            return '#ffe4e1'  # Misty rose
        elif 'rose' in color_lower or 'pink' in color_lower:
            return '#ffeef0'  # Light pink
        elif 'gris' in color_lower or 'gray' in color_lower:
            return '#f5f5f5'  # White smoke
        else:
            return '#f8f9fa'  # Light gray
    
    def _get_node_background_color_with_transparency(self, node: TreeNode) -> str:
        """Get background color for node with transparency based on berry color."""
        if not node.berry_color:
            return 'rgba(248, 249, 250, 0.85)'  # Light gray with transparency
            
        color_lower = node.berry_color.lower()
        if 'blanc' in color_lower or 'white' in color_lower:
            return 'rgba(240, 248, 255, 0.85)'  # Alice blue with transparency
        elif 'rouge' in color_lower or 'red' in color_lower or 'noir' in color_lower or 'black' in color_lower:
            return 'rgba(255, 228, 225, 0.85)'  # Misty rose with transparency
        elif 'rose' in color_lower or 'pink' in color_lower:
            return 'rgba(255, 238, 240, 0.85)'  # Light pink with transparency
        elif 'gris' in color_lower or 'gray' in color_lower:
            return 'rgba(245, 245, 245, 0.85)'  # White smoke with transparency
        else:
            return 'rgba(248, 249, 250, 0.85)'  # Light gray with transparency
    
    def _get_species_background_color(self, species: str) -> str:
        """Get background color for node based on species."""
        if not species:
            return self.SPECIES_COLORS['hybrid']  # Empty species -> Vitis interspecific
            
        species_lower = species.lower()
        
        # Vitis vinifera (European wine grapes)
        if 'vinifera' in species_lower:
            return self.SPECIES_COLORS['vinifera']
        
        # Vitis riparia (Native American cold-hardy)  
        elif 'riparia' in species_lower:
            return self.SPECIES_COLORS['riparia']
        
        # Vitis labrusca (Native American grapes)
        elif 'labrusca' in species_lower:
            return self.SPECIES_COLORS['labrusca']
        
        # Vitis rupestris (Native American rock grapes)
        elif 'rupestris' in species_lower:
            return self.SPECIES_COLORS['rupestris']
        
        # Vitis aestivalis (Native American summer grapes)
        elif 'aestivalis' in species_lower or 'lincecumii' in species_lower:
            return self.SPECIES_COLORS['aestivalis']
        
        # Vitis amurensis (Asian cold-hardy)
        elif 'amurensis' in species_lower:
            return self.SPECIES_COLORS['amurensis']
        
        # Vitis rotundifolia / Muscadinia rotundifolia (Muscadine grapes)
        elif 'rotundifolia' in species_lower or 'muscadinia' in species_lower:
            return self.SPECIES_COLORS['rotundifolia']
        
        # Hybrids (INTERSPECIFIC and INTERGENERIC crosses)
        elif 'interspecific' in species_lower or 'intergeneric' in species_lower:
            return self.SPECIES_COLORS['hybrid']
        
        # Unknown species
        else:
            return self.SPECIES_COLORS['unknown']
    
    def _get_country_flag_emoji(self, country: str) -> str:
        """Get flag emoji for country."""
        return self.COUNTRY_FLAGS.get(country.upper(), '🏁')
    
    def _get_berry_color_emoji(self, color: str) -> str:
        """Get emoji for berry color."""
        if not color:
            return ''
        
        color_lower = color.lower()
        if 'red' in color_lower or 'rouge' in color_lower:
            return '🔴'
        elif 'black' in color_lower or 'noir' in color_lower or 'dark' in color_lower:
            return '⚫'
        elif 'white' in color_lower or 'blanc' in color_lower or 'weiss' in color_lower:
            return '⚪'
        elif 'rose' in color_lower or 'pink' in color_lower or 'gris' in color_lower:
            return '🟣'
        elif 'blue' in color_lower or 'bleu' in color_lower:
            return '🔵'
        elif 'green' in color_lower or 'vert' in color_lower:
            return '🟢'
        elif 'yellow' in color_lower or 'jaune' in color_lower:
            return '🟡'
        else:
            return '🟫'  # Brown for unknown colors
    
    def _get_sex_symbol(self, sex: str) -> str:
        """Get symbol for sex of flower."""
        if not sex:
            return ''
        
        sex_lower = sex.lower()
        if 'male' in sex_lower and 'female' not in sex_lower:
            return '♂'
        elif 'female' in sex_lower:
            return '♀'
        elif 'hermaphrodite' in sex_lower:
            return '⚥'
        else:
            return '❓'
    
    def generate_tree_data(self) -> Dict[str, Any]:
        """Generate tree data for all grape varieties."""
        print("🌳 Building tree data for all grape varieties...")
        
        grape_varieties = self.get_all_grape_varieties()
        vis_networks = {}
        
        for i, variety_name in enumerate(grape_varieties, 1):
            print(f"[{i}/{len(grape_varieties)}] Processing: {variety_name}")
            
            # Reset processed varieties for each new root
            self.processed_varieties.clear()
            self.variety_nodes.clear()
            
            tree = self.build_tree_for_variety(variety_name)
            if tree:
                network_data = self.convert_tree_to_vis_network(tree, variety_name)
                vis_networks[variety_name] = network_data
        
        return {
            'varieties': grape_varieties,
            'networks': vis_networks,
        }
    
    def _get_country_flags_json(self) -> str:
        """Convert COUNTRY_FLAGS dict to JSON string for JavaScript."""
        import json
        return json.dumps(self.COUNTRY_FLAGS, indent=20, ensure_ascii=False)

    def generate_html_template(self, tree_data: Dict[str, Any]) -> str:
        """Generate the complete HTML template with embedded data."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grape Variety Family Tree Viewer</title>
    <script src="https://unpkg.com/vis-network@9.1.6/dist/vis-network.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            height: 100vh;
            overflow: hidden;
            display: flex;
            position: relative;
        }}
        
        .sidebar {{
            width: 300px;
            background: white;
            padding: 20px;
            box-shadow: 2px 0 4px rgba(0,0,0,0.1);
            overflow-y: auto;
            flex-shrink: 0;
        }}
        
        .controls {{
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .variety-selector {{
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            width: 100%;
        }}
        
        .display-options {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .toggle {{
            padding: 6px 12px;
            background: #e9ecef;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s;
        }}
        
        .toggle.active {{
            background: #007bff;
            color: white;
        }}
        
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 10px;
        }}
        
        .network-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 0;
            height: 100%;
            flex: 1;
        }}
        
        #network {{
            width: 100%;
            height: 100%;
            border-radius: 8px;
        }}
        
        .no-data {{
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 40px;
            height: 600px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .custom-tooltip {{
            position: absolute;
            background: rgba(255, 255, 255, 0.95);
            border: 2px solid #767676;
            border-radius: 6px;
            padding: 12px;
            font-size: 14px;
            font-family: Arial, sans-serif;
            color: #333;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            max-width: 300px;
            white-space: pre-line;
            display: none;
            pointer-events: auto;
        }}
        
        .custom-tooltip .tooltip-title {{
            font-weight: bold;
            margin-bottom: 8px;
            color: #007bff;
            font-size: 16px;
        }}
        
        .custom-tooltip .tooltip-content {{
            line-height: 1.4;
        }}
        
        .stats {{
            margin-top: 10px;
            font-size: 14px;
            color: #666;
        }}
        
        .instructions {{
            margin-top: 10px;
            font-size: 13px;
            color: #888;
        }}
        
        .species-legend {{
            margin-top: 15px;
            padding: 12px;
            background: rgba(248, 249, 250, 0.9);
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 12px;
        }}
        
        .species-legend h4 {{
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #333;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 4px;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            margin-right: 8px;
            border: 1px solid #ccc;
            flex-shrink: 0;
        }}
        
        
        @media (max-width: 768px) {{
            body {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                height: auto;
                flex-shrink: 1;
            }}
            
            .controls {{
                flex-direction: row;
                flex-wrap: wrap;
            }}
            
            .display-options {{
                flex-direction: row;
                flex-wrap: wrap;
            }}
            
            .main-content {{
                padding: 5px;
            }}
        }}
        
        /* Custom styling for selected node subtitles */
        .vis-network svg text {{
            font-size: inherit !important;
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h1>🍇 Grape Family Trees</h1>
        
        <div class="controls">
            <select id="varietySelector" class="variety-selector">
                <option value="">Select a grape variety...</option>
            </select>
            
            <div class="display-options">
                <button id="toggleFlags" class="toggle">🏁 Country Flags</button>
                <button id="toggleSex" class="toggle">⚥ Sex Info</button>
                <button id="toggleColors" class="toggle">🍇 Berry Colors</button>
                <button id="resetView" class="toggle">🎯 Reset View</button>
            </div>
        </div>
        
        <div class="stats" id="statsContainer"></div>
        
        <!-- Berry Colors Legend (shown by default) -->
        <div id="berriesLegend" class="species-legend" style="display: block;">
            <h4>🍇 Berry Colors</h4>
            <div class="legend-item"><span class="legend-color" style="background: rgba(240, 248, 255, 0.85);"></span> White/Blanc grapes</div>
            <div class="legend-item"><span class="legend-color" style="background: rgba(255, 228, 225, 0.85);"></span> Red/Noir grapes</div>
            <div class="legend-item"><span class="legend-color" style="background: rgba(255, 238, 240, 0.85);"></span> Pink/Rose grapes</div>
            <div class="legend-item"><span class="legend-color" style="background: rgba(245, 245, 245, 0.85);"></span> Gray/Gris grapes</div>
            <div class="legend-item"><span class="legend-color" style="background: rgba(248, 249, 250, 0.85);"></span> Unknown berry color</div>
        </div>

        <!-- Species Colors Legend (hidden by default) -->
        <div id="speciesLegend" class="species-legend" style="display: none;">
            <h4>🧬 Species Colors</h4>
            <div class="legend-item"><span class="legend-color" style="background: {self.SPECIES_COLORS['vinifera']};"></span> V. vinifera</div>
            <div class="legend-item"><span class="legend-color" style="background: {self.SPECIES_COLORS['riparia']};"></span> V. riparia</div>
            <div class="legend-item"><span class="legend-color" style="background: {self.SPECIES_COLORS['labrusca']};"></span> V. labrusca</div>
            <div class="legend-item"><span class="legend-color" style="background: {self.SPECIES_COLORS['rupestris']};"></span> V. rupestris</div>
            <div class="legend-item"><span class="legend-color" style="background: {self.SPECIES_COLORS['aestivalis']};"></span> V. aestivalis</div>
            <div class="legend-item"><span class="legend-color" style="background: {self.SPECIES_COLORS['amurensis']};"></span> V. amurensis</div>
            <div class="legend-item"><span class="legend-color" style="background: {self.SPECIES_COLORS['rotundifolia']};"></span> V. rotundifolia (Muscadine)</div>
            <div class="legend-item"><span class="legend-color" style="background: {self.SPECIES_COLORS['hybrid']};"></span> Vitis inter- (Hybrids)</div>
            <div class="legend-item"><span class="legend-color" style="background: {self.SPECIES_COLORS['unknown']};"></span> Unknown species</div>
        </div>
        
        <div class="instructions">
            💡 Click variety for info tooltip | Double-click to explore tree | Drag to pan | Scroll to zoom
        </div>
    </div>
    
    <div class="main-content">
        <div class="network-container">
            <div id="network" class="no-data">
                Select a grape variety to view its family tree
            </div>
        </div>
    </div>
    
    <!-- Custom tooltip -->
    <div id="customTooltip" class="custom-tooltip">
        <div class="tooltip-title"></div>
        <div class="tooltip-content"></div>
    </div>

    <script>
        // Embedded tree data
        const TREE_DATA = {json.dumps(tree_data, indent=2)};
        
        class TreeViewer {{
            constructor() {{
                this.selectedVariety = null;
                this.network = null;
                this.usePhysics = true;
                this.useHierarchical = true;
                this.useLeftToRight = true;
                this.showFlags = true;   // Default enabled
                this.showSex = false;
                this.colorMode = 'species'; // 'berries' or 'species' - default to species
                
                this.initializeUI();
                this.bindEvents();
                this.updateStats();
                this.setupTooltipEvents();
                this.handleUrlParameters();
            }}
            
            initializeUI() {{
                // Populate variety selector
                const selector = document.getElementById('varietySelector');
                TREE_DATA.varieties.forEach(variety => {{
                    const option = document.createElement('option');
                    option.value = variety;
                    option.textContent = variety;
                    selector.appendChild(option);
                }});
                
                // Set initial button states
                document.getElementById('toggleFlags').classList.toggle('active', this.showFlags);
                document.getElementById('toggleSex').classList.toggle('active', this.showSex);
                document.getElementById('toggleColors').classList.add('active'); // Always active now
                
                // Update button text and show appropriate legend based on initial state
                this.updateColorButton();
                this.updateColorLegends();
            }}
            
            bindEvents() {{
                document.getElementById('varietySelector').addEventListener('change', (e) => {{
                    this.selectVariety(e.target.value);
                }});
                
                document.getElementById('toggleFlags').addEventListener('click', () => {{
                    this.toggleFlags();
                }});
                
                document.getElementById('toggleSex').addEventListener('click', () => {{
                    this.toggleSex();
                }});
                
                document.getElementById('toggleColors').addEventListener('click', () => {{
                    this.toggleColors();
                }});
                
                document.getElementById('resetView').addEventListener('click', () => {{
                    this.resetView();
                }});
            }}
            
            toggleFlags() {{
                this.showFlags = !this.showFlags;
                document.getElementById('toggleFlags').classList.toggle('active', this.showFlags);
                
                // Update node labels with new display options
                this.updateNodeLabels();
            }}
            
            toggleSex() {{
                this.showSex = !this.showSex;
                document.getElementById('toggleSex').classList.toggle('active', this.showSex);
                
                // Update node labels with new display options
                this.updateNodeLabels();
            }}
            
            toggleColors() {{
                // Simple toggle between berries and species (always showing colors)
                if (this.colorMode === 'berries') {{
                    this.colorMode = 'species';
                }} else {{
                    this.colorMode = 'berries';
                }}
                
                // Update button text and legends
                this.updateColorButton();
                this.updateColorLegends();
                
                // Update node colors
                this.updateNodeColors();
            }}
            
            updateColorButton() {{
                const button = document.getElementById('toggleColors');
                if (this.colorMode === 'berries') {{
                    button.textContent = '🍇 Berry Colors';
                }} else {{
                    button.textContent = '🧬 Species Colors';
                }}
            }}
            
            updateColorLegends() {{
                const berriesLegend = document.getElementById('berriesLegend');
                const speciesLegend = document.getElementById('speciesLegend');
                
                if (this.colorMode === 'berries') {{
                    berriesLegend.style.display = 'block';
                    speciesLegend.style.display = 'none';
                }} else {{
                    berriesLegend.style.display = 'none';
                    speciesLegend.style.display = 'block';
                }}
            }}
            
            updateNodeLabels() {{
                if (!this.network) return;
                
                const nodes = this.network.body.data.nodes;
                const updates = [];
                
                nodes.forEach(node => {{
                    let label = node.baseName;
                    
                    // Add country flag if enabled
                    if (this.showFlags && node.country) {{
                        const flag = this.getCountryFlag(node.country);
                        label = flag + ' ' + label;
                    }}
                    
                    // Add sex symbol if enabled
                    if (this.showSex && node.sex) {{
                        const sexSymbol = this.getSexSymbol(node.sex);
                        label = label + ' ' + sexSymbol;
                    }}
                    
                    // Preserve all other node properties including title (tooltip)
                    updates.push({{
                        id: node.id,
                        label: label,
                        title: node.title  // Preserve tooltip
                    }});
                }});
                
                // Update the nodes
                this.network.body.data.nodes.update(updates);
            }}
            
            updateNodeColors() {{
                if (!this.network) return;
                
                const nodes = this.network.body.data.nodes;
                const updates = [];
                
                nodes.forEach(node => {{
                    const isSelected = node.id === this.selectedVariety;
                    let backgroundColor;
                    
                    if (this.colorMode === 'berries') {{
                        backgroundColor = this.getBerryColor(node.berryColor || '');
                    }} else {{
                        backgroundColor = this.getSpeciesColor(node.species || '');
                    }}
                    
                    // Preserve selected node styling
                    if (isSelected) {{
                        updates.push({{
                            id: node.id,
                            color: {{
                                background: 'rgba(0, 123, 255, 0.85)',
                                border: '#0056b3'
                            }}
                        }});
                    }} else {{
                        updates.push({{
                            id: node.id,
                            color: {{
                                background: backgroundColor,
                                border: 'rgba(222, 226, 230, 0.85)'
                            }}
                        }});
                    }}
                }});
                
                // Update the nodes
                this.network.body.data.nodes.update(updates);
            }}
            
            getSpeciesColor(species) {{
                if (!species) return '{self.SPECIES_COLORS['hybrid']}';  // Empty species -> Vitis interspecific
                
                const speciesLower = species.toLowerCase();
                
                if (speciesLower.includes('vinifera')) {{
                    return '{self.SPECIES_COLORS['vinifera']}';  // Pale green
                }} else if (speciesLower.includes('riparia')) {{
                    return '{self.SPECIES_COLORS['riparia']}';   // Light blue
                }} else if (speciesLower.includes('labrusca')) {{
                    return '{self.SPECIES_COLORS['labrusca']}';  // Plum
                }} else if (speciesLower.includes('rupestris')) {{
                    return '{self.SPECIES_COLORS['rupestris']}'; // Peach puff
                }} else if (speciesLower.includes('aestivalis') || speciesLower.includes('lincecumii')) {{
                    return '{self.SPECIES_COLORS['aestivalis']}';// Light yellow
                }} else if (speciesLower.includes('amurensis')) {{
                    return '{self.SPECIES_COLORS['amurensis']}'; // Light pink
                }} else if (speciesLower.includes('rotundifolia') || speciesLower.includes('muscadinia')) {{
                    return '{self.SPECIES_COLORS['rotundifolia']}'; // Light purple
                }} else if (speciesLower.includes('interspecific') || speciesLower.includes('intergeneric')) {{
                    return '{self.SPECIES_COLORS['hybrid']}';     // Light grey
                }} else {{
                    return '{self.SPECIES_COLORS['unknown']}';    // Orange
                }}
            }}
            
            getBerryColor(color) {{
                if (!color) return 'rgba(248, 249, 250, 0.85)';
                
                const colorLower = color.toLowerCase();
                if (colorLower.includes('blanc') || colorLower.includes('white')) {{
                    return 'rgba(240, 248, 255, 0.85)';
                }} else if (colorLower.includes('rouge') || colorLower.includes('red') || 
                          colorLower.includes('noir') || colorLower.includes('black')) {{
                    return 'rgba(255, 228, 225, 0.85)';
                }} else if (colorLower.includes('rose') || colorLower.includes('pink')) {{
                    return 'rgba(255, 238, 240, 0.85)';
                }} else if (colorLower.includes('gris') || colorLower.includes('gray')) {{
                    return 'rgba(245, 245, 245, 0.85)';
                }} else {{
                    return 'rgba(248, 249, 250, 0.85)';
                }}
            }}
            
            getCountryFlag(country) {{
                const flags = {self._get_country_flags_json()};
                const result = flags[country.toUpperCase()] || '🏁';
                if (result === '🏁' && country) {{
                    console.log('Unknown country:', country);
                }}
                return result;
            }}
            
            getSexSymbol(sex) {{
                const sexLower = sex.toLowerCase();
                if (sexLower.includes('male') && !sexLower.includes('female')) {{
                    return '♂';
                }} else if (sexLower.includes('female')) {{
                    return '♀';
                }} else if (sexLower.includes('hermaphrodite')) {{
                    return '⚥';
                }} else {{
                    return '❓';
                }}
            }}
            
            showCustomTooltip(position, node) {{
                const tooltip = document.getElementById('customTooltip');
                const titleElement = tooltip.querySelector('.tooltip-title');
                const contentElement = tooltip.querySelector('.tooltip-content');
                
                // Set tooltip content
                titleElement.textContent = node.baseName;
                
                // Create content from the original title (tooltip data)
                let content = node.title || node.baseName;
                // Remove the bold formatting and clean up
                content = content.replace(/<b>.*?<\/b>/g, '').replace(/^<br>/, '');
                
                // Add VIVC link if VIVC number is available
                const vivcMatch = content.match(/VIVC:\s*(\d+)/);
                if (vivcMatch) {{
                    const vivcNumber = vivcMatch[1];
                    const vivcUrl = `https://www.vivc.de/index.php?r=passport%2Fview&id=${{vivcNumber}}`;
                    content = content.replace(
                        `VIVC: ${{vivcNumber}}`,
                        `VIVC: <a href="${{vivcUrl}}" target="_blank" style="color: #007bff; text-decoration: underline;">${{vivcNumber}}</a>`
                    );
                }}
                
                contentElement.innerHTML = content;
                
                // Position tooltip
                tooltip.style.left = (position.x + 10) + 'px';
                tooltip.style.top = (position.y - 10) + 'px';
                tooltip.style.display = 'block';
            }}
            
            hideCustomTooltip() {{
                const tooltip = document.getElementById('customTooltip');
                tooltip.style.display = 'none';
            }}
            
            setupTooltipEvents() {{
                const tooltip = document.getElementById('customTooltip');
                
                // Prevent click events from propagating to the network when clicking on tooltip
                tooltip.addEventListener('click', (event) => {{
                    event.stopPropagation();
                }});
                
                // Hide tooltip when clicking outside the network
                document.addEventListener('click', (event) => {{
                    const networkContainer = document.getElementById('network');
                    
                    if (!networkContainer.contains(event.target) && !tooltip.contains(event.target)) {{
                        this.hideCustomTooltip();
                    }}
                }});
                
                // Handle browser back/forward navigation
                window.addEventListener('popstate', (event) => {{
                    this.handleUrlParameters();
                }});
            }}
            
            handleUrlParameters() {{
                const urlParams = new URLSearchParams(window.location.search);
                const varietyParam = urlParams.get('variety');
                
                if (varietyParam) {{
                    // URL decode the variety name (handles spaces and special characters)
                    const varietyName = decodeURIComponent(varietyParam);
                    
                    // Check if the variety exists in our data
                    if (TREE_DATA.varieties.includes(varietyName)) {{
                        this.selectVariety(varietyName, false); // Don't update URL to prevent infinite loop
                    }} else {{
                        // Try case-insensitive match
                        const matchingVariety = TREE_DATA.varieties.find(v => 
                            v.toLowerCase() === varietyName.toLowerCase()
                        );
                        if (matchingVariety) {{
                            this.selectVariety(matchingVariety, false); // Don't update URL to prevent infinite loop
                        }}
                    }}
                }}
            }}
            
            updateUrl(varietyName) {{
                if (varietyName) {{
                    const url = new URL(window.location);
                    url.searchParams.set('variety', encodeURIComponent(varietyName));
                    window.history.pushState({{variety: varietyName}}, '', url.toString());
                }} else {{
                    // Remove the variety parameter if no variety selected
                    const url = new URL(window.location);
                    url.searchParams.delete('variety');
                    window.history.pushState({{}}, '', url.toString());
                }}
            }}
            
            resetView() {{
                if (this.network) {{
                    this.network.fit();
                }}
            }}
            
            selectVariety(varietyName, updateUrl = true) {{
                if (!varietyName) {{
                    document.getElementById('network').innerHTML = '<div class="no-data">Select a grape variety to view its family tree</div>';
                    this.network = null;
                    if (updateUrl) {{
                        this.updateUrl(null);
                    }}
                    return;
                }}
                
                this.selectedVariety = varietyName;
                document.getElementById('varietySelector').value = varietyName;
                this.displayTree(varietyName);
                
                // Update URL unless we're handling a URL parameter (to prevent infinite loops)
                if (updateUrl) {{
                    this.updateUrl(varietyName);
                }}
            }}
            
            displayTree(varietyName) {{
                const networkData = TREE_DATA.networks[varietyName];
                if (!networkData) {{
                    document.getElementById('network').innerHTML = '<div class="no-data">No tree data available for this variety</div>';
                    return;
                }}
                
                // Clear the no-data message
                document.getElementById('network').innerHTML = '';
                
                // Prepare data for Vis.js
                const nodes = new vis.DataSet(networkData.nodes);
                const edges = new vis.DataSet(networkData.edges);
                
                const data = {{
                    nodes: nodes,
                    edges: edges
                }};
                
                // Configure layout options
                const options = {{
                    layout: this.useHierarchical ? {{
                        hierarchical: {{
                            direction: this.useLeftToRight ? 'LR' : 'UD',
                            sortMethod: 'directed',
                            nodeSpacing: this.useLeftToRight ? 50 : 120,
                            levelSeparation: this.useLeftToRight ? 253 : 152
                        }}
                    }} : {{}},
                    physics: {{
                        enabled: this.usePhysics,
                        forceAtlas2Based: {{
                            gravitationalConstant: -80,
                            centralGravity: 0.03,
                            springLength: 60,
                            springConstant: 0.12,
                            damping: 0.4
                        }},
                        maxVelocity: 50,
                        solver: 'forceAtlas2Based',
                        stabilization: {{iterations: 150}}
                    }},
                    nodes: {{
                        shape: 'box',
                        margin: 6,
                        widthConstraint: {{
                            maximum: 240
                        }},
                        heightConstraint: {{
                            minimum: 32
                        }},
                        font: {{
                            size: 32,
                            face: 'Arial',
                            color: '#333',
                            multi: 'html'
                        }},
                        borderWidth: 1,
                        opacity: 0.85,
                        shadow: {{
                            enabled: true,
                            color: 'rgba(0,0,0,0.15)',
                            size: 3,
                            x: 1,
                            y: 1
                        }}
                    }},
                    edges: {{
                        width: 2,
                        arrows: {{
                            to: {{
                                enabled: true,
                                scaleFactor: 1
                            }}
                        }},
                        smooth: {{
                            enabled: true,
                            type: 'dynamic'
                        }},
                        chosen: {{
                            edge: function(values, id, selected, hovering) {{
                                if (hovering) {{
                                    values.width = 4;
                                    values.color = '#007BFF';
                                    values.opacity = 1.0;
                                }} else {{
                                    values.width = 2;
                                    values.color = '#999999';
                                    values.opacity = 0.8;
                                }}
                            }}
                        }}
                    }},
                    interaction: {{
                        dragNodes: true,
                        dragView: true,
                        zoomView: true,
                        selectConnectedEdges: false,
                        zoomSpeed: 0.25,
                        wheelSensitivity: 0.15,
                        hideEdgesOnDrag: false,
                        hover: true
                    }}
                }};
                
                // Create network
                const container = document.getElementById('network');
                this.network = new vis.Network(container, data, options);
                
                // Add event listeners
                this.network.on('doubleClick', (params) => {{
                    if (params.nodes.length > 0) {{
                        const clickedNode = params.nodes[0];
                        this.selectVariety(clickedNode);
                    }}
                }});
                
                // Single click for tooltip
                this.network.on('click', (params) => {{
                    if (params.nodes.length > 0) {{
                        const nodeId = params.nodes[0];
                        const node = nodes.get(nodeId);
                        this.showCustomTooltip(params.pointer.DOM, node);
                    }} else {{
                        this.hideCustomTooltip();
                    }}
                }});
                
                // Auto-fit to show entire graph after stabilization
                this.network.once('stabilizationIterationsDone', () => {{
                    this.network.fit({{
                        animation: {{
                            duration: 1000,
                            easingFunction: 'easeInOutQuad'
                        }}
                    }});
                    
                    // Apply current toggle states after network is stabilized
                    this.updateNodeLabels();
                    this.updateNodeColors();
                }});
                
                // Force physics simulation to start (important for URL navigation)
                if (this.usePhysics) {{
                    this.network.startSimulation();
                }}
            }}
            
            updateStats() {{
                const totalVarieties = TREE_DATA.varieties.length;
                const varietiesWithTrees = Object.keys(TREE_DATA.networks).length;
                
                document.getElementById('statsContainer').innerHTML = 
                    `Total varieties: ${{totalVarieties}} | With family trees: ${{varietiesWithTrees}}`;
            }}
        }}
        
        // Initialize the tree viewer when the page loads
        window.addEventListener('DOMContentLoaded', () => {{
            window.treeViewer = new TreeViewer();
        }});
    </script>
</body>
</html>'''
    
    def generate_html_file(self, output_path: str = "docs/grape-tree-viewer.html"):
        """Generate the complete HTML file."""
        print("🔧 Generating tree data...")
        tree_data = self.generate_tree_data()
        
        print("📝 Creating HTML template...")
        html_content = self.generate_html_template(tree_data)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Writing HTML file to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Tree viewer generated: {output_file}")
        print(f"📊 Generated trees for {len(tree_data['networks'])} varieties")
        
        return output_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate grape variety tree viewer HTML with Vis.js",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/17_generate_tree_viewer.py                    # Generate to docs/grape-tree-viewer.html
  python src/17_generate_tree_viewer.py --output custom.html  # Custom output path
        """
    )
    
    parser.add_argument(
        "--output", 
        default="docs/grape-tree-viewer.html",
        help="Output HTML file path (default: docs/grape-tree-viewer.html)"
    )
    
    args = parser.parse_args()
    
    try:
        generator = TreeViewerGenerator()
        output_file = generator.generate_html_file(args.output)
        
        print(f"\n🌐 Open the tree viewer:")
        print(f"file://{output_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()