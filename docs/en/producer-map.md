---
title: North American Wine Producers Map
description: Interactive map of wine producers across North America with filtering by grape varieties, wine types, state/province and visiting options
hide:
  - toc
---

# North American Wine Producers Map

Discover wine producers across North America with this interactive map. Filter by grape varieties (cépages), wine types, state/province and whether they're open for public visits to find the perfect wineries in your area.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" 
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" 
      crossorigin=""/>

<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" 
      integrity="sha512-Avb2QiuDEEvB4bZJYdft2mNjVShBftLdPG8FJ0V7irTLQ8Uo0qcPxh4Plq7G5tGm0rU+1SPhVotteLpBERwTkw==" 
      crossorigin="anonymous" referrerpolicy="no-referrer" />

<div class="wine-map-container">
    <!-- Filter bar -->
    <div class="wine-map-filters-bar">
        <div class="filter-group">
            <label for="grape-variety-filter">Grape Variety:</label>
            <select id="grape-variety-filter">
                <option value="">All grape varieties</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label for="wine-type-filter">Wine Type:</label>
            <select id="wine-type-filter">
                <option value="">All wine types</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label for="state-filter">State/Province:</label>
            <select id="state-filter">
                <option value="">All states/provinces</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label for="open-for-visits-filter">Open for Visits:</label>
            <select id="open-for-visits-filter">
                <option value="">All producers</option>
                <option value="yes">Open for visits</option>
                <option value="no">Not open for visits</option>
            </select>
        </div>
        
        <button id="clear-filters" class="clear-filters">Clear</button>
    </div>
    
    <!-- The map -->
    <div id="wine-map"></div>
</div>

## About This Map

!!! warning "Wine Tourism Notice"
    Use the "Open for Visits" filter to find producers that welcome visitors. Many locations represent production facilities only. Always contact wineries directly before visiting to confirm their tourism policies and opening hours.

!!! info "Data Accuracy"
    This map uses public data and is enriched through automated research. It may contain errors or outdated information. Please verify details directly with producers.

This comprehensive dataset combines producers from:
- **Quebec**: RACJ (Registre des titulaires de permis) 
- **United States**: TTB (Alcohol and Tobacco Tax Bureau) permit data

### Features

- **🍇 Filter by Grape Variety**: Find producers growing specific varieties like Marquette, Vidal, or Chardonnay
- **🍷 Filter by Wine Type**: Search for red, white, rosé, sparkling, or dessert wine producers
- **📍 Browse by State/Province**: Explore specific regions across North America
- **👥 Filter by Visits**: Find producers open to public visits
- **📱 Mobile Friendly**: Optimized for all screen sizes
- **🌐 Producer Info**: Click markers for detailed wine information, websites and activities

### Map Legend

- **🟢 Green**: Open for visits
- **🟡 Yellow**: Not open for visits

### Wine Information

Each producer marker shows detailed information when clicked:
- **Grape Varieties**: The specific varieties grown (cépages)
- **Wine Types**: Types of wines produced (red, white, rosé, etc.)
- **Activities**: Available visitor activities (tastings, tours, events)
- **Contact**: Website and social media links

*Data: RACJ permit registry (Quebec) + TTB permit data (US), enhanced with automated producer research. Map © OpenStreetMap contributors.*

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" 
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" 
        crossorigin=""></script>

<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>

<script src="../assets/js/wine-map.js"></script>