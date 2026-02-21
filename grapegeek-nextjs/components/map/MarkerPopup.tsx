'use client';

import Link from 'next/link';
import { MapMarker } from '@/lib/types';
import { slugify } from '@/lib/utils';

interface MarkerPopupProps {
  marker: MapMarker;
  selectedVariety?: string;
}

export default function MarkerPopup({ marker, selectedVariety }: MarkerPopupProps) {
  const winegrowerSlug = slugify(marker.name);

  return (
    <div className="p-2">
      {/* Header */}
      <div className="mb-3">
        <Link
          href={`/winegrowers/${winegrowerSlug}`}
          className="font-bold text-lg text-gray-900 hover:text-brand transition-colors mb-1 block"
          style={{ textDecoration: 'none' }}
        >
          {marker.name}
        </Link>
        <div className="text-sm text-gray-600 flex items-center gap-1">
          <span>📍</span>
          <span>{marker.city}, {marker.state_province}</span>
        </div>
      </div>

      {/* Variety Pills */}
      {marker.varieties && marker.varieties.length > 0 && (
        <div className="mb-3">
          <div className="flex flex-wrap gap-1">
            {marker.varieties.map((variety, index) => (
              <Link
                key={`${variety}-${index}`}
                href={`/varieties/${encodeURIComponent(variety)}`}
                className={`inline-block px-2 py-1 text-xs rounded-full transition-all hover:ring-2 hover:ring-offset-1 ${
                  selectedVariety && variety === selectedVariety
                    ? 'bg-brand text-white hover:bg-brand-hover hover:ring-brand-soft'
                    : 'bg-purple-100 text-purple-800 hover:bg-purple-200 hover:ring-brand-soft'
                }`}
                style={{ textDecoration: 'none' }}
              >
                {variety}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Wine Types */}
      {marker.wine_types && marker.wine_types.length > 0 && (
        <div className="text-sm text-gray-700 mb-3">
          <strong>Types:</strong> {marker.wine_types.join(', ')}
        </div>
      )}

      {/* View Profile Link */}
      <div className="pt-2 border-t border-gray-200">
        <Link
          href={`/winegrowers/${winegrowerSlug}`}
          className="text-sm text-brand hover:text-brand-hover font-medium flex items-center gap-1"
        >
          View Full Profile →
        </Link>
      </div>
    </div>
  );
}
