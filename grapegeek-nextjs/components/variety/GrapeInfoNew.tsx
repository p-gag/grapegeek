'use client';

import Link from 'next/link';
import { slugify, simplifySpeciesName } from '@/lib/utils';
import type { GrapeVariety, VarietyProductionStats } from '@/lib/types';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface GrapeInfoProps {
  variety: GrapeVariety & {
    year_of_crossing?: number | string;
    breeder?: string;
    known_for?: string;
    hardiness?: string;
    wine_styles?: string[];
    ripening_season?: string;
  };
  locale: Locale;
  productionStats?: VarietyProductionStats | null;
}

export default function GrapeInfo({ variety, locale, productionStats }: GrapeInfoProps) {
  const t = createTranslator(locale);

  const parents: string[] = [];
  if (variety.parent1_name) parents.push(variety.parent1_name);
  if (variety.parent2_name) parents.push(variety.parent2_name);

  const producerCount = variety.uses?.length || 0;

  const varietalStats = productionStats?.varietal_stats;
  const hasWineStats = varietalStats && varietalStats.total_wines > 0;
  const varietalPct = hasWineStats ? varietalStats.varietal_percentage : 0;
  const blendedPct = hasWineStats ? 100 - varietalPct : 0;

  const geoDist = productionStats?.geographic_distribution || [];
  const topGeo = geoDist.slice(0, 5);
  const maxGeoCount = topGeo.length > 0 ? topGeo[0].producer_count : 0;

  return (
    <div className="grape-info">
      {/* Key Details */}
      <div className="grape-details">
        {variety.species && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.species')}</span>
            <span className="detail-value detail-value-italic">{simplifySpeciesName(variety.species)}</span>
          </div>
        )}

        {variety.berry_skin_color && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.berryColor')}</span>
            <span className="detail-value">{variety.berry_skin_color}</span>
          </div>
        )}

        {parents.length > 0 && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.parents')}</span>
            <span className="detail-value">
              {parents.map((parent, index) => (
                <span key={parent}>
                  <Link
                    href={`/${locale}/varieties/${slugify(parent)}`}
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

        {(variety.year_of_crossing || variety.breeder) && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.bred')}</span>
            <span className="detail-value">
              {variety.year_of_crossing && `${variety.year_of_crossing} `}
              {variety.breeder && `by ${variety.breeder}`}
            </span>
          </div>
        )}

        {variety.country_of_origin && (
          <div className="detail-row">
            <span className="detail-label">{t('variety.info.origin')}</span>
            <span className="detail-value">{variety.country_of_origin}</span>
          </div>
        )}
      </div>

      {/* VIVC Link */}
      {variety.vivc_number && (
        <a
          href={`https://www.vivc.de/index.php?r=passport%2Fview&id=${variety.vivc_number}`}
          target="_blank"
          rel="noopener noreferrer"
          className="vivc-compact-link"
        >
          <span className="vivc-compact-text">
            {t('variety.info.viewOnVivc')} <span className="vivc-compact-number">#{variety.vivc_number}</span>
          </span>
          <span className="vivc-compact-arrow">↗</span>
        </a>
      )}

      {/* Stats side by side on desktop, stacked on mobile */}
      <div className="info-stats-grid">
        {/* Wine production stats — donut chart */}
        {hasWineStats && (
          <div className="info-stats-cell">
            <div className="info-stats-header">
              <span className="info-stats-number">{varietalStats.total_wines}</span>
              <span className="info-stats-label">{t('variety.production.wines')}</span>
            </div>
            <div className="info-stats-body">
              <div className="donut-chart-container">
                <svg viewBox="0 0 100 100" className="donut-chart">
                  <circle
                    cx="50" cy="50" r="38"
                    fill="none"
                    stroke="#f59e0b"
                    strokeWidth="12"
                  />
                  <circle
                    cx="50" cy="50" r="38"
                    fill="none"
                    stroke="#8b5cf6"
                    strokeWidth="12"
                    strokeDasharray={`${varietalPct * 2.388} ${238.8 - varietalPct * 2.388}`}
                    strokeDashoffset="59.7"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="donut-center">
                  <span className="donut-pct">{varietalPct.toFixed(0)}%</span>
                  <span className="donut-sub">{t('variety.production.singleVarietal')}</span>
                </div>
              </div>
              <div className="donut-legend">
                <span className="donut-legend-item varietal-color">
                  <span className="donut-legend-dot" style={{ background: '#8b5cf6' }} />
                  {t('variety.production.singleVarietal')}
                </span>
                <span className="donut-legend-item blended-color">
                  <span className="donut-legend-dot" style={{ background: '#f59e0b' }} />
                  {t('variety.production.blended')}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Winegrowers with geographic breakdown */}
        <div className="info-stats-cell">
          <div className="info-stats-header">
            <span className="info-stats-number">{producerCount}</span>
            <span className="info-stats-label">{t('variety.info.winegrowers')}</span>
          </div>
          <div className="info-stats-body">
            {topGeo.length > 0 && (
              <div className="geo-bars">
                {topGeo.map((geo) => (
                  <div key={`${geo.state_province}-${geo.country}`} className="geo-bar-row">
                    <span className="geo-bar-name">{geo.state_province}</span>
                    <div className="geo-bar-track">
                      <div
                        className="geo-bar-fill"
                        style={{ width: `${(geo.producer_count / maxGeoCount) * 100}%` }}
                      />
                    </div>
                    <span className="geo-bar-count">{geo.producer_count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
