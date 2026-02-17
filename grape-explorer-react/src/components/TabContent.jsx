// Mock components for different tab views
const TreeView = () => (
  <div className="tab-content-view">
    <div className="coming-soon">
      <div className="coming-soon-icon">🌳</div>
      <h3>Interactive Family Tree</h3>
      <p>Full React Flow family tree visualization coming soon...</p>
      <div className="mockup-preview">
        <div style={{ fontSize: '0.9rem', textAlign: 'center', color: '#666' }}>
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ 
              display: 'inline-block', 
              padding: '0.5rem 1rem', 
              background: '#e3f2fd', 
              borderRadius: '20px',
              margin: '0.3rem'
            }}>
              Cascade
            </div>
            <div style={{ 
              display: 'inline-block', 
              padding: '0.5rem 1rem', 
              background: '#e8f5e8', 
              borderRadius: '20px',
              margin: '0.3rem'
            }}>
              Seyve-Villard 14-287
            </div>
          </div>
          <div style={{ margin: '1rem 0', color: '#999' }}>↓</div>
          <div style={{ 
            display: 'inline-block', 
            padding: '0.8rem 1.5rem', 
            background: '#fff3e0', 
            borderRadius: '25px',
            border: '3px solid #ff9800',
            fontWeight: 'bold',
            fontSize: '1.1rem'
          }}>
            Acadie Blanc
          </div>
        </div>
      </div>
    </div>
  </div>
)

const MapView = () => (
  <div className="tab-content-view">
    <div className="coming-soon">
      <div className="coming-soon-icon">🗺️</div>
      <h3>Winegrower Map</h3>
      <p>Interactive Leaflet map with winegrower locations coming soon...</p>
      <div className="mockup-preview">
        <div style={{ fontSize: '0.9rem', textAlign: 'center', color: '#666' }}>
          <div style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>🍁 Canada</div>
          <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '1rem' }}>
            <span style={{ color: '#007bff', fontSize: '1.5rem' }}>●●●●●</span>
            <span style={{ fontWeight: 'bold' }}>Nova Scotia</span>
          </div>
          <div style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>🇺🇸 USA</div>
          <div style={{ display: 'flex', justifyContent: 'space-around' }}>
            <span style={{ color: '#28a745', fontSize: '1.2rem' }}>●●</span>
            <span>Vermont</span>
            <span style={{ color: '#ffc107', fontSize: '1rem' }}>●</span>
            <span>Ontario</span>
          </div>
        </div>
      </div>
    </div>
  </div>
)

const ResearchView = () => (
  <div className="tab-content-view">
    <div className="coming-soon">
      <div className="coming-soon-icon">📚</div>
      <h3>Research Content</h3>
      <p>Comprehensive technical research with citations coming soon...</p>
      <div className="mockup-preview research-preview">
        <div style={{ textAlign: 'left', fontSize: '0.9rem', lineHeight: '1.6' }}>
          <div style={{ marginBottom: '1rem' }}>
            <h4 style={{ color: '#495057', marginBottom: '0.5rem' }}>1. Overview</h4>
            <p style={{ color: '#666' }}>White, cold-climate hybrid, best known under the Nova Scotia spelling L'Acadie Blanc...</p>
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <h4 style={{ color: '#495057', marginBottom: '0.5rem' }}>2. Origin & Breeding</h4>
            <p style={{ color: '#666' }}>Most sources point to Ollie A. Bradt at the Vineland Horticultural Research Station...</p>
          </div>
          <div style={{ color: '#007bff', fontSize: '0.8rem', fontStyle: 'italic' }}>
            + 8 more detailed sections with 40+ citations
          </div>
        </div>
      </div>
    </div>
  </div>
)

const TabContent = ({ activeTab, variety }) => {
  switch (activeTab) {
    case 'tree':
      return <TreeView />
    case 'map':
      return <MapView />
    case 'research':
      return <ResearchView />
    case 'overview':
    default:
      return null // Overview is handled by the main page content
  }
}

export default TabContent