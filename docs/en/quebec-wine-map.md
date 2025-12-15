---
title: Quebec Wine Producers Map
description: Interactive map of artisanal wine producers in Quebec with filtering by grape varieties (cépages)
---

# Quebec Wine Producers Map

Discover Quebec's wine producers with our interactive map. Filter by grape varieties (cépages), wine types, and regions to find vineyards that match your interests.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" 
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" 
      crossorigin=""/>

<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />


<div class="wine-map-container">
    <!-- Mobile filter toggle -->
    <button id="filter-toggle" class="filter-toggle" aria-label="Toggle filters">
        🔍 Filters
    </button>
    
    <!-- Filter controls -->
    <div class="wine-map-filters" id="wine-map-filters">
        <button class="filter-toggle-btn" id="filter-toggle-btn" aria-label="Toggle filters" title="Hide/Show filters">
            ◀
        </button>
        
        <div class="filter-content">
            <h4>🍇 Filter Producers</h4>
            
            <div class="filter-group">
                <label for="cepage-filter">Grape Variety (Cépage)</label>
                <select id="cepage-filter">
                    <option value="">All varieties</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label for="type-filter">Wine Type</label>
                <select id="type-filter">
                    <option value="">All types</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label for="region-filter">Region</label>
                <select id="region-filter">
                    <option value="">All regions</option>
                </select>
            </div>
            
            <button id="clear-filters" class="clear-filters">Clear all filters</button>
        </div>
    </div>
    
    <!-- The map -->
    <div id="wine-map"></div>
</div>

## About This Map

This interactive map shows **wine producers** in Quebec with production permits from the RACJ (Registre des titulaires de permis). 

### Features

- **🍇 Filter by Grape Variety**: Find producers growing specific cépages like Frontenac, Marquette, or Chardonnay
- **📍 Explore Regions**: Browse Quebec's wine regions including Cantons-de-l'Est, Montérégie, and Laurentides  
- **🔗 Share Links**: Direct URLs for filtered maps (e.g., `/quebec-wine-map/?cepage=frontenac`)
- **📱 Mobile Optimized**: Works great on phones and tablets
- **🌐 Producer Info**: Click markers for websites and wine details

### Map Legend

- **🟢 Green**: Producers with websites
- **🔵 Blue**: Producers with multiple wines (3+)  
- **🔴 Red**: Standard producers

### Filters

Combine filters for grape variety, wine type, and region. Filters update the URL for easy sharing.

## Wine Tourism

Use this map to:
- Find nearby producers when traveling in Quebec
- Locate wineries growing specific grape varieties
- Plan routes through wine regions
- Contact producers directly

### Major Regions

- **Cantons-de-l'Est**: Historic wine region with established vineyards
- **Montérégie**: Quebec's largest concentration of wineries
- **Laurentides**: Emerging region with cold-climate viticulture  
- **Lanaudière**: Growing number of producers

---

*Data: RACJ permit registry, enhanced with producer research. Map © OpenStreetMap contributors.*

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" 
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" 
        crossorigin=""></script>

<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>

