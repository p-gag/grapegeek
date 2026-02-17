import GrapePhotos from '../components/GrapePhotos'
import GrapeInfo from '../components/GrapeInfo'
import MapPreviewLeaflet from '../components/MapPreviewLeaflet'
import TreePreviewReactFlow from '../components/TreePreviewReactFlow'
import ResearchAccordion from '../components/ResearchAccordion'
import SectionNav from '../components/SectionNav'
import DataDisclaimer from '../components/DataDisclaimer'

const GrapeVarietyPage = ({ variety }) => {
  return (
    <div className="grape-variety-page">
      {/* Hero Section with Photo */}
      <section id="overview" className="hero-section">
        <div className="hero-content">
          <div className="hero-header">
            <h1 className="variety-title">{variety.name}</h1>
            <p className="variety-tagline">{variety.summary}</p>
          </div>
          
          <div className="hero-grid">
            <GrapePhotos variety={variety} photos={variety.photos} />
            <GrapeInfo variety={variety} />
          </div>
        </div>
      </section>

      {/* Sticky Section Navigation */}
      <SectionNav />
      
      {/* Map and Tree Adaptive Layout */}
      <div className="adaptive-previews-container">
        {/* Map Preview Section */}
        <section id="map" className="section-preview adaptive-preview">
          <div className="section-content">
            <MapPreviewLeaflet variety={variety} />
          </div>
        </section>
        
        {/* Family Tree Preview Section */}
        <section id="tree" className="section-preview adaptive-preview">
          <div className="section-content">
            <TreePreviewReactFlow variety={variety} />
          </div>
        </section>
      </div>
      
      {/* Research Section */}
      <section id="research" className="section-research">
        <div className="section-content">
          <ResearchAccordion variety={variety} />
        </div>
      </section>

      {/* Photo Credits Section */}
      <section id="photo-credits" className="photo-credits-section">
        <div className="section-content">
          <p className="credits-text">
            <strong>Photo Credits:</strong> Cluster in field photograph by Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY. Source: <a href="http://www.vivc.de" target="_blank" rel="noopener noreferrer">VIVC</a>
          </p>
        </div>
      </section>

      {/* Footer: Data Disclaimer */}
      <DataDisclaimer type="variety" />
    </div>
  )
}

export default GrapeVarietyPage