const WinegrowerInfo = ({ producer }) => {
  return (
    <div className="winegrower-info-compact">
      <div className="compact-stats">
        <div className="stat-compact">
          <span className="stat-icon">🍇</span>
          <span className="stat-number">{producer.grape_varieties ? producer.grape_varieties.length : 0}</span>
          <span className="stat-label">varieties</span>
        </div>

        <div className="stat-compact">
          <span className="stat-icon">🍷</span>
          <span className="stat-number">{producer.wine_types ? producer.wine_types.length : 0}</span>
          <span className="stat-label">wine types</span>
        </div>

        <div className="stat-compact">
          <span className="stat-icon">🍾</span>
          <span className="stat-number">{producer.wines ? producer.wines.length : 0}</span>
          <span className="stat-label">wines</span>
        </div>
      </div>
    </div>
  )
}

export default WinegrowerInfo