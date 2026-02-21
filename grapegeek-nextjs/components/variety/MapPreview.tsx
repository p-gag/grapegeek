'use client';

import dynamic from 'next/dynamic';
import Link from 'next/link';
import type { GrapeVariety } from '@/lib/types';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface MapPreviewProps {
  variety: GrapeVariety;
  locale: Locale;
}

// Create the entire map component dynamically to avoid SSR issues with hooks
const DynamicMapView = dynamic(
  () => import('./MapPreviewLeaflet'),
  {
    ssr: false,
    loading: () => (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
        Loading map...
      </div>
    )
  }
);

export default function MapPreview({ variety, locale }: MapPreviewProps) {
  const t = createTranslator(locale);

  return (
    <div className="preview-section">
      <div className="preview-header">
        <h2>🗺️ {t('variety.map.title')}</h2>
        <p>{t('variety.map.subtitle', { variety: variety.name })}</p>
      </div>

      <div className="map-preview-container">
        <div className="map-rectangle">
          <DynamicMapView variety={variety} />

          <div className="map-invitation">
            <div className="invitation-text">{t('variety.map.explore')}</div>
            <div className="invitation-arrow">→</div>
          </div>
        </div>

        <Link
          href={`/${locale}/map?variety=${encodeURIComponent(variety.name)}`}
          className="map-overlay-button"
          aria-label={t('variety.map.openMap')}
        >
          <span className="sr-only">{t('variety.map.openMap')}</span>
        </Link>
      </div>
    </div>
  );
}
