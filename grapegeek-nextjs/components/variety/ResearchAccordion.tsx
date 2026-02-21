'use client';

import type { GrapeVariety } from '@/lib/types';

interface ResearchAccordionProps {
  variety: GrapeVariety;
}

export default function ResearchAccordion({ variety }: ResearchAccordionProps) {
  return (
    <div className="research-accordion">
      <div className="section-header">
        <h2>📚 Technical Research</h2>
        <p>Comprehensive grape variety analysis</p>
      </div>

      {/* Coming Soon Placeholder */}
      <div className="coming-soon">
        <div className="coming-soon-icon">🔬</div>
        <h3>Research Content Coming Soon</h3>
        <p>
          We&apos;re working on comprehensive technical research for {variety.name}, including viticulture characteristics,
          winemaking notes, academic citations, and historical information.
        </p>
        <p style={{ fontSize: '0.9rem', fontStyle: 'italic', marginTop: '1rem' }}>
          This section will include detailed analysis with citations from academic sources, industry publications,
          and grower reports.
        </p>
      </div>
    </div>
  );
}
