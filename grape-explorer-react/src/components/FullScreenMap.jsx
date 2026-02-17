import { useState, useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Custom marker icons
const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3);"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6]
  })
}

const greenIcon = createCustomIcon('#2E7D32')  // Open for visits
const yellowIcon = createCustomIcon('#FFC107') // Not open for visits

// Component to handle map updates
const MapController = ({ producers, selectedProducers }) => {
  const map = useMap()
  
  useEffect(() => {
    const displayProducers = selectedProducers.length > 0 ? selectedProducers : producers
    if (displayProducers && displayProducers.length > 0) {
      const bounds = L.latLngBounds(displayProducers.map(p => [p.coordinates[1], p.coordinates[0]]))
      map.fitBounds(bounds, { padding: [20, 20] })
    }
  }, [map, producers, selectedProducers])
  
  return null
}

const FullScreenMap = ({ initialVariety = null, onClose }) => {
  const [mapData, setMapData] = useState(null)
  const [allProducers, setAllProducers] = useState([])
  const [filteredProducers, setFilteredProducers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const mapRef = useRef()

  // Filter states
  const [filters, setFilters] = useState({
    grape_variety: initialVariety || '',
    wine_type: '',
    state: '',
    open_for_visits: ''
  })

  // Filter options
  const [filterOptions, setFilterOptions] = useState({
    grape_varieties: [],
    wine_types: [],
    states_provinces: []
  })

  useEffect(() => {
    const loadMapData = async () => {
      try {
        setLoading(true)
        const response = await fetch('/data/map-data.json')
        if (!response.ok) {
          throw new Error(`Failed to load map data: ${response.status}`)
        }
        const data = await response.json()
        setMapData(data)
        setAllProducers(data.full_map.producers)
        setFilterOptions(data.full_map.filter_options)
        
        // Apply initial filters if variety is specified
        if (initialVariety && data.varieties[initialVariety]) {
          setFilteredProducers(data.varieties[initialVariety].producers)
        } else {
          setFilteredProducers(data.full_map.producers)
        }
      } catch (err) {
        console.error('Error loading map data:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadMapData()
  }, [initialVariety])

  useEffect(() => {
    applyFilters()
  }, [filters, allProducers])

  const applyFilters = () => {
    if (!allProducers.length) return

    let filtered = [...allProducers]

    // Grape variety filter
    if (filters.grape_variety) {
      filtered = filtered.filter(producer => 
        producer.grape_varieties.includes(filters.grape_variety)
      )
    }

    // Wine type filter
    if (filters.wine_type) {
      filtered = filtered.filter(producer => 
        producer.wine_types.includes(filters.wine_type)
      )
    }

    // State/province filter
    if (filters.state) {
      filtered = filtered.filter(producer => 
        producer.state_province === filters.state
      )
    }

    // Open for visits filter
    if (filters.open_for_visits) {
      if (filters.open_for_visits === 'yes') {
        filtered = filtered.filter(producer => producer.open_for_visits)
      } else if (filters.open_for_visits === 'no') {
        filtered = filtered.filter(producer => !producer.open_for_visits)
      }
    }

    setFilteredProducers(filtered)
  }

  const clearFilters = () => {
    setFilters({
      grape_variety: '',
      wine_type: '',
      state: '',
      open_for_visits: ''
    })
  }

  const updateFilter = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }))
  }

  const createPopupContent = (producer) => {
    const socialLinks = []
    
    // Website
    if (producer.website) {
      socialLinks.push(
        `<a href="${producer.website}" target="_blank" rel="noopener" title="Website">
          <i class="fas fa-globe" style="color: #1976D2; margin-right: 8px;"></i>
        </a>`
      )
    }

    // Social media
    producer.social_media.forEach(link => {
      if (link.includes('facebook.com')) {
        socialLinks.push(`<a href="${link}" target="_blank" rel="noopener" title="Facebook"><i class="fab fa-facebook" style="color: #1877F2; margin-right: 8px;"></i></a>`)
      } else if (link.includes('instagram.com')) {
        socialLinks.push(`<a href="${link}" target="_blank" rel="noopener" title="Instagram"><i class="fab fa-instagram" style="color: #E4405F; margin-right: 8px;"></i></a>`)
      } else if (link.includes('twitter.com') || link.includes('x.com')) {
        socialLinks.push(`<a href="${link}" target="_blank" rel="noopener" title="Twitter/X"><i class="fab fa-x-twitter" style="color: #000000; margin-right: 8px;"></i></a>`)
      }
    })

    return `
      <div style="max-width: 280px; font-family: system-ui;">
        <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600;">${producer.name}</h3>
        
        ${producer.wine_label && producer.wine_label !== producer.name ? 
          `<div style="font-size: 12px; color: #666; margin-bottom: 8px;"><strong>Label:</strong> ${producer.wine_label}</div>` : ''}
        
        <div style="font-size: 13px; color: #555; margin-bottom: 12px;">
          📍 ${producer.city}, ${producer.state_province}
        </div>
        
        ${producer.grape_varieties.length > 0 ? `
          <div style="margin-bottom: 10px;">
            <div style="font-size: 12px; font-weight: 600; margin-bottom: 4px; color: #333;">🍇 Grape Varieties:</div>
            <div style="font-size: 11px; line-height: 1.3;">
              ${producer.grape_varieties.slice(0, 6).map(variety => {
                const isHighlighted = filters.grape_variety === variety
                return `<span style="background-color: ${isHighlighted ? '#007bff' : '#f1f3f4'}; color: ${isHighlighted ? 'white' : '#333'}; padding: 2px 6px; border-radius: 3px; margin-right: 4px; margin-bottom: 2px; display: inline-block; font-size: 10px;">${variety}</span>`
              }).join('')}
              ${producer.grape_varieties.length > 6 ? `<span style="color: #666; font-size: 10px;">+${producer.grape_varieties.length - 6} more</span>` : ''}
            </div>
          </div>` : ''}
        
        ${producer.wine_types.length > 0 ? `
          <div style="margin-bottom: 10px;">
            <div style="font-size: 12px; font-weight: 600; margin-bottom: 4px; color: #333;">🍷 Wine Types:</div>
            <div style="font-size: 11px; color: #555;">
              ${producer.wine_types.join(', ')}
            </div>
          </div>` : ''}
        
        ${producer.activities.length > 0 ? `
          <div style="margin-bottom: 10px;">
            <div style="font-size: 12px; font-weight: 600; margin-bottom: 4px; color: #333;">👥 Activities:</div>
            <div style="font-size: 11px; color: #555;">
              ${producer.activities.join(', ')}
            </div>
          </div>` : ''}
        
        ${socialLinks.length > 0 ? `
          <div style="border-top: 1px solid #eee; padding-top: 8px; margin-top: 8px;">
            ${socialLinks.join('')}
          </div>` : ''}
      </div>
    `
  }

  if (loading) {
    return (
      <div className="fullscreen-map-overlay">
        <div className="fullscreen-map-container">
          <div className="map-header">
            <h2>🗺️ Wine Producers Map</h2>
            <button className="close-button" onClick={onClose}>✕</button>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
            Loading map data...
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="fullscreen-map-overlay">
        <div className="fullscreen-map-container">
          <div className="map-header">
            <h2>🗺️ Wine Producers Map</h2>
            <button className="close-button" onClick={onClose}>✕</button>
          </div>
          <div style={{ padding: '20px', textAlign: 'center', color: '#d32f2f' }}>
            <h3>Map Loading Error</h3>
            <p>{error}</p>
            <p>Please try refreshing the page.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fullscreen-map-overlay">
      <div className="fullscreen-map-container">
        {/* Header with title and close button */}
        <div className="map-header">
          <div className="header-navigation">
            <div className="breadcrumb">
              <span className="breadcrumb-item">🍇 Grape Geek</span>
              <span className="breadcrumb-separator">›</span>
              <span className="breadcrumb-item">{initialVariety || 'All Varieties'}</span>
              <span className="breadcrumb-separator">›</span>
              <span className="breadcrumb-current">🗺️ Producer Map</span>
            </div>
            <div className="winegrower-count">
              {filteredProducers.length} of {allProducers.length} producers
            </div>
          </div>
          <button className="close-button" onClick={onClose} title="Back to variety page">✕</button>
        </div>
        
        {/* Filter Bar */}
        <div className="map-filters-bar">
          <div className="filter-group">
            <label htmlFor="grape-variety-filter">Grape Variety:</label>
            <select 
              id="grape-variety-filter"
              value={filters.grape_variety}
              onChange={(e) => updateFilter('grape_variety', e.target.value)}
            >
              <option value="">All grape varieties</option>
              {filterOptions.grape_varieties.map(variety => (
                <option key={variety} value={variety}>{variety}</option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label htmlFor="wine-type-filter">Wine Type:</label>
            <select 
              id="wine-type-filter"
              value={filters.wine_type}
              onChange={(e) => updateFilter('wine_type', e.target.value)}
            >
              <option value="">All wine types</option>
              {filterOptions.wine_types.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label htmlFor="state-filter">State/Province:</label>
            <select 
              id="state-filter"
              value={filters.state}
              onChange={(e) => updateFilter('state', e.target.value)}
            >
              <option value="">All states/provinces</option>
              {filterOptions.states_provinces.map(state => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label htmlFor="open-for-visits-filter">Open for Visits:</label>
            <select 
              id="open-for-visits-filter"
              value={filters.open_for_visits}
              onChange={(e) => updateFilter('open_for_visits', e.target.value)}
            >
              <option value="">All winegrowers</option>
              <option value="yes">Open for visits</option>
              <option value="no">Not open for visits</option>
            </select>
          </div>
          
          <button className="clear-filters" onClick={clearFilters}>Clear</button>
        </div>
        
        {/* Map */}
        <div className="map-container">
          <MapContainer
            ref={mapRef}
            style={{ height: '100%', width: '100%' }}
            center={[45.0, -85.0]}
            zoom={4}
            zoomControl={true}
            scrollWheelZoom={true}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='© OpenStreetMap contributors'
            />
            
            <MapController 
              producers={allProducers} 
              selectedProducers={filteredProducers}
            />
            
            {filteredProducers.map((producer) => (
              <Marker
                key={producer.id}
                position={[producer.coordinates[1], producer.coordinates[0]]}
                icon={producer.open_for_visits ? greenIcon : yellowIcon}
              >
                <Popup>
                  <div dangerouslySetInnerHTML={{ __html: createPopupContent(producer) }} />
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
        
        {/* Legend & Quick Actions */}
        <div className="map-footer">
          <div className="map-legend">
            <div className="legend-item">
              <div className="legend-marker" style={{ backgroundColor: '#2E7D32' }}></div>
              <span>Open for visits</span>
            </div>
            <div className="legend-item">
              <div className="legend-marker" style={{ backgroundColor: '#FFC107' }}></div>
              <span>Not open for visits</span>
            </div>
          </div>
          
          <div className="quick-actions">
            <button 
              className="quick-action-btn"
              onClick={onClose}
              title="Back to variety details"
            >
              ← Back to {initialVariety || 'Varieties'}
            </button>
            {initialVariety && (
              <button 
                className="quick-action-btn secondary"
                onClick={() => clearFilters()}
                title="View all winegrowers"
              >
                🌍 View All Producers
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default FullScreenMap