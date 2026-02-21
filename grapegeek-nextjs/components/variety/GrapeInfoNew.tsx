'use client';

import Link from 'next/link';
import type { GrapeVariety } from '@/lib/types';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface GrapeInfoProps {
  variety: GrapeVariety & {
    // Optional fields that may not exist yet
    year_of_crossing?: number | string;
    breeder?: string;
    known_for?: string;
    hardiness?: string;
    wine_styles?: string[];
    ripening_season?: string;
  };
  locale: Locale;
}

export default function GrapeInfo({ variety, locale }: GrapeInfoProps) {
  const t = createTranslator(locale);

  // Get parent names
  const parents: string[] = [];
  if (variety.parent1_name) parents.push(variety.parent1_name);
  if (variety.parent2_name) parents.push(variety.parent2_name);

  // Get producer count
  const producerCount = variety.uses?.length || 0;

  return (
    <div className="grape-info">
      {/* Key Details */}
      <div className="grape-details">
        {/* Bred */}
        {(variety.year_of_crossing || variety.breeder) && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.bred')}</span>
            <span className="detail-value">
              {variety.year_of_crossing && `${variety.year_of_crossing} `}
              {variety.breeder && `by ${variety.breeder}`}
            </span>
          </div>
        )}

        {/* Parents */}
        {parents.length > 0 && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.parents')}</span>
            <span className="detail-value">
              {parents.map((parent, index) => (
                <span key={parent}>
                  <Link
                    href={`/${locale}/varieties/${encodeURIComponent(parent)}`}
                    className="parent-link"
                  >
                    {parent}
                  </Link>
                  {index < parents.length - 1 && <span> × </span>}
                </span>
              ))}
            </span>
          </div>
        )}

        {/* Species */}
        {variety.species && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.species')}</span>
            <span className="detail-value">{variety.species}</span>
          </div>
        )}

        {/* Berry Skin Color */}
        {variety.berry_skin_color && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.berryColor')}</span>
            <span className="detail-value">{variety.berry_skin_color}</span>
          </div>
        )}

        {/* Known for */}
        {variety.known_for && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.knownFor')}</span>
            <span className="detail-value">{variety.known_for}</span>
          </div>
        )}

        {/* Country of Origin */}
        {variety.country_of_origin && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.origin')}</span>
            <span className="detail-value">{variety.country_of_origin}</span>
          </div>
        )}

        {/* VIVC Number */}
        {variety.vivc_number && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.vivcNumber')}</span>
            <span className="detail-value">
              <a
                href={`http://www.vivc.de/index.php?r=passport%2Fview&id=${variety.vivc_number}`}
                target="_blank"
                rel="noopener noreferrer"
                className="parent-link"
              >
                #{variety.vivc_number}
              </a>
            </span>
          </div>
        )}
      </div>

      {/* Quick Stats Card */}
      <div className="quick-stats-card">
        <h4>{t('variety.info.quickStats')}</h4>

        {/* VIVC Link Button */}
        {variety.vivc_number && (
          <a
            href={`http://www.vivc.de/index.php?r=passport%2Fview&id=${variety.vivc_number}`}
            target="_blank"
            rel="noopener noreferrer"
            className="vivc-link-button"
          >
            <span className="vivc-icon">🔗</span>
            <span className="vivc-text">
              <strong>{t('variety.info.viewOnVivc')}</strong>
              <small>Vitis International Variety Catalogue</small>
            </span>
            <span className="vivc-arrow">→</span>
          </a>
        )}

        <div className="stat-grid">
          {/* Winegrower Count */}
          <div className="stat-item">
            <div className="stat-icon">🍷</div>
            <div className="stat-content">
              <span className="stat-number">{producerCount}</span>
              <span className="stat-label">{t('variety.info.winegrowers')}</span>
            </div>
          </div>

          {/* Cold Hardiness */}
          {variety.hardiness && (
            <div className="stat-item">
              <div className="stat-icon">🌡️</div>
              <div className="stat-content">
                <span className="stat-number">{variety.hardiness}</span>
                <span className="stat-label">{t('variety.info.coldHardiness')}</span>
              </div>
            </div>
          )}

          {/* Wine Styles */}
          {variety.wine_styles && variety.wine_styles.length > 0 && (
            <div className="stat-item">
              <div className="stat-icon">🍷</div>
              <div className="stat-content">
                <span className="stat-number">{variety.wine_styles.length}</span>
                <span className="stat-label">{t('variety.info.wineStyles')}</span>
                <span className="stat-detail">{variety.wine_styles.join(', ')}</span>
              </div>
            </div>
          )}

          {/* Ripening Season */}
          {variety.ripening_season && (
            <div className="stat-item">
              <div className="stat-icon">🗓️</div>
              <div className="stat-content">
                <span className="stat-number">{variety.ripening_season}</span>
                <span className="stat-label">{t('variety.info.ripeningSeasons')}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
