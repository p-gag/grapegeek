'use client';

import { useRouter } from 'next/navigation';
import type { Winegrower } from '@/lib/types';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface WinegrowerVarietiesProps {
  winegrower: Winegrower;
  varietyPhotos?: { [varietyName: string]: string };
  locale: Locale;
}

export default function WinegrowerVarieties({ winegrower, varietyPhotos = {}, locale }: WinegrowerVarietiesProps) {
  const t = createTranslator(locale);
  const router = useRouter();

  const handleVarietyClick = (varietyName: string) => {
    router.push(`/${locale}/varieties/${encodeURIComponent(varietyName)}`);
  };

  const getVarietyImage = (varietyName: string) => {
    // Return photo URL if available, null if not
    return varietyPhotos[varietyName] || null;
  };

  const hasPhoto = (varietyName: string) => {
    return !!varietyPhotos[varietyName];
  };

  // Get unique varieties from wines
  const varieties = Array.from(
    new Set(
      winegrower.wines?.flatMap(wine =>
        wine.grapes.map(g => g.variety_name)
      ) || []
    )
  ).sort();

  if (varieties.length === 0) {
    return (
      <div className="winegrower-varieties-empty">
        <div className="empty-state">
          <div className="empty-icon">🍇</div>
          <p>{t('winegrower.varieties.empty')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="winegrower-varieties-compact">
      <h3 className="varieties-title">{t('winegrower.varieties.title')}</h3>

      <div className="varieties-grid-compact">
        {varieties.map((variety, index) => (
          <div
            key={`${variety}-${index}`}
            className="variety-card-compact"
            onClick={() => handleVarietyClick(variety)}
          >
            <div className="variety-content">
              <div className="variety-image-compact">
                {hasPhoto(variety) ? (
                  <img
                    src={getVarietyImage(variety)!}
                    alt={`${variety} grape cluster`}
                    className="variety-photo"
                    crossOrigin="anonymous"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = `https://via.placeholder.com/200x267/8B5CF6/FFFFFF?text=${encodeURIComponent(variety)}`;
                    }}
                  />
                ) : (
                  <div className="variety-photo-placeholder">
                    <div className="placeholder-icon">🍇</div>
                    <div className="placeholder-text">{t('winegrower.varieties.noPhoto')}</div>
                  </div>
                )}
              </div>
              <div className="variety-info-compact">
                <h4 className="variety-name">{variety}</h4>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
