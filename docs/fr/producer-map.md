---
description: Interactive map of artisanal wine producers in Quebec with filtering
  by grape varieties (cépages)
english_hash: 7e6ee5fba74ad070045122170d22bc83332f1303c14d89fd22aae3d05e9679d1
hide:
- toc
title: Quebec Wine Producers Map
translated_date: '2025-12-15'
---

# Carte des producteurs de vin du Québec

Découvrez les producteurs de vin grâce à cette carte interactive. Filtrez par cépages et types de vin pour trouver des vignobles qui correspondent à vos intérêts dans un secteur donné.


<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" 
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" 
      crossorigin=""/>

<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />


<div class="wine-map-container">
    <!-- Filter bar -->
    <div class="wine-map-filters-bar">
        <div class="filter-group">
            <label for="cepage-filter">Cépage :</label>
            <select id="cepage-filter">
                <option value="">Toutes les variétés</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label for="type-filter">Type de vin :</label>
            <select id="type-filter">
                <option value="">Tous les types</option>
            </select>
        </div>
        
        <button id="clear-filters" class="clear-filters">Effacer</button>
    </div>
    
    <!-- La carte -->
    <div id="wine-map"></div>
</div>

## À propos de cette carte

!!! warning "Avis aux visiteurs — œnotourisme"
    Ces lieux représentent des installations de production et peuvent **ne pas être ouverts au public**. Plusieurs producteurs vendent leurs vins aux marchés locaux ou par l’entremise de distributeurs. Veuillez communiquer directement avec les établissements avant de vous déplacer afin de confirmer leurs politiques d’accueil et leurs heures d’ouverture.

!!! info "Exactitude des données"
    Cette carte utilise des données publiques et est enrichie par de la recherche automatisée. Elle peut contenir des erreurs ou de l’information désuète. Veuillez vérifier les détails directement auprès des producteurs.

Pour l’instant, la principale source de données est la RACJ (Registre des titulaires de permis). J’envisage d’ajouter d’autres régions éventuellement.

### Fonctionnalités

- **🍇 Filtrer par cépage** : Trouvez des producteurs qui cultivent des cépages précis comme Frontenac, Marquette ou Chardonnay
- **📍 Explorer les régions** : Parcourez les régions viticoles du Québec, notamment les Cantons-de-l’Est, la Montérégie et les Laurentides  
- **📱 Mobile** : Ça marche, mais un plus grand écran = plus le fun
- **🌐 Infos sur les producteurs** : Cliquez sur les marqueurs pour voir les sites web et les cépages

### Légende de la carte

- **🟢 Vert** : Producteurs avec site web
- **🔴 Rouge** : Producteurs standard


*Données : registre des permis de la RACJ, bonifiées par une recherche sur les producteurs. Carte © Contributeurs d’OpenStreetMap.*

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" 
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" 
        crossorigin=""></script>

<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>