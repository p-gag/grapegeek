import type { VarietyProductionStats } from '@/lib/types';
import Link from 'next/link';
import { slugify } from '@/lib/utils';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface ProductionStatsProps {
  varietyName: string;
  stats: VarietyProductionStats | null;
  locale: Locale;
}

export default function ProductionStats({ varietyName, stats, locale }: ProductionStatsProps) {
  const t = createTranslator(locale);

  if (!stats) {
    return (
      <div className="production-stats-empty">
        <p>{t('variety.production.notAvailable')}</p>
      </div>
    );
  }

  const { varietal_stats, common_blends, planted_neighbors, top_producers, geographic_distribution } = stats;

  // Don't show stats if there are no wines
  if (varietal_stats.total_wines === 0) {
    return (
      <div className="production-stats-empty">
        <p>{t('variety.production.noData')}</p>
      </div>
    );
  }

  return (
    <div className="production-stats">
      <h2 className="section-title">{t('variety.production.title')}</h2>
      <p className="section-description">
        {t('variety.production.basedOn', { count: varietal_stats.total_wines })}
      </p>

      {/* Varietal vs Blended */}
      <div className="stat-card">
        <h3 className="stat-card-title">🍷 {t('variety.production.varieVsBlended')}</h3>
        <div className="stat-grid">
          <div className="stat-item">
            <div className="stat-number">{varietal_stats.varietal_count}</div>
            <div className="stat-label">{t('variety.production.singleVarietal')}</div>
            <div className="stat-detail">{varietal_stats.varietal_percentage}%</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">{varietal_stats.blended_count}</div>
            <div className="stat-label">{t('variety.production.blended')}</div>
            <div className="stat-detail">{(100 - varietal_stats.varietal_percentage).toFixed(1)}%</div>
          </div>
        </div>
      </div>

      {/* Variety Relationships */}
      {(common_blends.length > 0 || planted_neighbors.length > 0) && (
        <div className="stat-card">
          <h3 className="stat-card-title">🔗 {t('variety.production.relationships')}</h3>
          <p className="stat-card-description">
            {t('variety.production.relationshipsDesc', { variety: varietyName })}
          </p>

          <div className="variety-relationships-grid">
            {/* Blend Partners */}
            {common_blends.length > 0 && (
              <div className="variety-relationship-section">
                <h4 className="variety-relationship-subtitle">🔀 {t('variety.production.blendPartners')}</h4>
                <p className="variety-relationship-note">{t('variety.production.blendPartnersNote')}</p>
                <div className="variety-bars-compact">
                  {common_blends.map((blend, i) => (
                    <div key={i} className="variety-bar-row-compact">
                      <Link
                        href={`/${locale}/varieties/${slugify(blend.variety_name)}`}
                        className="variety-bar-name-compact"
                      >
                        {blend.variety_name}
                      </Link>
                      <div className="variety-bar-container-compact">
                        <div
                          className="variety-bar-fill blend-bar"
                          style={{ width: `${blend.percentage}%` }}
                        />
                      </div>
                      <div className="variety-bar-value-compact">
                        {blend.co_occurrence_count} ({blend.percentage}%)
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Planted Neighbors */}
            {planted_neighbors.length > 0 && (
              <div className="variety-relationship-section">
                <h4 className="variety-relationship-subtitle">🌱 {t('variety.production.plantedNeighbors')}</h4>
                <p className="variety-relationship-note">{t('variety.production.plantedNeighborsNote')}</p>
                <div className="variety-bars-compact">
                  {planted_neighbors.map((neighbor, i) => (
                    <div key={i} className="variety-bar-row-compact">
                      <Link
                        href={`/${locale}/varieties/${slugify(neighbor.variety_name)}`}
                        className="variety-bar-name-compact"
                      >
                        {neighbor.variety_name}
                      </Link>
                      <div className="variety-bar-container-compact">
                        <div
                          className="variety-bar-fill neighbor-bar"
                          style={{ width: `${neighbor.percentage}%` }}
                        />
                      </div>
                      <div className="variety-bar-value-compact">
                        {neighbor.producer_count} ({neighbor.percentage}%)
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Top Winegrowers */}
      {top_producers.length > 0 && (
        <div className="stat-card">
          <h3 className="stat-card-title">🍷 {t('variety.production.topWinegrowers')}</h3>
          <p className="stat-card-description">
            {t('variety.production.topWinegrowersDesc', { variety: varietyName })}
          </p>
          <div className="table-container">
            <table className="stats-table">
              <thead>
                <tr>
                  <th>{t('variety.production.tableWinegrower')}</th>
                  <th>{t('variety.production.tableLocation')}</th>
                  <th>{t('variety.production.tableWines')}</th>
                  <th>{t('variety.production.tableUsage')}</th>
                </tr>
              </thead>
              <tbody>
                {top_producers.map((producer, i) => (
                  <tr key={i}>
                    <td>
                      <Link href={`/${locale}/winegrowers/${slugify(producer.business_name)}`}>
                        {producer.business_name}
                      </Link>
                    </td>
                    <td>{producer.state_province}, {producer.country}</td>
                    <td>{producer.wines_with_variety}/{producer.total_wines}</td>
                    <td>{producer.usage_percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
