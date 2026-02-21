'use client';

import { Winegrower } from '@/lib/types';
import { MapPin, ExternalLink } from 'lucide-react';

interface LocationMapProps {
  winegrower: Winegrower;
}

export default function LocationMap({ winegrower }: LocationMapProps) {
  if (!winegrower.latitude || !winegrower.longitude) {
    return null;
  }

  // Build Google Maps embed URL
  const embedUrl = `https://www.google.com/maps?q=${winegrower.latitude},${winegrower.longitude}&output=embed&z=12`;

  // Build Google Maps link URL
  const linkUrl = `https://www.google.com/maps?q=${winegrower.latitude},${winegrower.longitude}`;

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-4 bg-gray-50 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold">Location</h3>
        </div>
        <a
          href={linkUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 transition"
        >
          Open in Maps
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      <div className="relative w-full h-64">
        <iframe
          src={embedUrl}
          className="w-full h-full border-0"
          allowFullScreen
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
          title={`Location of ${winegrower.business_name}`}
        />
      </div>

      {winegrower.geocoding_method && (
        <div className="px-4 py-2 bg-gray-50 border-t">
          <p className="text-xs text-gray-500">
            Location determined by: {winegrower.geocoding_method}
          </p>
        </div>
      )}
    </div>
  );
}
