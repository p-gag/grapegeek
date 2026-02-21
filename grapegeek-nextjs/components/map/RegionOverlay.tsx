'use client';

import { useEffect, useState } from 'react';
import { GeoJSON } from 'react-leaflet';
import type { PathOptions } from 'leaflet';

/**
 * RegionOverlay - Shows state/province boundaries on the map
 *
 * Highlights regions that have winegrowers in the database (indexed)
 * and greys out regions without data (non-indexed).
 *
 * HOW TO ADD NEW REGIONS:
 * 1. Add GeoJSON data to /public/data/na-regions.json
 * 2. Ensure properties.name matches database state_province field
 * 3. That's it! The overlay automatically detects indexed regions
 *
 * See /public/data/README.md for detailed instructions.
 */

interface RegionOverlayProps {
  indexedRegions?: Array<{ state_province: string; country: string }>;
}

export default function RegionOverlay({ indexedRegions = [] }: RegionOverlayProps) {
  const [geoData, setGeoData] = useState<any>(null);

  // Load GeoJSON data
  useEffect(() => {
    fetch('/data/na-regions.json')
      .then(res => res.json())
      .then(data => setGeoData(data))
      .catch(err => console.error('Error loading region overlay:', err));
  }, []);

  if (!geoData) return null;

  // Normalize country codes (database uses US/CA, GeoJSON uses USA/CANADA)
  const normalizeCountry = (country: string): string => {
    if (country === 'US') return 'USA';
    if (country === 'CA') return 'CANADA';
    return country;
  };

  // Create a set of indexed region names for fast lookup
  const indexedSet = new Set(
    indexedRegions.map(r => `${r.state_province}|${normalizeCountry(r.country)}`)
  );

  // Style function for regions
  const style = (feature: any): PathOptions => {
    const regionKey = `${feature.properties.name}|${feature.properties.country}`;
    const isIndexed = indexedSet.has(regionKey);

    return {
      fillColor: isIndexed ? '#10b981' : '#d1d5db',
      fillOpacity: isIndexed ? 0.15 : 0.05,
      color: isIndexed ? '#059669' : '#9ca3af',
      weight: 1,
      opacity: 0.5
    };
  };

  return (
    <GeoJSON
      data={geoData}
      style={style}
      interactive={false}
    />
  );
}
