const TreePreview = ({ variety }) => {
  const handleOpenTree = () => {
    // TODO: Navigate to full-screen tree explorer
    console.log('Opening family tree explorer for', variety.name)
  }

  return (
    <div className="preview-section">
      <div className="preview-header">
        <h2>🌳 Family Tree</h2>
        <p>Explore the genealogy and parentage of {variety.name}</p>
      </div>
      
      <div className="preview-content landscape">
        <div className="preview-visual tree-visual">
          <div className="tree-mockup">
            <div className="tree-level parents">
              <div className="parent-node cascade">
                <div className="node-content">
                  <div className="node-name">Cascade</div>
                  <div className="node-species">V. riparia × labrusca</div>
                </div>
              </div>
              
              <div className="parent-node seyve-villard">
                <div className="node-content">
                  <div className="node-name">Seyve-Villard 14-287</div>
                  <div className="node-species">V. vinifera × rupestris</div>
                </div>
              </div>
            </div>
            
            <div className="tree-connections">
              <div className="connection-line"></div>
              <div className="connection-merge"></div>
            </div>
            
            <div className="tree-level offspring">
              <div className="offspring-node acadie">
                <div className="node-content featured">
                  <div className="node-name">{variety.name}</div>
                  <div className="node-species">Interspecific Crossing</div>
                  <div className="node-year">1953</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="preview-details">
          <div className="genealogy-info">
            <h4>Parentage:</h4>
            <div className="parent-list">
              {variety.parents.map((parent, index) => (
                <span key={parent} className="parent-item">
                  {parent}
                  {index < variety.parents.length - 1 && <span className="cross"> × </span>}
                </span>
              ))}
            </div>
          </div>
          
          <div className="breeding-info">
            <h4>Breeding Program:</h4>
            <p>{variety.breeder}</p>
            <p className="year">{variety.year_of_crossing}</p>
          </div>
          
          <button 
            className="launch-button"
            onClick={handleOpenTree}
          >
            🌳 Explore Family Tree
          </button>
        </div>
      </div>
    </div>
  )
}

export default TreePreview