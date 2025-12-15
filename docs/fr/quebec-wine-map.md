---
english_hash: 5cc2a0ab4d3197537289fa25011e1f054bf572ae1ba94fd4b60c40d0e9e83e26
translated_date: '2025-12-15'
title: Carte des producteurs de vin du Québec
description: Carte interactive des producteurs de vin artisanaux au Québec avec filtres par cépages
hide:
  - toc
---

# Carte des producteurs de vin du Québec

Découvrez les producteurs de vin du Québec grâce à notre carte interactive. Filtrez par cépages et types de vin pour trouver les vignobles qui correspondent à vos intérêts.

!!! warning "Avis sur l'œnotourisme"
    Ces emplacements représentent des installations de production et peuvent **ne pas être ouverts au public**. Plusieurs producteurs vendent leurs vins dans des marchés locaux ou par l’entremise de distributeurs. Veuillez communiquer directement avec les vignobles avant de vous déplacer pour confirmer leurs politiques d’accueil et leurs heures d’ouverture.

!!! info "Exactitude des données"
    Cette carte est générée à partir des données publiques de permis de la RACJ et bonifiée par de la recherche automatisée. Elle peut contenir des erreurs ou de l’information périmée. Veuillez vérifier les détails directement auprès des producteurs.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" 
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" 
      crossorigin=""/>

<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />


<div class="wine-map-container">
    <!-- Mobile filter toggle -->
    <button id="filter-toggle" class="filter-toggle" aria-label="Afficher/Masquer les filtres">
        🔍 Filtres
    </button>
    
    <!-- Filter controls -->
    <div class="wine-map-filters" id="wine-map-filters">
        <button class="filter-toggle-btn" id="filter-toggle-btn" aria-label="Afficher/Masquer les filtres" title="Masquer/Afficher les filtres">
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
            
            
            <button id="clear-filters" class="clear-filters">Effacer tous les filtres</button>
        </div>
    </div>
    
    <!-- The map -->
    <div id="wine-map"></div>
</div>

## À propos de cette carte

Cette carte interactive présente des **producteurs de vin** au Québec titulaires d’un permis de production de la RACJ (Registre des titulaires de permis). 

### Fonctionnalités

- **🍇 Filtrer par cépage** : trouvez des producteurs qui cultivent des cépages précis comme Frontenac, Marquette ou Chardonnay
- **📍 Explorer les régions** : parcourez les régions viticoles du Québec, dont les Cantons-de-l’Est, la Montérégie et les Laurentides  
- **🔗 Partager des liens** : URL directes pour des cartes filtrées (p. ex., `/quebec-wine-map/?cepage=frontenac`)
- **📱 Optimisée pour mobile** : fonctionne super bien sur téléphones et tablettes
- **🌐 Infos sur les producteurs** : cliquez sur les marqueurs pour les sites web et les détails des vins

### Légende de la carte

- **🟢 Vert** : producteurs avec site web
- **🔵 Bleu** : producteurs avec plusieurs vins (3+)  
- **🔴 Rouge** : producteurs réguliers

### Filtres

Combinez les filtres par cépage, type de vin et région. Les filtres mettent l’URL à jour pour faciliter le partage.

## Œnotourisme

Utilisez cette carte pour :
- Trouver des producteurs à proximité lors de vos déplacements au Québec
- Repérer des vignobles qui cultivent des cépages spécifiques
- Planifier des parcours à travers les régions viticoles
- Contacter directement les producteurs

---

*Données : registre des permis de la RACJ, enrichies par la recherche sur les producteurs. Carte © contributeurs d’OpenStreetMap.*

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" 
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" 
        crossorigin=""></script>

<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>