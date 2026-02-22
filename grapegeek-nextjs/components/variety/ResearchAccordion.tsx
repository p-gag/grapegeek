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

      <p className="text-gray-500 italic text-sm mt-4 text-center">
        {t('variety.research.comingSoonText', { variety: variety.name })}
      </p>
    </div>
  );
}
