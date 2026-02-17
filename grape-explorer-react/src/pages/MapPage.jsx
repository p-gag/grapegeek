import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import { createRoot } from 'react-dom/client'
import L from 'leaflet'
import Header from '../components/Header'
import WinegrowerCard from '../components/WinegrowerCard'
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

const greenIcon = createCustomIcon('#2E7D32')
const yellowIcon = createCustomIcon('#FFC107')

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

const MapPage = () => {
  const { variety } = useParams() // From /variety/:slug/map routes
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  
  // Get variety from URL params or search params
  const currentVariety = variety || searchParams.get('variety')
  
  const [mapData, setMapData] = useState(null)
  const [allProducers, setAllProducers] = useState([])
  const [filteredProducers, setFilteredProducers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Filter states from URL params
  const [filters, setFilters] = useState({
    grape_variety: currentVariety || '',
    wine_type: searchParams.get('wine_type') || '',
    state: searchParams.get('state') || '',
    open_for_visits: searchParams.get('open_for_visits') || ''
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
        
        // Apply initial filters
        if (currentVariety && data.varieties[currentVariety]) {
          setFilteredProducers(data.varieties[currentVariety].producers)
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
  }, [currentVariety])

  useEffect(() => {
    applyFilters()
    updateURL()
  }, [filters, allProducers])

  const applyFilters = () => {
    if (!allProducers.length) return

    let filtered = [...allProducers]

    if (filters.grape_variety) {
      filtered = filtered.filter(producer => 
        producer.grape_varieties.includes(filters.grape_variety)
      )
    }

    if (filters.wine_type) {
      filtered = filtered.filter(producer => 
        producer.wine_types.includes(filters.wine_type)
      )
    }

    if (filters.state) {
      filtered = filtered.filter(producer => 
        producer.state_province === filters.state
      )
    }

    if (filters.open_for_visits) {
      if (filters.open_for_visits === 'yes') {
        filtered = filtered.filter(producer => producer.open_for_visits)
      } else if (filters.open_for_visits === 'no') {
        filtered = filtered.filter(producer => !producer.open_for_visits)
      }
    }

    setFilteredProducers(filtered)
  }

  const updateURL = () => {
    const params = new URLSearchParams()
    if (filters.grape_variety) params.set('variety', filters.grape_variety)
    if (filters.wine_type) params.set('wine_type', filters.wine_type)
    if (filters.state) params.set('state', filters.state)
    if (filters.open_for_visits) params.set('open_for_visits', filters.open_for_visits)
    setSearchParams(params)
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

  const handleBackClick = () => {
    if (currentVariety) {
      // Go back to the specific variety page
      const varietySlug = currentVariety.toLowerCase().replace(/\s+/g, '-')
      navigate(`/variety/${varietySlug}`)
    } else {
      // Go back to the previous page or home
      navigate(-1)
    }
  }

  if (loading) {
    return (
      <div className="app">
        <Header showBackLink={true} />
        <div className="map-page">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
            Loading map data...
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app">
        <Header showBackLink={true} />
        <div className="map-page">
          <div style={{ padding: '20px', textAlign: 'center', color: '#d32f2f' }}>
            <h3>Map Loading Error</h3>
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>Try Again</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <Header showBackLink={true} />
      
      <div className="map-page">
        {/* Main Content with Sidebar */}
        <div className="map-main-content">
          {/* Left Sidebar Panel */}
          <div className="map-sidebar">
            {/* Breadcrumb Navigation */}
            <div className="sidebar-breadcrumb">
              <button onClick={() => navigate('/')} className="breadcrumb-link">
                🍇 Grape Geek
              </button>
              <span className="breadcrumb-separator">›</span>
              {currentVariety && (
                <>
                  <button onClick={handleBackClick} className="breadcrumb-link">
                    {currentVariety}
                  </button>
                  <span className="breadcrumb-separator">›</span>
                </>
              )}
              <span className="breadcrumb-current">Map</span>
            </div>

            {/* Sidebar Header */}
            <div className="sidebar-header">
              <h1>🗺️ Winegrower Map</h1>
              <div className="winegrower-count">
                <span className="count-number">{filteredProducers.length}</span>
                <span className="count-label">of {allProducers.length} winegrowers</span>
                {currentVariety && (
                  <div className="variety-context">
                    growing <strong>{currentVariety}</strong>
                  </div>
                )}
              </div>
            </div>
            
            {/* Filters Section */}
            <div className="sidebar-filters">
              <h3 className="filters-title">Filters</h3>
              
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
              
              <button className="clear-filters-btn" onClick={clearFilters}>
                Clear All Filters
              </button>
            </div>

            {/* Legend */}
            <div className="sidebar-legend">
              <h3 className="legend-title">Legend</h3>
              <div className="legend-items">
                <div className="legend-item">
                  <div className="legend-dot green"></div>
                  <span>Open for visits</span>
                </div>
                <div className="legend-item">
                  <div className="legend-dot yellow"></div>
                  <span>Not open for visits</span>
                </div>
              </div>
            </div>
          </div>

          {/* Map Container */}
          <div className="map-content">
            <MapContainer
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
                <Popup 
                  maxWidth={400}
                  minWidth={320}
                  className="winegrower-popup"
                >
                  <WinegrowerCard
                    producer={producer}
                    selectedVariety={currentVariety}
                  />
                </Popup>
              </Marker>
            ))}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MapPage