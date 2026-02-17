const RelatedVarieties = ({ variety }) => {
  return (
    <div className="related-varieties">
      <div style={{ marginBottom: '1.5rem' }}>
        <h4>Similar Varieties</h4>
        <div className="variety-tags">
          {variety.similar_varieties.map(varietyName => (
            <a key={varietyName} href="#" className="variety-tag">
              {varietyName}
            </a>
          ))}
        </div>
      </div>
      
      <div>
        <h4>Same Parents</h4>
        <div className="variety-tags">
          {variety.parent_crosses.map(cross => (
            <a key={cross} href="#" className="variety-tag">
              {cross}
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RelatedVarieties