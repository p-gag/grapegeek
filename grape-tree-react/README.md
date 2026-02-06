# Grape Tree Viewer - React Flow Test

A React Flow implementation for visualizing grape variety family trees with proper flag icon support.

## Setup

1. **Install dependencies:**
   ```bash
   cd grape-tree-react
   npm install
   ```

2. **Generate tree data:**
   ```bash
   cd ..
   uv run src/18_generate_tree_data.py
   ```

3. **Start development server:**
   ```bash
   cd grape-tree-react
   npm run dev
   ```

4. **Open browser:**
   ```
   http://localhost:3000
   ```

## Features

- ✅ **Proper flag display**: Uses flag-icons CSS library with React components
- ✅ **Interactive tree exploration**: Double-click nodes to explore different varieties
- ✅ **Custom node styling**: Berry color backgrounds, species information
- ✅ **Hierarchical layout**: Automatic positioning based on genealogy levels
- ✅ **Responsive design**: Works on desktop and mobile
- ✅ **Rich tooltips**: VIVC numbers, breeding info, parentage

## Architecture

- **Data generation**: `../src/18_generate_tree_data.py` extracts tree data from JSONL files
- **Custom nodes**: `src/components/GrapeNode.jsx` renders grape variety information
- **Flag rendering**: Direct CSS class integration (no HTML parsing issues)
- **Layout**: Hierarchical positioning based on genealogical levels

## Key Improvements over Vis.js

- 🎯 **Native HTML support**: React components render HTML naturally
- 🏁 **Proper flags**: CSS flag icons work seamlessly in JSX
- ⚡ **Better performance**: React's virtual DOM handles updates efficiently  
- 🎨 **Modern styling**: CSS-in-JS and modern React patterns
- 🔧 **Developer experience**: Better debugging and component inspection

## Data Flow

1. Python script (`18_generate_tree_data.py`) processes grape variety data
2. Generates `src/data/tree-data.json` with React Flow compatible format
3. React app imports JSON and renders interactive family trees
4. Custom `GrapeNode` components display flags, colors, and metadata