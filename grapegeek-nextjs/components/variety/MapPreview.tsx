'use client';

import { useEffect, useState, useMemo } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import type { GrapeVariety, MapMarker } from '@/lib/types';

interface MapPreviewProps {
  variety: GrapeVariety;
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

export default function MapPreview({ variety }: MapPreviewProps) {
  return (
    <div className="preview-section">
      <div className="preview-header">
        <h2>🗺️ Where It Grows</h2>
        <p>Wineries and vineyards growing {variety.name} across North America</p>
      </div>

      <div className="map-preview-container">
        <div className="map-rectangle">
          <DynamicMapView variety={variety} />

          <div className="map-invitation">
            <div className="invitation-text">Explore interactive winegrower map</div>
            <div className="invitation-arrow">→</div>
          </div>
        </div>

        <Link
          href={`/map?variety=${encodeURIComponent(variety.name)}`}
          className="map-overlay-button"
          aria-label="Open interactive map"
        >
          <span className="sr-only">Open Interactive Map</span>
        </Link>
      </div>
    </div>
  );
}
