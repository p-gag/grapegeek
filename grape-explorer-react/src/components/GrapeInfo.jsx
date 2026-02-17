const GrapeInfo = ({ variety }) => {
  return (
    <div className="grape-info">
      {/* Key Details */}
      <div className="grape-details">
        <div className="detail-row">
          <span className="detail-label">Bred</span>
          <span className="detail-value">{variety.year_of_crossing} by {variety.breeder}</span>
        </div>
        
        <div className="detail-row">
          <span className="detail-label">Parents</span>
          <span className="detail-value">
            {variety.parents.map((parent, index) => (
              <span key={parent}>
                <span className="parent-link">{parent}</span>
                {index < variety.parents.length - 1 && <span> × </span>}
              </span>
            ))}
          </span>
        </div>
        
        <div className="detail-row">
          <span className="detail-label">Species</span>
          <span className="detail-value">{variety.species}</span>
        </div>
        
        <div className="detail-row">
          <span className="detail-label">Known for</span>
          <span className="detail-value">{variety.known_for}</span>
        </div>
        
        <div className="detail-row">
          <span className="detail-label">VIVC Number</span>
          <span className="detail-value">#{variety.vivc_number}</span>
        </div>
      </div>

      {/* Quick Stats Card */}
      <div className="quick-stats-card">
        <h4>Quick Stats</h4>
        
        <div className="stat-grid">
          <div className="stat-item">
            <div className="stat-icon">🏭</div>
            <div className="stat-content">
              <span className="stat-number">{variety.producer_count}</span>
              <span className="stat-label">North American Producers</span>
            </div>
          </div>
          
          <div className="stat-item">
            <div className="stat-icon">🌡️</div>
            <div className="stat-content">
              <span className="stat-number">{variety.hardiness}</span>
              <span className="stat-label">Cold Hardiness</span>
            </div>
          </div>
          
          <div className="stat-item">
            <div className="stat-icon">🍷</div>
            <div className="stat-content">
              <span className="stat-number">{variety.wine_styles.length}</span>
              <span className="stat-label">Wine Styles</span>
              <span className="stat-detail">{variety.wine_styles.join(', ')}</span>
            </div>
          </div>
          
          <div className="stat-item">
            <div className="stat-icon">🗓️</div>
            <div className="stat-content">
              <span className="stat-number">{variety.ripening_season}</span>
              <span className="stat-label">Ripening Season</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GrapeInfo