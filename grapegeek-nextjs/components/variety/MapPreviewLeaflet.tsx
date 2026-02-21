'use client';

import { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import type { GrapeVariety, MapMarker } from '@/lib/types';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default icon
if (typeof window !== 'undefined') {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
}

// Component to fit bounds
function FitBounds({ markers }: { markers: Array<{ lat: number; lng: number }> }) {
  const map = useMap();

  useEffect(() => {
    if (markers.length > 0) {
      const bounds = L.latLngBounds(markers.map((m) => [m.lat, m.lng]));
      map.fitBounds(bounds, { padding: [20, 20] });
    }
  }, [map, markers]);

  return null;
}

interface MapPreviewLeafletProps {
  variety: GrapeVariety;
}

export default function MapPreviewLeaflet({ variety }: MapPreviewLeafletProps) {
  const [mapData, setMapData] = useState<MapMarker[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch map data
  useEffect(() => {
    fetch('/api/map-data')
      .then((res) => res.json())
      .then((data) => {
        setMapData(data.markers || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching map data:', err);
        setError('Failed to load map data');
        setLoading(false);
      });
  }, []);

  // Filter markers for this variety
  const varietyMarkers = useMemo(() => {
    return mapData.filter((marker) => marker.varieties.includes(variety.name));
  }, [mapData, variety.name]);

  const winegrowerCount = varietyMarkers.length;

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
        <div>Loading map data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
        <div>Error loading map: {error}</div>
      </div>
    );
  }

  if (winegrowerCount === 0) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
        <div>No winegrowers currently growing {variety.name} in our database</div>
      </div>
    );
  }

  return (
    <>
      <MapContainer
        style={{ height: '400px', width: '100%', borderRadius: '0' }}
        center={[45.0, -85.0]}
        zoom={4}
        zoomControl={false}
        scrollWheelZoom={false}
        dragging={false}
        touchZoom={false}
        doubleClickZoom={false}
        attributionControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="© OpenStreetMap"
        />

        {varietyMarkers.length > 0 && <FitBounds markers={varietyMarkers} />}

        {varietyMarkers.map((marker) => (
          <CircleMarker
            key={marker.permit_id}
            center={[marker.lat, marker.lng]}
            radius={5}
            pathOptions={{
              fillColor: '#8B5CF6',
              fillOpacity: 0.8,
              color: '#6366F1',
              weight: 2
            }}
          />
        ))}
      </MapContainer>

      <div className="map-stats">
        <div className="stat-badge">
          <span className="stat-number">{winegrowerCount}</span>
          <span className="stat-label">Winegrowers</span>
        </div>
      </div>
    </>
  );
}
