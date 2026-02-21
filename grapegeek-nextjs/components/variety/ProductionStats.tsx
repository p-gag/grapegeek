import type { VarietyProductionStats } from '@/lib/types';
import Link from 'next/link';
import { slugify } from '@/lib/utils';

interface ProductionStatsProps {
  varietyName: string;
  stats: VarietyProductionStats | null;
}

export default function ProductionStats({ varietyName, stats }: ProductionStatsProps) {
  if (!stats) {
    return (
      <div className="production-stats-empty">
        <p>Production statistics not available for this variety.</p>
      </div>
    );
  }

  const { varietal_stats, common_blends, planted_neighbors, top_producers, geographic_distribution } = stats;

  // Don't show stats if there are no wines
  if (varietal_stats.total_wines === 0) {
    return (
      <div className="production-stats-empty">
        <p>No production data available yet for this variety.</p>
      </div>
    );
  }

  return (
    <div className="production-stats">
      <h2 className="section-title">Production & Usage Statistics</h2>
      <p className="section-description">
        Based on {varietal_stats.total_wines} wine{varietal_stats.total_wines !== 1 ? 's' : ''} from our database of North American producers.
      </p>

      {/* Varietal vs Blended */}
      <div className="stat-card">
        <h3 className="stat-card-title">🍷 Varietal vs Blended Usage</h3>
        <div className="stat-grid">
          <div className="stat-item">
            <div className="stat-number">{varietal_stats.varietal_count}</div>
            <div className="stat-label">Single-Varietal Wines</div>
            <div className="stat-detail">{varietal_stats.varietal_percentage}%</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">{varietal_stats.blended_count}</div>
            <div className="stat-label">Blended Wines</div>
            <div className="stat-detail">{(100 - varietal_stats.varietal_percentage).toFixed(1)}%</div>
          </div>
        </div>
      </div>

      {/* Variety Relationships */}
      {(common_blends.length > 0 || planted_neighbors.length > 0) && (
        <div className="stat-card">
          <h3 className="stat-card-title">🔗 Variety Relationships</h3>
          <p className="stat-card-description">
            Varieties commonly associated with {varietyName}
          </p>

          <div className="variety-relationships-grid">
            {/* Blend Partners */}
            {common_blends.length > 0 && (
              <div className="variety-relationship-section">
                <h4 className="variety-relationship-subtitle">🔀 Blend Partners</h4>
                <p className="variety-relationship-note">Co-occurrence in wines (not actual blend ratios)</p>
                <div className="variety-bars-compact">
                  {common_blends.map((blend, i) => (
                    <div key={i} className="variety-bar-row-compact">
                      <Link
                        href={`/varieties/${encodeURIComponent(blend.variety_name)}`}
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
                <h4 className="variety-relationship-subtitle">🌱 Planted Neighbors</h4>
                <p className="variety-relationship-note">Grown at same winegrowers</p>
                <div className="variety-bars-compact">
                  {planted_neighbors.map((neighbor, i) => (
                    <div key={i} className="variety-bar-row-compact">
                      <Link
                        href={`/varieties/${encodeURIComponent(neighbor.variety_name)}`}
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
          <h3 className="stat-card-title">🍷 Top Winegrowers</h3>
          <p className="stat-card-description">
            Winegrowers with highest usage of {varietyName} (minimum 3 wines)
          </p>
          <div className="table-container">
            <table className="stats-table">
              <thead>
                <tr>
                  <th>Winegrower</th>
                  <th>Location</th>
                  <th>Wines</th>
                  <th>Usage %</th>
                </tr>
              </thead>
              <tbody>
                {top_producers.map((producer, i) => (
                  <tr key={i}>
                    <td>
                      <Link href={`/winegrowers/${slugify(producer.business_name)}`}>
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

      {/* Geographic Distribution - TODO: Uncomment when region pages are ready */}
      {/* {geographic_distribution.length > 0 && (
        <div className="stat-card">
          <h3 className="stat-card-title">📍 Geographic Distribution</h3>
          <p className="stat-card-description">
            Where {varietyName} is most popular
          </p>
          <div className="table-container">
            <table className="stats-table">
              <thead>
                <tr>
                  <th>Region</th>
                  <th>Producers</th>
                  <th>Wines</th>
                  <th>% of Total</th>
                </tr>
              </thead>
              <tbody>
                {geographic_distribution.map((region, i) => (
                  <tr key={i}>
                    <td>{region.state_province}, {region.country}</td>
                    <td>{region.producer_count}</td>
                    <td>{region.wine_count}</td>
                    <td>{region.percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )} */}
    </div>
  );
}
