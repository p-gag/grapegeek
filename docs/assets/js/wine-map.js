/**
 * Enhanced Wine Producers Map - Interactive map with grape variety, wine type, state and visit filtering
 * Uses Leaflet.js for mapping and URL parameters for deep linking
 * Version: 2025-12-20-v3 (enhanced with normalization)
 */

class WineMap {
    constructor(mapId, dataUrl) {
        this.mapId = mapId;
        this.dataUrl = dataUrl;
        this.map = null;
        this.markers = null;
        this.wineData = null;
        this.allFeatures = [];
        this.filteredFeatures = [];
        
        // Filter state
        this.filters = {
            grape_variety: '',
            wine_type: '',
            state: '',
            open_for_visits: ''
        };
        
        // Initialize
        this.initMap();
        this.loadData();
        this.setupURLHandling();
        this.setupFilters();
    }
    
    initMap() {
        // Initialize Leaflet map centered on North America
        this.map = L.map(this.mapId, {
            center: [45.0, -85.0], // Centered on North America wine regions
            zoom: 5,
            zoomControl: false, // Disable default zoom control
            scrollWheelZoom: true
        });
        
        // Add custom zoom control to bottom right
        L.control.zoom({
            position: 'bottomright'
        }).addTo(this.map);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);
        
        // Initialize marker cluster group
        this.markers = L.markerClusterGroup({
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true,
            spiderfyOnMaxZoom: false,
            removeOutsideVisibleBounds: true,
            maxClusterRadius: 50
        });
        
        this.map.addLayer(this.markers);
        
        // Auto-hide filters when clicking on map
        this.setupMapClickHandler();
    }
    
    async loadData() {
        try {
            console.log('Loading wine producer data from:', this.dataUrl);
            const response = await fetch(this.dataUrl);
            console.log('Fetch response status:', response.status);
            console.log('Fetch response ok:', response.ok);
            
            if (!response.ok) {
                throw new Error(`Failed to load data: ${response.status} ${response.statusText}`);
            }
            
            this.wineData = await response.json();
            this.allFeatures = this.wineData.features || [];
            this.filteredFeatures = [...this.allFeatures];
            
            console.log(`Loaded ${this.allFeatures.length} wine producers`);
            
            // Populate filter options
            this.populateFilters();
            
            // Apply initial filters from URL
            this.loadFiltersFromURL();
            
            // Display markers
            this.updateMap();
            
        } catch (error) {
            console.error('Error loading wine producer data:', error);
            this.showError(`Failed to load wine producer data: ${error.message}`);
        }
    }
    
    populateFilters() {
        if (!this.allFeatures.length) return;
        
        // Use filtered features for counting (excluding the grape variety filter itself)
        const featuresForCounting = this.getFilteredFeaturesExcluding('grape_variety');
        
        const grapeVarieties = new Map();
        const wineTypes = new Set();
        const states = new Set();
        
        // Count grape varieties from currently filtered features
        featuresForCounting.forEach(feature => {
            const props = feature.properties;
            
            // Count grape varieties
            if (props.grape_varieties && Array.isArray(props.grape_varieties)) {
                props.grape_varieties.forEach(variety => {
                    if (variety) {
                        grapeVarieties.set(variety, (grapeVarieties.get(variety) || 0) + 1);
                    }
                });
            }
            
            // Collect wine types
            if (props.wine_types && Array.isArray(props.wine_types)) {
                props.wine_types.forEach(type => {
                    if (type) wineTypes.add(type);
                });
            }
            
            if (props.state_province) {
                states.add(props.state_province);
            }
        });
        
        // Populate grape variety filter with dynamic counts
        const grapeSelect = document.getElementById('grape-variety-filter');
        if (grapeSelect) {
            const sortedVarieties = Array.from(grapeVarieties.keys()).sort();
            const grapeVarietiesWithCounts = {};
            sortedVarieties.forEach(variety => {
                const count = grapeVarieties.get(variety);
                grapeVarietiesWithCounts[variety] = `${variety} (${count})`;
            });
            
            this.populateSelectWithCounts(grapeSelect, sortedVarieties, grapeVarietiesWithCounts);
        }
        
        // Populate wine type filter
        const wineTypeSelect = document.getElementById('wine-type-filter');
        if (wineTypeSelect) {
            this.populateSelect(wineTypeSelect, Array.from(wineTypes).sort());
        }
        
        // Populate state filter
        const stateSelect = document.getElementById('state-filter');
        if (stateSelect) {
            this.populateSelect(stateSelect, Array.from(states).sort());
        }
    }
    
    populateSelect(selectElement, options, formatter = null) {
        // Clear existing options except first (All)
        while (selectElement.children.length > 1) {
            selectElement.removeChild(selectElement.lastChild);
        }
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = formatter ? formatter(option) : option;
            selectElement.appendChild(optionElement);
        });
    }
    
    populateSelectWithCounts(selectElement, options, countsMap) {
        // Clear existing options except first (All)
        while (selectElement.children.length > 1) {
            selectElement.removeChild(selectElement.lastChild);
        }
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = countsMap[option] || option;
            selectElement.appendChild(optionElement);
        });
    }
    
    getFilteredFeaturesExcluding(excludeFilter) {
        return this.allFeatures.filter(feature => {
            const props = feature.properties;
            
            // Apply all filters except the excluded one
            if (excludeFilter !== 'wine_type' && this.filters.wine_type) {
                if (!props.wine_types || !props.wine_types.includes(this.filters.wine_type)) {
                    return false;
                }
            }
            
            if (excludeFilter !== 'state' && this.filters.state) {
                if (props.state_province !== this.filters.state) {
                    return false;
                }
            }
            
            if (excludeFilter !== 'open_for_visits' && this.filters.open_for_visits) {
                if (this.filters.open_for_visits === 'yes' && !props.open_for_visits) {
                    return false;
                }
                if (this.filters.open_for_visits === 'no' && props.open_for_visits) {
                    return false;
                }
            }
            
            return true;
        });
    }
    
    
    setupFilters() {
        // Grape variety filter
        const grapeSelect = document.getElementById('grape-variety-filter');
        if (grapeSelect) {
            grapeSelect.addEventListener('change', (e) => {
                this.filters.grape_variety = e.target.value;
                this.applyFilters();
                this.updateURL();
            });
        }
        
        // Wine type filter
        const wineTypeSelect = document.getElementById('wine-type-filter');
        if (wineTypeSelect) {
            wineTypeSelect.addEventListener('change', (e) => {
                this.filters.wine_type = e.target.value;
                this.populateFilters(); // Repopulate other filters with new counts
                this.applyFilters();
                this.updateURL();
            });
        }
        
        // State filter
        const stateSelect = document.getElementById('state-filter');
        if (stateSelect) {
            stateSelect.addEventListener('change', (e) => {
                this.filters.state = e.target.value;
                this.populateFilters(); // Repopulate other filters with new counts
                this.applyFilters();
                this.updateURL();
            });
        }
        
        // Open for visits filter
        const visitsSelect = document.getElementById('open-for-visits-filter');
        if (visitsSelect) {
            visitsSelect.addEventListener('change', (e) => {
                this.filters.open_for_visits = e.target.value;
                this.populateFilters(); // Repopulate other filters with new counts
                this.applyFilters();
                this.updateURL();
            });
        }
        
        // Clear filters button
        const clearButton = document.getElementById('clear-filters');
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                this.clearFilters();
            });
        }
    }
    
    applyFilters() {
        this.filteredFeatures = this.allFeatures.filter(feature => {
            const props = feature.properties;
            
            // Grape variety filter
            if (this.filters.grape_variety) {
                if (!props.grape_varieties || !props.grape_varieties.includes(this.filters.grape_variety)) {
                    return false;
                }
            }
            
            // Wine type filter
            if (this.filters.wine_type) {
                if (!props.wine_types || !props.wine_types.includes(this.filters.wine_type)) {
                    return false;
                }
            }
            
            // State filter
            if (this.filters.state && props.state_province !== this.filters.state) {
                return false;
            }
            
            // Open for visits filter
            if (this.filters.open_for_visits) {
                if (this.filters.open_for_visits === 'yes' && !props.open_for_visits) {
                    return false;
                }
                if (this.filters.open_for_visits === 'no' && props.open_for_visits) {
                    return false;
                }
            }
            
            return true;
        });
        
        console.log(`Filtered to ${this.filteredFeatures.length} producers`);
        this.updateMap();
    }
    
    clearFilters() {
        this.filters = {
            grape_variety: '',
            wine_type: '',
            state: '',
            open_for_visits: ''
        };
        
        // Reset select elements
        const grapeSelect = document.getElementById('grape-variety-filter');
        const wineTypeSelect = document.getElementById('wine-type-filter');
        const stateSelect = document.getElementById('state-filter');
        const visitsSelect = document.getElementById('open-for-visits-filter');
        
        if (grapeSelect) grapeSelect.value = '';
        if (wineTypeSelect) wineTypeSelect.value = '';
        if (stateSelect) stateSelect.value = '';
        if (visitsSelect) visitsSelect.value = '';
        
        this.filteredFeatures = [...this.allFeatures];
        this.updateMap();
        this.updateURL();
    }
    
    updateMap() {
        // Clear existing markers
        this.markers.clearLayers();
        
        if (!this.filteredFeatures.length) {
            console.log('No producers match current filters');
            return;
        }
        
        // Add markers for filtered features
        this.filteredFeatures.forEach(feature => {
            const marker = this.createMarker(feature);
            if (marker) {
                this.markers.addLayer(marker);
            }
        });
        
        // Fit map to show all markers if there are any
        if (this.markers.getLayers().length > 0) {
            this.map.fitBounds(this.markers.getBounds(), { padding: [20, 20] });
        }
    }
    
    createMarker(feature) {
        const props = feature.properties;
        const coords = feature.geometry.coordinates;
        
        if (!coords || coords.length !== 2) {
            console.warn('Invalid coordinates for feature:', props.permit_id);
            return null;
        }
        
        const [lng, lat] = coords;
        
        // Choose marker color based on website and visits
        const markerColor = this.getMarkerColor(props.open_for_visits, props.website);
        
        const marker = L.circleMarker([lat, lng], {
            radius: 8,
            fillColor: markerColor,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });
        
        // Create popup content
        const popupContent = this.createPopupContent(props);
        marker.bindPopup(popupContent);
        
        return marker;
    }
    
    getMarkerColor(openForVisits, website) {
        // Simple two-color scheme: open for visits or not
        if (openForVisits) {
            return '#2E7D32'; // Green - open for visits
        }
        
        return '#FFC107'; // Yellow/Amber - not open for visits
    }
    
    createPopupContent(props) {
        const website = props.website;
        const socialMedia = props.social_media || [];
        const wines = props.wines || [];
        const grapeVarieties = props.grape_varieties || [];
        const wineTypes = props.wine_types || [];
        const activities = props.activities || [];
        
        let html = `<div class="wine-popup">`;
        
        // Producer name
        html += `<h3>${props.name || 'Unknown Producer'}</h3>`;
        
        // Wine label (if different from name)
        if (props.wine_label && props.wine_label !== props.name) {
            html += `<div class="wine-label">Label: ${props.wine_label}</div>`;
        }
        
        // Location
        html += `<div class="location">${props.city || 'Unknown'}, ${props.state_province || 'Unknown'}</div>`;
        
        // Website and Social Media (standard icons)
        const links = [];
        if (website) {
            links.push(`<a href="${website}" target="_blank" rel="noopener" title="Website"><i class="fas fa-globe" style="color: #1976D2;"></i></a>`);
        }
        
        // Social media with platform icons
        if (socialMedia.length > 0) {
            socialMedia.forEach(link => {
                if (link.includes('facebook.com')) {
                    links.push(`<a href="${link}" target="_blank" rel="noopener" title="Facebook"><i class="fab fa-facebook" style="color: #1877F2;"></i></a>`);
                } else if (link.includes('instagram.com')) {
                    links.push(`<a href="${link}" target="_blank" rel="noopener" title="Instagram"><i class="fab fa-instagram" style="color: #E4405F;"></i></a>`);
                } else if (link.includes('twitter.com') || link.includes('x.com')) {
                    links.push(`<a href="${link}" target="_blank" rel="noopener" title="Twitter/X"><i class="fab fa-x-twitter" style="color: #000000;"></i></a>`);
                } else if (link.includes('youtube.com')) {
                    links.push(`<a href="${link}" target="_blank" rel="noopener" title="YouTube"><i class="fab fa-youtube" style="color: #FF0000;"></i></a>`);
                } else {
                    links.push(`<a href="${link}" target="_blank" rel="noopener" title="Social Media"><i class="fas fa-link" style="color: #666;"></i></a>`);
                }
            });
        }
        
        
        // Grape Varieties (cepage style)
        if (grapeVarieties.length > 0) {
            html += `<div class="cepages-section">`;
            html += `<h4>Grape Varieties</h4>`;
            html += `<div class="cepages-list">`;
            
            grapeVarieties.forEach((variety, index) => {
                const isHighlighted = this.filters.grape_variety && variety === this.filters.grape_variety;
                const className = isHighlighted ? 'cepage highlighted' : 'cepage';
                html += `<span class="${className}">${variety}</span>`;
                if (index < grapeVarieties.length - 1) {
                    html += `, `;
                }
            });
            
            html += `</div>`;
            html += `</div>`;
        }
        
        // Wine Types (compact)
        if (wineTypes.length > 0) {
            html += `<div class="wine-types" style="margin-top: 8px;">`;
            html += `<strong>Types:</strong> ${wineTypes.join(', ')}`;
            html += `</div>`;
        }
        
        // Activities (compact, only if open for visits)
        if (activities.length > 0) {
            html += `<div class="activities" style="margin-top: 8px;">`;
            html += `<strong>Visits:</strong> ${activities.join(', ')}`;
            html += `</div>`;
        }
        
        // Bottom section with wine count and social links
        if (wines.length > 0 || links.length > 0) {
            html += `<hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;">`;
            html += `<div class="popup-footer">`;
            
            if (wines.length > 0) {
                html += `<div class="wine-count">${wines.length} wine${wines.length > 1 ? 's' : ''} found</div>`;
            }
            
            if (links.length > 0) {
                html += `<div class="social-links">${links.join(' ')}</div>`;
            }
            
            html += `</div>`;
        }
        
        html += `</div>`;
        return html;
    }
    
    setupURLHandling() {
        window.addEventListener('popstate', () => {
            this.loadFiltersFromURL();
        });
    }
    
    loadFiltersFromURL() {
        const params = new URLSearchParams(window.location.search);
        
        this.filters.grape_variety = params.get('grape_variety') || '';
        this.filters.wine_type = params.get('wine_type') || '';
        this.filters.state = params.get('state') || '';
        this.filters.open_for_visits = params.get('open_for_visits') || '';
        
        // Update select elements
        const grapeSelect = document.getElementById('grape-variety-filter');
        const wineTypeSelect = document.getElementById('wine-type-filter');
        const stateSelect = document.getElementById('state-filter');
        const visitsSelect = document.getElementById('open-for-visits-filter');
        
        if (grapeSelect) grapeSelect.value = this.filters.grape_variety;
        if (wineTypeSelect) wineTypeSelect.value = this.filters.wine_type;
        if (stateSelect) stateSelect.value = this.filters.state;
        if (visitsSelect) visitsSelect.value = this.filters.open_for_visits;
        
        this.applyFilters();
    }
    
    updateURL() {
        const params = new URLSearchParams();
        
        if (this.filters.grape_variety) params.set('grape_variety', this.filters.grape_variety);
        if (this.filters.wine_type) params.set('wine_type', this.filters.wine_type);
        if (this.filters.state) params.set('state', this.filters.state);
        if (this.filters.open_for_visits) params.set('open_for_visits', this.filters.open_for_visits);
        
        const newURL = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
        window.history.replaceState(null, '', newURL);
    }
    
    setupMapClickHandler() {
        this.map.on('click', () => {
            // Optional: Could hide filter dropdown or do other UI actions
        });
    }
    
    showError(message) {
        const mapElement = document.getElementById(this.mapId);
        if (mapElement) {
            mapElement.innerHTML = `
                <div style="padding: 20px; text-align: center; color: #d32f2f;">
                    <h3>Map Loading Error</h3>
                    <p>${message}</p>
                    <p>Please try refreshing the page.</p>
                </div>
            `;
        }
    }
}

// Initialize the map when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if the map element exists
    if (document.getElementById('wine-map')) {
        window.wineMap = new WineMap('wine-map', '/assets/data/wine-producers-final.geojson');
    }
});