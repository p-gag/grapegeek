const MapPreview = ({ variety }) => {
  const handleOpenMap = () => {
    // TODO: Navigate to full-screen map
    console.log('Opening full-screen map for', variety.name)
  }

  return (
    <div className="preview-section">
      <div className="preview-header">
        <h2>🗺️ Where It Grows</h2>
        <p>Wineries and vineyards growing {variety.name} across North America</p>
      </div>
      
      <div className="map-preview-container">
        <div className="map-rectangle">
          <div className="static-map">
            <div className="map-background">
              <div className="map-overlay">
                <div className="region-cluster canada">
                  <div className="region-name">🍁 CANADA</div>
                  <div className="province-group nova-scotia">
                    <div className="province-label">Nova Scotia</div>
                    <div className="winegrower-markers">
                      <div className="marker large">●</div>
                      <div className="marker large">●</div>
                      <div className="marker medium">●</div>
                      <div className="marker medium">●</div>
                      <div className="marker small">●</div>
                    </div>
                  </div>
                </div>
                
                <div className="region-cluster usa">
                  <div className="region-name">🇺🇸 USA</div>
                  <div className="state-group vermont">
                    <div className="state-label">Vermont</div>
                    <div className="winegrower-markers">
                      <div className="marker medium">●</div>
                      <div className="marker small">●</div>
                    </div>
                  </div>
                  <div className="state-group ontario">
                    <div className="state-label">Ontario</div>
                    <div className="winegrower-markers">
                      <div className="marker small">●</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="map-stats">
                <div className="stat-badge">
                  <span className="stat-number">{variety.producer_count}</span>
                  <span className="stat-label">Winegrowers</span>
                </div>
              </div>
              
              <div className="map-invitation">
                <div className="invitation-text">Click to explore interactive map with filters, winegrower details & more</div>
                <div className="invitation-arrow">→</div>
              </div>
            </div>
          </div>
        </div>
        
        <button 
          className="map-overlay-button"
          onClick={handleOpenMap}
          aria-label="Open interactive map"
        >
          <span className="sr-only">Open Interactive Map</span>
        </button>
      </div>
    </div>
  )
}

export default MapPreview