# Quebec Wine Map - Design Document

## Overview
Interactive map showing Quebec wine producers with filterable cépages, integrated into the MkDocs site.

## User Stories
- **Variety researchers**: "Show me all vineyards growing Frontenac"
- **Wine tourists**: "Find wineries near Montreal with tasting rooms"
- **Deep linking**: Direct links from variety pages to map filtered by that grape

## Technical Architecture

### Data Flow
```
Enhanced Producer Data → Geocoding → GeoJSON → Leaflet Map
```

### URL Structure
- Base: `/quebec-wine-map/`
- Filtered: `/quebec-wine-map/?cepage=frontenac&type=red&region=monteregie`
- Deep links from variety pages: `[View producers](../quebec-wine-map/?cepage=frontenac)`

### Components

#### 1. Data Layer
- **Source**: `data/racj/racj-alcool-fabricant_enhanced.json`
- **Geocoding**: Address → coordinates using OpenStreetMap Nominatim
- **Output**: `docs/assets/data/quebec-wineries.geojson`

#### 2. Map Implementation
- **Library**: Leaflet.js (lightweight, mobile-friendly)
- **Base tiles**: OpenStreetMap
- **Bounds**: Quebec wine regions focus
- **Clustering**: MarkerClusterGroup for overlapping markers

#### 3. Filter System
```javascript
// URL params: ?cepage=frontenac&type=red&region=monteregie
filters = {
  cepage: string,    // grape variety
  type: string,      // red/white/rosé/sparkling
  region: string     // administrative region
}
```

#### 4. UI Components
- **Filter sidebar**: Dropdown selects with auto-complete
- **Marker popups**: Producer info + wine list with highlighted matching cépages
- **Info panel**: Selected producer details
- **Mobile**: Collapsible filter drawer

### File Structure
```
docs/
├── quebec-wine-map.md                    # English map page
├── fr/carte-vignobles-quebec.md          # French map page
├── assets/
│   ├── js/
│   │   ├── wine-map.js                   # Core map logic
│   │   ├── wine-filters.js               # Filter functionality
│   │   └── wine-data.js                  # Data loading/processing
│   ├── css/wine-map.css                  # Map styling
│   └── data/quebec-wineries.geojson      # Producer geographic data
```

### Data Schema (GeoJSON)
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.2, 45.5]
      },
      "properties": {
        "name": "Vignoble de l'Orpailleur",
        "wine_label": "L'Orpailleur",
        "city": "Dunham",
        "region": "Montérégie", 
        "website": "https://...",
        "wines": [
          {
            "name": "Cuvée Natashquan",
            "type": "white",
            "cepages": ["Seyval Blanc", "Chardonnay"],
            "description": "..."
          }
        ]
      }
    }
  ]
}
```

### Integration Points

#### Variety Pages Enhancement
```markdown
## Producers Growing Marquette

[View all Marquette producers on map](/quebec-wine-map/?cepage=marquette) 🗺️

The following Quebec vineyards grow Marquette:
- [Vignoble A](producer-link)
- [Vignoble B](producer-link)
```

#### Navigation Updates
```yaml
# mkdocs.yml nav section
nav:
  - Home: index.md
  - Varieties: varieties/
  - Quebec Wine Map: quebec-wine-map.md  # New
  - About: about.md
```

## Development Phases

### Phase 1: Data Preparation
- Extract producer addresses from enhanced data
- Geocode addresses to coordinates
- Generate GeoJSON with wine metadata
- Validate coordinate accuracy

### Phase 2: Basic Map
- Create Leaflet map with Quebec bounds
- Load producer markers
- Basic popup with producer info
- Mobile-responsive layout

### Phase 3: Filtering System
- Implement cepage filter dropdown
- URL parameter handling for deep links
- Filter persistence and sharing
- Performance optimization for large datasets

### Phase 4: Integration
- Add map links to variety pages
- Bilingual support (French interface)
- Style integration with Material theme
- Cross-linking with producer profiles

## Success Metrics
- **Functionality**: All filters work correctly with URL parameters
- **Performance**: Map loads in <2s with 200+ producers
- **Mobile**: Usable on phones/tablets
- **Integration**: Seamless navigation from variety pages
- **Accessibility**: Keyboard navigation, screen reader support