---
description: Interactive map of wine producers across North America with filtering
  by grape varieties, wine types, state/province and visiting options
english_hash: 7df5dedd2601270fa2b6c3501f4bd94372ad34743ec2bb2d23eaffb974eb6983
hide:
- toc
title: North American Wine Producers Map
translated_date: '2025-12-25'
---

# Carte des producteurs de vin en Amérique du Nord

Découvrez les producteurs de vin partout en Amérique du Nord grâce à cette carte interactive. Filtrez par cépages, types de vin, État/province et critère « ouvert aux visites » pour dénicher les vignobles parfaits près de chez vous.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" 
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" 
      crossorigin=""/>

<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" 
      integrity="sha512-Avb2QiuDEEvB4bZJYdft2mNjVShBftLdPG8FJ0V7irTLQ8Uo0qcPxh4Plq7G5tGm0rU+1SPhVotteLpBERwTkw==" 
      crossorigin="anonymous" referrerpolicy="no-referrer" />

<div class="wine-map-container">
    <!-- Barre de filtres -->
    <div class="wine-map-filters-bar">
        <div class="filter-group">
            <label for="grape-variety-filter">Cépage :</label>
            <select id="grape-variety-filter">
                <option value="">Tous les cépages</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label for="wine-type-filter">Type de vin :</label>
            <select id="wine-type-filter">
                <option value="">Tous les types de vin</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label for="state-filter">État/province :</label>
            <select id="state-filter">
                <option value="">Tous les États/provinces</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label for="open-for-visits-filter">Ouvert aux visites :</label>
            <select id="open-for-visits-filter">
                <option value="">Tous les producteurs</option>
                <option value="yes">Ouvert aux visites</option>
                <option value="no">Non ouvert aux visites</option>
            </select>
        </div>
        
        <button id="clear-filters" class="clear-filters">Réinitialiser</button>
    </div>
    
    <!-- La carte -->
    <div id="wine-map"></div>
</div>

## À propos de cette carte

!!! warning "Avis sur l’œnotourisme"
    Utilisez le filtre « Ouvert aux visites » pour trouver les producteurs qui accueillent des visiteurs. Plusieurs emplacements représentent uniquement des installations de production. Communiquez toujours directement avec les vignobles avant de vous déplacer afin de confirmer leurs politiques d’accueil et leurs heures d’ouverture.

!!! info "Fiabilité des données"
    Cette carte s’appuie sur des données publiques et est enrichie par de la recherche automatisée. Elle peut contenir des erreurs ou des renseignements périmés. Veuillez vérifier les détails directement auprès des producteurs.

Cet ensemble de données exhaustif regroupe des producteurs provenant de :
- **Québec** : RACJ (Registre des titulaires de permis) 
- **États-Unis** : données de permis du TTB (Alcohol and Tobacco Tax Bureau)

### Fonctionnalités

- **🍇 Filtrer par cépage** : Trouvez des producteurs qui cultivent des variétés précises comme Marquette, Vidal ou Chardonnay
- **🍷 Filtrer par type de vin** : Recherchez des producteurs de vins rouges, blancs, rosés, effervescents ou de dessert
- **📍 Parcourir par État/province** : Explorez des régions précises partout en Amérique du Nord
- **👥 Filtrer par visites** : Repérez les producteurs ouverts aux visites du public
- **📱 Adaptée aux appareils mobiles** : Optimisée pour tous les formats d’écran
- **🌐 Infos sur le producteur** : Cliquez sur les marqueurs pour obtenir des renseignements détaillés sur les vins, les sites Web et les activités

### Légende de la carte

- **🟢 Vert** : Ouvert aux visites
- **🟡 Jaune** : Non ouvert aux visites

### Informations sur les vins

Chaque marqueur de producteur affiche des renseignements détaillés lorsque vous cliquez dessus :
- **Cépages** : Les variétés cultivées (cépages)
- **Types de vins** : Types de vins produits (rouge, blanc, rosé, etc.)
- **Activités** : Activités offertes aux visiteurs (dégustations, visites, événements)
- **Contact** : Site Web et liens vers les médias sociaux

*Données : registre des permis de la RACJ (Québec) + données de permis du TTB (É.-U.), bonifiées par de la recherche automatisée sur les producteurs. Carte © les contributeurs d’OpenStreetMap.*

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" 
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" 
        crossorigin=""></script>

<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>