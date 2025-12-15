/**
 * Quebec Wine Map - Interactive map with cepage filtering
 * Uses Leaflet.js for mapping and URL parameters for deep linking
 */

class QuebecWineMap {
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
            cepage: '',
            type: '',
            region: ''
        };
        
        // Initialize
        this.initMap();
        this.loadData();
        this.setupURLHandling();
        this.setupFilters();
    }
    
    initMap() {
        // Initialize Leaflet map centered on Quebec wine regions
        this.map = L.map(this.mapId, {
            center: [45.4, -72.8], // Centered roughly on Eastern Townships
            zoom: 9,
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
        
        // Remove map info - not needed
        // this.addMapInfo();
        
        // Auto-hide filters when clicking on map
        this.setupMapClickHandler();
    }
    
    async loadData() {
        try {
            console.log('Loading wine data from:', this.dataUrl);
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
            console.error('Error loading wine data:', error);
            this.showError(`Failed to load wine producer data: ${error.message}`);
        }
    }
    
    populateFilters() {
        if (!this.allFeatures.length) return;
        
        // Collect all unique values
        const cepages = new Set();
        const types = new Set();
        const regions = new Set();
        
        this.allFeatures.forEach(feature => {
            const props = feature.properties;
            
            // Cépages
            if (props.cepages && Array.isArray(props.cepages)) {
                props.cepages.forEach(cepage => {
                    if (cepage && cepage.trim()) {
                        cepages.add(cepage.trim());
                    }
                });
            }
            
            // Wine types
            if (props.wine_types && Array.isArray(props.wine_types)) {
                props.wine_types.forEach(type => {
                    if (type && type.trim()) {
                        types.add(type.trim());
                    }
                });
            }
            
            // Regions
            if (props.region && props.region.trim()) {
                regions.add(props.region.trim());
            }
        });
        
        // Populate select elements
        this.populateSelect('cepage-filter', Array.from(cepages).sort());
        this.populateSelect('type-filter', Array.from(types).sort());
        this.populateSelect('region-filter', Array.from(regions).sort());
    }
    
    populateSelect(selectId, options) {
        const select = document.getElementById(selectId);
        if (!select) return;
        
        // Clear existing options except the first ("All")
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Add new options
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            select.appendChild(optionElement);
        });
    }
    
    setupFilters() {
        const filterIds = ['cepage-filter', 'type-filter', 'region-filter'];
        
        filterIds.forEach(id => {
            const select = document.getElementById(id);
            if (select) {
                select.addEventListener('change', () => this.onFilterChange());
            }
        });
        
        // Clear filters button
        const clearBtn = document.getElementById('clear-filters');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearFilters());
        }
        
        // Mobile filter toggle
        const toggleBtn = document.getElementById('filter-toggle');
        const filtersPanel = document.querySelector('.wine-map-filters');
        
        if (toggleBtn && filtersPanel) {
            toggleBtn.addEventListener('click', () => {
                filtersPanel.classList.toggle('show');
            });
        }
        
        // Desktop filter collapse toggle
        const desktopToggleBtn = document.getElementById('filter-toggle-btn');
        if (desktopToggleBtn && filtersPanel) {
            desktopToggleBtn.addEventListener('click', () => {
                filtersPanel.classList.toggle('collapsed');
                // Update arrow direction
                desktopToggleBtn.textContent = filtersPanel.classList.contains('collapsed') ? '▶' : '◀';
            });
        }
        
    }
    
    onFilterChange() {
        // Update filter state
        this.filters.cepage = document.getElementById('cepage-filter')?.value || '';
        this.filters.type = document.getElementById('type-filter')?.value || '';
        this.filters.region = document.getElementById('region-filter')?.value || '';
        
        // Update URL
        this.updateURL();
        
        // Filter and update map
        this.applyFilters();
        this.updateMap();
        
        // Hide mobile filters panel
        const filtersPanel = document.querySelector('.wine-map-filters');
        if (filtersPanel) {
            filtersPanel.classList.remove('show');
        }
    }
    
    applyFilters() {
        this.filteredFeatures = this.allFeatures.filter(feature => {
            const props = feature.properties;
            
            // Cepage filter
            if (this.filters.cepage) {
                if (!props.cepages || !props.cepages.includes(this.filters.cepage)) {
                    return false;
                }
            }
            
            // Type filter
            if (this.filters.type) {
                if (!props.wine_types || !props.wine_types.includes(this.filters.type)) {
                    return false;
                }
            }
            
            // Region filter
            if (this.filters.region) {
                if (props.region !== this.filters.region) {
                    return false;
                }
            }
            
            return true;
        });
        
        console.log(`Filtered: ${this.filteredFeatures.length} / ${this.allFeatures.length} producers`);
    }
    
    updateMap() {
        // Clear existing markers
        this.markers.clearLayers();
        
        // Add filtered markers
        this.filteredFeatures.forEach(feature => {
            const marker = this.createMarker(feature);
            if (marker) {
                this.markers.addLayer(marker);
            }
        });
        
        // Update map bounds if we have markers
        if (this.filteredFeatures.length > 0) {
            const group = new L.featureGroup(this.markers.getLayers());
            if (group.getBounds().isValid()) {
                this.map.fitBounds(group.getBounds(), {
                    padding: [20, 20],
                    maxZoom: 12
                });
            }
        }
        
        // Remove info panel update - not needed
        // this.updateMapInfo();
    }
    
    createMarker(feature) {
        const props = feature.properties;
        const coords = feature.geometry.coordinates;
        
        if (!coords || coords.length !== 2) {
            console.warn('Invalid coordinates for feature:', props.name);
            return null;
        }
        
        const [lon, lat] = coords;
        
        // Create custom marker icon based on properties
        const hasWebsite = props.website;
        const wineCount = props.wine_count || 0;
        
        const marker = L.circleMarker([lat, lon], {
            radius: hasWebsite ? 8 : 6,
            fillColor: hasWebsite ? '#2e7d32' : (wineCount > 3 ? '#1565c0' : '#8b1538'),
            color: 'white',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });
        
        // Create popup content
        const popupContent = this.createPopupContent(props);
        marker.bindPopup(popupContent, {
            maxWidth: 400,
            className: 'wine-popup'
        });
        
        return marker;
    }
    
    createPopupContent(props) {
        let html = `<div class="wine-popup">`;
        
        // Producer name
        html += `<h3>${props.name}</h3>`;
        
        // Wine label (if different)
        if (props.wine_label && props.wine_label !== props.name) {
            html += `<div class="wine-label">Wine label: ${props.wine_label}</div>`;
        }
        
        // Location
        html += `<div class="location">${props.city}, ${props.region}</div>`;
        
        // Website
        if (props.website) {
            html += `<div class="website"><a href="${props.website}" target="_blank" rel="noopener noreferrer">🌐 Visit website</a></div>`;
        }
        
        // Wines
        if (props.wines && props.wines.length > 0) {
            html += `<div class="wines-section">`;
            html += `<h4>Wines (${props.wine_count || props.wines.length})</h4>`;
            
            props.wines.slice(0, 3).forEach(wine => {
                html += `<div class="wine-item">`;
                html += `<div class="wine-name">${wine.name || 'Unnamed wine'}</div>`;
                
                if (wine.type) {
                    html += `<span class="wine-type">${wine.type}</span>`;
                }
                
                if (wine.cepages && wine.cepages.length > 0) {
                    html += `<div class="wine-cepages">`;
                    wine.cepages.forEach(cepage => {
                        const isHighlighted = this.filters.cepage && cepage === this.filters.cepage;
                        const className = isHighlighted ? 'cepage highlighted' : 'cepage';
                        html += `<span class="${className}">${cepage}</span>`;
                    });
                    html += `</div>`;
                }
                
                if (wine.description) {
                    const truncated = wine.description.length > 100 
                        ? wine.description.substring(0, 100) + '...'
                        : wine.description;
                    html += `<div class="wine-description">${truncated}</div>`;
                }
                
                html += `</div>`;
            });
            
            if (props.wine_count > 3) {
                html += `<div style="font-size: 12px; color: #666; font-style: italic;">... and ${props.wine_count - 3} more wines</div>`;
            }
            
            html += `</div>`;
        }
        
        html += `</div>`;
        return html;
    }
    
    addMapInfo() {
        const info = document.createElement('div');
        info.className = 'wine-map-info';
        info.id = 'wine-map-info';
        document.querySelector('.wine-map-container').appendChild(info);
    }
    
    updateMapInfo() {
        const info = document.getElementById('wine-map-info');
        if (!info) return;
        
        const total = this.allFeatures.length;
        const shown = this.filteredFeatures.length;
        
        info.innerHTML = `
            <div><strong>${shown}</strong> of <strong>${total}</strong> producers</div>
            <div style="font-size: 10px; color: #666; margin-top: 4px;">
                🟢 Has website &nbsp; 🔵 Multiple wines
            </div>
        `;
    }
    
    clearFilters() {
        this.filters = { cepage: '', type: '', region: '' };
        
        // Reset form elements
        ['cepage-filter', 'type-filter', 'region-filter'].forEach(id => {
            const select = document.getElementById(id);
            if (select) select.value = '';
        });
        
        // Update URL and map
        this.updateURL();
        this.applyFilters();
        this.updateMap();
    }
    
    setupURLHandling() {
        // Listen for URL changes
        window.addEventListener('popstate', () => {
            this.loadFiltersFromURL();
            this.applyFilters();
            this.updateMap();
        });
    }
    
    loadFiltersFromURL() {
        const params = new URLSearchParams(window.location.search);
        
        this.filters.cepage = params.get('cepage') || '';
        this.filters.type = params.get('type') || '';
        this.filters.region = params.get('region') || '';
        
        // Update form elements
        this.setSelectValue('cepage-filter', this.filters.cepage);
        this.setSelectValue('type-filter', this.filters.type);
        this.setSelectValue('region-filter', this.filters.region);
    }
    
    setSelectValue(selectId, value) {
        const select = document.getElementById(selectId);
        if (select) {
            select.value = value;
        }
    }
    
    updateURL() {
        const params = new URLSearchParams();
        
        if (this.filters.cepage) params.set('cepage', this.filters.cepage);
        if (this.filters.type) params.set('type', this.filters.type);
        if (this.filters.region) params.set('region', this.filters.region);
        
        const newURL = params.toString() 
            ? `${window.location.pathname}?${params.toString()}`
            : window.location.pathname;
        
        // Update URL without page reload
        window.history.replaceState({}, '', newURL);
    }
    
    setupMapClickHandler() {
        const filtersPanel = document.querySelector('.wine-map-filters');
        const desktopToggleBtn = document.getElementById('filter-toggle-btn');
        if (this.map && filtersPanel) {
            this.map.on('click', () => {
                // Auto-hide desktop filters when clicking on map
                if (!filtersPanel.classList.contains('collapsed')) {
                    filtersPanel.classList.add('collapsed');
                    // Update arrow direction
                    if (desktopToggleBtn) {
                        desktopToggleBtn.textContent = '▶';
                    }
                }
                // Also hide mobile filters
                if (filtersPanel.classList.contains('show')) {
                    filtersPanel.classList.remove('show');
                }
            });
        }
    }
    
    showError(message) {
        const mapContainer = document.getElementById(this.mapId);
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f5f5f5; color: #666; text-align: center;">
                    <div>
                        <div style="font-size: 48px; margin-bottom: 16px;">🍷</div>
                        <div style="font-size: 16px; margin-bottom: 8px;">Oops!</div>
                        <div style="font-size: 14px;">${message}</div>
                    </div>
                </div>
            `;
        }
    }
}

// Initialize map when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing wine map...');
    
    // Use absolute path for data URL
    const dataUrl = '/assets/data/quebec-wineries.geojson';
    
    console.log('Data URL:', dataUrl);
    
    if (document.getElementById('wine-map')) {
        window.quebecWineMap = new QuebecWineMap('wine-map', dataUrl);
    } else {
        console.error('wine-map element not found');
    }
});