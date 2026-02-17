const DataDisclaimer = ({ type = 'variety' }) => {
  const text = type === 'variety'
    ? 'Research compiled from academic sources, industry publications, and grower reports. See full citations in expanded sections.'
    : 'Information automatically extracted from public sources. May contain errors.'

  return (
    <div className="data-disclaimer-footer">
      <div className="disclaimer-content">
        <div className="disclaimer-text">
          <i className="fas fa-info-circle"></i>
          <span>{text}</span>
        </div>
      </div>
    </div>
  )
}

export default DataDisclaimer
