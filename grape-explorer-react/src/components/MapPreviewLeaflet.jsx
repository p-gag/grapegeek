import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import { useMapData, greenIcon, yellowIcon } from '../hooks/useMapData'
import 'leaflet/dist/leaflet.css'

// Fix for default markers in Vite
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Component to fit map bounds to markers
const FitBounds = ({ producers }) => {
  const map = useMap()
  
  useEffect(() => {
    if (producers && producers.length > 0) {
      const bounds = L.latLngBounds(producers.map(p => [p.coordinates[1], p.coordinates[0]]))
      map.fitBounds(bounds, { padding: [20, 20] })
    }
  }, [map, producers])
  
  return null
}

const MapPreviewLeaflet = ({ variety }) => {
  const navigate = useNavigate()
  const { loading, error, getVarietyProducers } = useMapData(variety.name)
  
  // Get producers for this variety
  const varietyProducers = getVarietyProducers(variety.name)

  const handleOpenFullMap = () => {
    console.log('Opening map for variety:', variety.name)
    // Navigate to full map page with variety parameter
    navigate(`/map?variety=${encodeURIComponent(variety.name)}`)
  }

  if (loading) {
    return (
      <div className="preview-section">
        <div className="preview-header">
          <h2>🗺️ Where It Grows</h2>
          <p>Wineries and vineyards growing {variety.name} across North America</p>
        </div>
        <div className="map-preview-container">
          <div className="map-rectangle" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>Loading map data...</div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="preview-section">
        <div className="preview-header">
          <h2>🗺️ Where It Grows</h2>
          <p>Wineries and vineyards growing {variety.name} across North America</p>
        </div>
        <div className="map-preview-container">
          <div className="map-rectangle" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>Error loading map: {error}</div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="preview-section">
      <div className="preview-header">
        <h2>🗺️ Where It Grows</h2>
        <p>Wineries and vineyards growing {variety.name} across North America</p>
      </div>
      
      <div className="map-preview-container">
        <div className="map-rectangle">
          <MapContainer
            style={{ height: '400px', width: '100%', borderRadius: '16px' }}
            center={[45.0, -85.0]}
            zoom={4}
            zoomControl={false}
            scrollWheelZoom={false}
            dragging={false}
            touchZoom={false}
            doubleClickZoom={false}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='© OpenStreetMap contributors'
            />
            
            <FitBounds producers={varietyProducers} />
            
            {varietyProducers.map((producer) => (
              <Marker
                key={producer.id}
                position={[producer.coordinates[1], producer.coordinates[0]]}
                icon={producer.open_for_visits ? greenIcon : yellowIcon}
                interactive={false}
              />
            ))}
          </MapContainer>
          
          <div className="map-stats">
            <div className="stat-badge">
              <span className="stat-number">{varietyProducers.length}</span>
              <span className="stat-label">Winegrowers</span>
            </div>
          </div>

          <div className="map-invitation">
            <div className="invitation-text">
              Explore interactive winegrower map
            </div>
            <div className="invitation-arrow">→</div>
          </div>
        </div>
        
        <button 
          className="map-overlay-button"
          onClick={handleOpenFullMap}
          aria-label="Open interactive map"
        >
          <span className="sr-only">Open Interactive Map</span>
        </button>
      </div>

    </div>
  )
}

export default MapPreviewLeaflet