const WinegrowerVarieties = ({ producer }) => {
  const handleVarietyClick = (varietyName) => {
    const formattedName = varietyName.toLowerCase().replace(/\s+/g, '-')
    window.location.href = `/variety/${formattedName}`
  }

  const getVarietyImage = (varietyName) => {
    // Use Acadie Blanc cluster image for all varieties as mock
    // In real implementation, this would map to actual variety images
    if (varietyName.toLowerCase().includes('acadie')) {
      return '/photos/vivc_17638_Cluster_in_the_field_17107k.jpg'
    }
    // Default to Acadie Blanc image for other varieties as mock
    return '/photos/vivc_17638_Cluster_in_the_field_17107k.jpg'
  }

  if (!producer.grape_varieties || producer.grape_varieties.length === 0) {
    return (
      <div className="winegrower-varieties-empty">
        <div className="empty-state">
          <div className="empty-icon">🍇</div>
          <p>No grape varieties listed for this winegrower</p>
        </div>
      </div>
    )
  }

  const sortedVarieties = [...producer.grape_varieties].sort()

  return (
    <div className="winegrower-varieties-compact">
      <h3 className="varieties-title">Grape Varieties Grown Here</h3>

      <div className="varieties-grid-compact">
        {sortedVarieties.map((variety, index) => (
          <div
            key={`${variety}-${index}`}
            className="variety-card-compact"
            onClick={() => handleVarietyClick(variety)}
          >
            <div className="variety-content">
              <div className="variety-image-compact">
                <img
                  src={getVarietyImage(variety)}
                  alt={`${variety} grape cluster`}
                  className="variety-photo"
                />
              </div>
              <div className="variety-info-compact">
                <h4 className="variety-name">{variety}</h4>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default WinegrowerVarieties