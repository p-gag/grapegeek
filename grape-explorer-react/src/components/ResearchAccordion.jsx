import { useState } from 'react'

const ResearchAccordion = ({ variety }) => {
  const [openSections, setOpenSections] = useState(['overview']) // Start with overview open

  const toggleSection = (sectionId) => {
    setOpenSections(prev => 
      prev.includes(sectionId) 
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    )
  }

  const researchSections = [
    {
      id: 'overview',
      title: '1. Overview',
      icon: '🍇',
      content: `White, cold-climate hybrid, best known under the Nova Scotia spelling L'Acadie Blanc. Bred in Ontario but widely planted in Nova Scotia, with smaller footholds in Québec and Ontario; many winegrowers there call it the province's "signature" white and a cornerstone of Tidal Bay blends.`
    },
    {
      id: 'origin',
      title: '2. Origin & Breeding',
      icon: '🧬',
      content: `Most sources point to Ollie A. (O.A.) Bradt at the Vineland Horticultural Research Station (now Vineland Research & Innovation Centre) in Niagara, Ontario, who created the cross in 1953 from Cascade (Seibel 13053) × Seyve‑Villard 14‑287.`
    },
    {
      id: 'climate',
      title: '3. Climate Adaptation & Hardiness',
      icon: '🌡️',
      content: `Hardiness claims range depending on location and site exposure. Bishop's Cellar reports "cold hardy variety can survive to −25°C," with loose bunches that make organic growing more feasible. Vermont nurseries report cold hardy to around −20°F (≈ −29°C).`
    },
    {
      id: 'viticulture',
      title: '4. Viticulture & Growing',
      icon: '🌱',
      content: `Multiple sources describe upright, VSP‑friendly architecture with moderate vigor. Northeastern Vine Supply notes "very upright growth lend this selection to vertical shoot position training," with small leaves and approximately 90g cluster mass.`
    },
    {
      id: 'disease',
      title: '5. Disease Resistance',
      icon: '🛡️',
      content: `Nursery and regional sources often describe L'Acadie's loose clusters and relative resilience to common mildews. VineTech describes it as "resistant to downy mildew and powdery mildew," with reduced botrytis risk from looser bunches.`
    },
    {
      id: 'winemaking',
      title: '6. Winemaking Approaches',
      icon: '🍷',
      content: `Producers utilize multiple approaches: traditional‑method sparkling with extended tirage, Charmat and pét‑nat styles, still wines with oak fermentation, and as a key component in Nova Scotia's Tidal Bay appellation blends.`
    },
    {
      id: 'research-questions',
      title: '7. Open Questions',
      icon: '❓',
      content: `Several areas need further research: precise hardiness thresholds across different sites, acid retention behavior in varying climates, and comprehensive disease susceptibility data compared to other cold-climate hybrids.`
    }
  ]

  return (
    <div className="research-accordion">
      <div className="section-header">
        <h2>📚 Technical Research</h2>
        <p>Comprehensive analysis with {variety.citation_count}+ citations</p>
      </div>
      
      <div className="accordion-container">
        {researchSections.map(section => (
          <div 
            key={section.id} 
            className={`accordion-item ${openSections.includes(section.id) ? 'open' : ''}`}
          >
            <button 
              className="accordion-header"
              onClick={() => toggleSection(section.id)}
            >
              <div className="accordion-title">
                <span className="section-icon">{section.icon}</span>
                <span className="section-title">{section.title}</span>
              </div>
              <span className="accordion-chevron">
                {openSections.includes(section.id) ? '−' : '+'}
              </span>
            </button>
            
            {openSections.includes(section.id) && (
              <div className="accordion-content">
                <div className="content-text">
                  {section.content}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="research-footer">
        <p className="citation-note">
          Research compiled from academic sources, industry publications, and grower reports. 
          See full citations in expanded sections.
        </p>
        <div className="research-stats">
          <span className="stat">📄 {variety.citation_count}+ Sources</span>
          <span className="stat">📊 Industry Data</span>
        </div>
      </div>
    </div>
  )
}

export default ResearchAccordion