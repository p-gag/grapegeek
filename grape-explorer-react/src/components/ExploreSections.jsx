import { Link } from 'react-router-dom'

// Mockup preview components
const TreePreview = () => (
  <div style={{ fontSize: '0.8rem', textAlign: 'center' }}>
    <div style={{ marginBottom: '0.5rem' }}>
      <div style={{ 
        display: 'inline-block', 
        padding: '0.3rem 0.8rem', 
        background: '#e3f2fd', 
        borderRadius: '15px',
        margin: '0.2rem'
      }}>
        Cascade
      </div>
      <div style={{ 
        display: 'inline-block', 
        padding: '0.3rem 0.8rem', 
        background: '#e8f5e8', 
        borderRadius: '15px',
        margin: '0.2rem'
      }}>
        SV 14-287
      </div>
    </div>
    <div style={{ margin: '0.5rem 0', color: '#666' }}>↓</div>
    <div style={{ 
      display: 'inline-block', 
      padding: '0.4rem 1rem', 
      background: '#fff3e0', 
      borderRadius: '15px',
      border: '2px solid #ff9800',
      fontWeight: 'bold'
    }}>
      Acadie Blanc
    </div>
  </div>
)

const MapPreview = () => (
  <div style={{ fontSize: '0.8rem', textAlign: 'center' }}>
    <div style={{ marginBottom: '0.5rem', color: '#666' }}>🍁 Canada</div>
    <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '0.5rem' }}>
      <span style={{ color: '#007bff' }}>●●●●●</span>
      <span>NS</span>
    </div>
    <div style={{ marginBottom: '0.5rem', color: '#666' }}>🇺🇸 USA</div>
    <div style={{ display: 'flex', justifyContent: 'space-around' }}>
      <span style={{ color: '#28a745' }}>●●</span>
      <span>VT</span>
      <span style={{ color: '#ffc107' }}>●</span>
      <span>ON</span>
    </div>
  </div>
)

const ResearchPreview = () => (
  <div style={{ fontSize: '0.8rem', lineHeight: '1.4' }}>
    <div style={{ marginBottom: '0.8rem' }}>
      <strong>Overview:</strong> White, cold-climate hybrid, best known under the Nova Scotia spelling...
    </div>
    <div style={{ marginBottom: '0.8rem' }}>
      <strong>Origin & Breeding:</strong> Most sources point to Ollie A. Bradt...
    </div>
    <div style={{ color: '#007bff', fontSize: '0.7rem' }}>
      + 8 more detailed sections
    </div>
  </div>
)

const ExploreSections = ({ variety }) => {
  return (
    <div className="explore-sections">
      <h3>Explore {variety.name}</h3>
      
      <div className="section-cards">
        {/* Family Tree Card */}
        <Link to={`/variety/${variety.slug}/tree`} className="section-card">
          <div className="section-icon">🌳</div>
          <h4>Family Tree</h4>
          <div className="section-preview">
            <TreePreview />
          </div>
          <div className="section-details">
            <p>Parents:</p>
            <ul>
              {variety.parents.map(parent => (
                <li key={parent}>• {parent}</li>
              ))}
            </ul>
          </div>
          <div className="section-cta">→ View Interactive Tree</div>
        </Link>

        {/* Producer Map Card */}
        <Link to={`/variety/${variety.slug}/map`} className="section-card">
          <div className="section-icon">🗺️</div>
          <h4>Producers</h4>
          <div className="section-preview">
            <MapPreview />
          </div>
          <div className="section-details">
            <p>Top Regions:</p>
            <ul>
              {variety.top_regions.map(region => (
                <li key={region}>• {region}</li>
              ))}
            </ul>
          </div>
          <div className="section-cta">→ View Producer Map</div>
        </Link>

        {/* Research Card */}
        <Link to={`/variety/${variety.slug}/research`} className="section-card">
          <div className="section-icon">📚</div>
          <h4>Research</h4>
          <div className="section-preview">
            <ResearchPreview />
          </div>
          <div className="section-details">
            <p>Sections:</p>
            <ul>
              {variety.research_sections.slice(0, 3).map(section => (
                <li key={section}>• {section}</li>
              ))}
            </ul>
            <p className="citation-count">{variety.citation_count}+ citations</p>
          </div>
          <div className="section-cta">→ Read Research</div>
        </Link>
      </div>
    </div>
  )
}

export default ExploreSections