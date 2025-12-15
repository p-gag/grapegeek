---
title: Quebec Wine Producers Map
description: Interactive map of artisanal wine producers in Quebec with filtering by grape varieties (cépages)
hide:
  - toc
---

# Quebec Wine Producers Map

Discover wine producers with this interactive map. Filter by grape varieties (cépages) and wine types to find vineyards that match your interests in a given area.


<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" 
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" 
      crossorigin=""/>

<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />


<div class="wine-map-container">
    <!-- Filter bar -->
    <div class="wine-map-filters-bar">
        <div class="filter-group">
            <label for="cepage-filter">Grape Variety:</label>
            <select id="cepage-filter">
                <option value="">All varieties</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label for="type-filter">Wine Type:</label>
            <select id="type-filter">
                <option value="">All types</option>
            </select>
        </div>
        
        <button id="clear-filters" class="clear-filters">Clear</button>
    </div>
    
    <!-- The map -->
    <div id="wine-map"></div>
</div>

## About This Map

!!! warning "Wine Tourism Notice"
    These locations represent production facilities and may **not be open for public visits**. Many producers sell their wines at local markets or through distributors. Please contact wineries directly before visiting to confirm their tourism policies and opening hours.

!!! info "Data Accuracy"
    This map use public data and is enriched through automated research. It may contain errors or outdated information. Please verify details directly with producers.

For now, the main data source is the RACJ (Registre des titulaires de permis). I will be looking to add more regions at some point.

### Features

- **🍇 Filter by Grape Variety**: Find producers growing specific cépages like Frontenac, Marquette, or Chardonnay
- **📍 Explore Regions**: Browse Quebec's wine regions including Cantons-de-l'Est, Montérégie, and Laurentides  
- **📱 Mobile**: Works but bigger screen = more fun
- **🌐 Producer Info**: Click markers for websites and varieties

### Map Legend

- **🟢 Green**: Producers with websites
- **🔴 Red**: Standard producers


*Data: RACJ permit registry, enhanced with producer research. Map © OpenStreetMap contributors.*

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" 
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" 
        crossorigin=""></script>

<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>

