---
english_hash: 038b88438b223d5e90cfeea2ac721d247a07f8f69b3fa9eec9cb69138c9271c8
translated_date: '2025-12-14'
---

---
title: Carte des producteurs de vin du Québec
description: Carte interactive des producteurs de vin artisanaux au Québec avec filtrage par cépages
---

# Carte des producteurs de vin du Québec

Découvrez les producteurs de vin du Québec grâce à notre carte interactive. Filtrez par cépages, types de vin et régions pour trouver les vignobles qui vous intéressent.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" 
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" 
      crossorigin=""/>

<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />

<link rel="stylesheet" href="../assets/css/wine-map.css">

<div class="wine-map-container">
    <!-- Bascule des filtres (mobile) -->
    <button id="filter-toggle" class="filter-toggle" aria-label="Afficher/masquer les filtres">
        🔍 Filtres
    </button>
    
    <!-- Contrôles de filtre -->
    <div class="wine-map-filters" id="wine-map-filters">
        <button class="filter-toggle-btn" id="filter-toggle-btn" aria-label="Afficher/masquer les filtres" title="Afficher/Masquer les filtres">
            ◀
        </button>
        
        <div class="filter-content">
            <h4>🍇 Filtrer les producteurs</h4>
            
            <div class="filter-group">
                <label for="cepage-filter">Cépage</label>
                <select id="cepage-filter">
                    <option value="">Toutes les variétés</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label for="type-filter">Type de vin</label>
                <select id="type-filter">
                    <option value="">Tous les types</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label for="region-filter">Région</label>
                <select id="region-filter">
                    <option value="">Toutes les régions</option>
                </select>
            </div>
            
            <button id="clear-filters" class="clear-filters">Effacer tous les filtres</button>
        </div>
    </div>
    
    <!-- La carte -->
    <div id="wine-map"></div>
</div>

## À propos de cette carte

Cette carte interactive présente les **producteurs de vin** au Québec détenant un permis de production de la RACJ (Registre des titulaires de permis).

### Fonctionnalités

- **🍇 Filtrer par cépage** : Trouvez les producteurs qui cultivent des cépages précis comme Frontenac, Marquette ou Chardonnay
- **📍 Explorer les régions** : Parcourez les régions viticoles du Québec, dont les Cantons-de-l'Est, la Montérégie et les Laurentides  
- **🔗 Partager des liens** : URLs directes pour les cartes filtrées (p. ex., `/quebec-wine-map/?cepage=frontenac`)
- **📱 Optimisée pour mobile** : Fonctionne très bien sur téléphones cellulaires et tablettes
- **🌐 Infos producteurs** : Cliquez sur les marqueurs pour accéder aux sites Web et aux détails sur les vins

### Légende de la carte

- **🟢 Vert** : Producteurs avec site Web
- **🔵 Bleu** : Producteurs avec plusieurs vins (3+)  
- **🔴 Rouge** : Producteurs réguliers

### Filtres

Combinez les filtres par cépage, type de vin et région. Les filtres mettent l’URL à jour pour faciliter le partage.

## Œnotourisme

Utilisez cette carte pour :
- Repérer les producteurs à proximité lors de vos déplacements au Québec
- Localiser les vignobles qui cultivent des cépages spécifiques
- Planifier des parcours à travers les régions viticoles
- Contacter directement les producteurs

### Régions principales

- **Cantons-de-l'Est** : Région viticole historique avec des vignobles bien établis
- **Montérégie** : La plus forte concentration de vignobles du Québec
- **Laurentides** : Région émergente avec viticulture de climat froid  
- **Lanaudière** : Nombre croissant de producteurs

---

*Données : registre des permis de la RACJ, bonifiées par des recherches sur les producteurs. Carte © les contributeurs d’OpenStreetMap.*

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" 
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" 
        crossorigin=""></script>

<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>

<script src="../assets/js/wine-map.js"></script>