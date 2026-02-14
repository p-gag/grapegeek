# Grape Family Trees - Interactive Genealogy Viewer

React Flow implementation for exploring grape variety ancestry with species coloring, crossing analysis, and mobile support.

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

4. **Open browser:** http://localhost:5173

## Production Build

```bash
npm run build  # Builds to ../docs/family-trees/ with data copy
```

## Features

- 🧬 **Species coloring**: Recursive genetic composition with proportional color bars
- 🌳 **Duplicate parent mode**: Crossing genealogy analysis with separate parent instances  
- 🏁 **Cross-platform flags**: Flag-icons CSS library (works on Windows)
- 📱 **Mobile responsive**: Touch gestures, adaptive layout, optimized for all screens
- 🔗 **URL parameters**: Direct variety linking with `?variety=Name`
- ✨ **Hover highlighting**: Blue connections and node scaling
- 🎯 **Interactive exploration**: Click nodes to navigate variety relationships

## Architecture

- **Data**: Client-side subgraph extraction from unified JSON
- **Components**: Custom GrapeNode with species bars, flags, and hover effects
- **Layout**: Hierarchical positioning with level calculation
- **Deployment**: Vite build configured for `/family-trees/` sub-path

## Key Files

- `src/App.jsx` - Main React Flow app with species coloring logic
- `src/components/GrapeNode.jsx` - Custom node with proportional species bars
- `src/components/NodePopup.jsx` - Contextual variety information
- `copy-data.js` - Build-time data copy script
- `vite.config.js` - Sub-path deployment configuration