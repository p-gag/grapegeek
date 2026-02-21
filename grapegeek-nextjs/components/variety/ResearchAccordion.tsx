'use client';

import type { GrapeVariety } from '@/lib/types';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface ResearchAccordionProps {
  variety: GrapeVariety;
  locale: Locale;
}

export default function ResearchAccordion({ variety, locale }: ResearchAccordionProps) {
  const t = createTranslator(locale);

  return (
    <div className="research-accordion">
      <div className="section-header">
        <h2>📚 {t('variety.research.title')}</h2>
        <p>{t('variety.research.subtitle')}</p>
      </div>

      {/* Coming Soon Placeholder */}
      <div className="coming-soon">
        <div className="coming-soon-icon">🔬</div>
        <h3>{t('variety.research.comingSoonTitle')}</h3>
        <p>
          {t('variety.research.comingSoonText', { variety: variety.name })}
        </p>
        <p style={{ fontSize: '0.9rem', fontStyle: 'italic', marginTop: '1rem' }}>
          {t('variety.research.comingSoonSubtext')}
        </p>
      </div>
    </div>
  );
}
