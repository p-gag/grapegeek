'use client';

import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapMarker } from '@/lib/types';
import MarkerPopup from './MarkerPopup';
import RegionOverlay from './RegionOverlay';
import type { Locale } from '@/lib/i18n/config';

// Fix default marker icons for Next.js
// Create custom icons
const createCustomIcon = (color: string) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3);"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6]
  });
};

const greenIcon = createCustomIcon('#2E7D32');
const yellowIcon = createCustomIcon('#FFC107');

// Component to handle map bounds updates
function MapController({ markers }: { markers: MapMarker[] }) {
  const map = useMap();

  useEffect(() => {
    if (markers && markers.length > 0) {
      const bounds = L.latLngBounds(markers.map(m => [m.lat, m.lng]));
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [map, markers]);

  return null;
}

interface MapViewProps {
  markers: MapMarker[];
  indexedRegions?: Array<{ state_province: string; country: string }>;
  showRegions?: boolean;
  locale?: Locale;
}

export default function MapView({ markers, indexedRegions = [], showRegions = true, locale = 'en' }: MapViewProps) {
  return (
    <MapContainer
        center={[45.0, -85.0]}
        zoom={4}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
        scrollWheelZoom={true}
      >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />

      {/* Region overlay - shows indexed vs non-indexed states */}
      {showRegions && <RegionOverlay indexedRegions={indexedRegions} />}

      <MapController markers={markers} />

      {markers.map((marker) => (
        <Marker
          key={marker.permit_id}
          position={[marker.lat, marker.lng]}
          icon={greenIcon} // TODO: Use yellowIcon for not open_for_visits when data available
        >
          <Popup
            maxWidth={400}
            minWidth={320}
            className="winegrower-popup"
          >
            <MarkerPopup marker={marker} locale={locale} />
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
