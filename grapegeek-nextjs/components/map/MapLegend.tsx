'use client';

/**
 * MapLegend - Shows what the region overlay colors mean
 */
export default function MapLegend() {
  return (
    <div className="map-legend">
      <div className="legend-item">
        <div className="legend-color indexed"></div>
        <span className="legend-label">Regions with winegrowers</span>
      </div>
      <div className="legend-item">
        <div className="legend-color non-indexed"></div>
        <span className="legend-label">Regions not yet indexed</span>
      </div>
    </div>
  );
}
