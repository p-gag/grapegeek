import { Winegrower } from '@/lib/types';
import { MapPin, Globe, Wine, ExternalLink } from 'lucide-react';

interface WinegrowerHeaderProps {
  winegrower: Winegrower;
}

export default function WinegrowerHeader({ winegrower }: WinegrowerHeaderProps) {
  return (
    <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white">
      <div className="container mx-auto px-4 py-12 max-w-7xl">
        <div className="flex items-start gap-6">
          {/* Icon */}
          <div className="hidden md:block">
            <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center">
              <Wine className="w-10 h-10" />
            </div>
          </div>

          {/* Main Info */}
          <div className="flex-1">
            <h1 className="text-4xl md:text-5xl font-bold mb-3">
              {winegrower.business_name}
            </h1>

            <div className="flex items-center gap-2 text-green-100 mb-4">
              <MapPin className="w-5 h-5" />
              <span className="text-lg">
                {winegrower.city}, {winegrower.state_province}, {winegrower.country}
              </span>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-white/10 rounded-lg p-4">
                <p className="text-green-200 text-sm">Wines</p>
                <p className="text-2xl font-bold">{winegrower.wines?.length || 0}</p>
              </div>

              <div className="bg-white/10 rounded-lg p-4">
                <p className="text-green-200 text-sm">Location</p>
                <p className="text-lg font-semibold">{winegrower.state_province}</p>
              </div>

              {winegrower.wine_label && (
                <div className="bg-white/10 rounded-lg p-4">
                  <p className="text-green-200 text-sm">Label</p>
                  <p className="text-lg font-semibold truncate" title={winegrower.wine_label}>
                    {winegrower.wine_label}
                  </p>
                </div>
              )}

              {winegrower.website && (
                <div className="bg-white/10 rounded-lg p-4">
                  <a
                    href={winegrower.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 hover:text-green-200 transition group"
                  >
                    <Globe className="w-5 h-5" />
                    <span className="font-semibold">Visit Website</span>
                    <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition" />
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
