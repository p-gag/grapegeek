---
description: Interactive map of artisanal wine producers in Quebec with filtering
  by grape varieties (cépages)
english_hash: 5a64e4b650dc4002afc91889c61a6a4d41224a03e2bbaed3b4ce4d0ca1d79cd3
hide:
- toc
title: Quebec Wine Producers Map
translated_date: '2025-12-16'
---

# Carte des producteurs de vin du Québec

Découvrez les producteurs de vin avec cette carte interactive. Filtrez par cépages et types de vin pour trouver des vignobles qui correspondent à vos intérêts dans un secteur donné.


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
                <option value="">Tous les cépages</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label for="type-filter">Type de vin :</label>
            <select id="type-filter">
                <option value="">Tous les types</option>
            </select>
        </div>
        
        <button id="clear-filters" class="clear-filters">Réinitialiser</button>
    </div>
    
    <!-- The map -->
    <div id="wine-map"></div>
</div>

## À propos de cette carte

!!! warning "Avis sur l’œnotourisme"
    Ces emplacements correspondent à des installations de production et peuvent **ne pas être ouverts au public**. Plusieurs producteurs vendent leurs vins aux marchés publics ou par l’entremise de distributeurs. Veuillez communiquer directement avec les vignobles avant de vous déplacer afin de confirmer leurs politiques d’accueil et leurs heures d’ouverture.

!!! info "Exactitude des données"
    Cette carte utilise des données publiques et est enrichie par de la recherche automatisée. Elle peut contenir des erreurs ou des informations désuètes. Veuillez vérifier les détails directement auprès des producteurs.

Pour l’instant, la principale source de données est la RACJ (Registre des titulaires de permis). J’envisage d’ajouter d’autres régions éventuellement.

### Fonctionnalités

- **🍇 Filtrer par cépage** : Repérez les producteurs qui cultivent des cépages précis comme Frontenac, Marquette ou Chardonnay
- **📍 Explorer les régions** : Parcourez les régions viticoles du Québec, notamment les Cantons-de-l’Est, la Montérégie et les Laurentides  
- **📱 Mobile** : Fonctionne sur cellulaire, mais un plus grand écran = plus de plaisir
- **🌐 Infos sur le producteur** : Cliquez sur les marqueurs pour les sites Web et les cépages

### Légende de la carte

- **🟢 Vert** : Producteurs ayant un site Web
- **🔴 Rouge** : Producteurs réguliers


*Données : registre des permis de la RACJ, bonifiées par la recherche sur les producteurs. Carte © contributeurs d’OpenStreetMap.*

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" 
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" 
        crossorigin=""></script>

<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>