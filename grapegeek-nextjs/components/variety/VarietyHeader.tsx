import { GrapeVariety } from '@/lib/types';
import { Wine, ExternalLink } from 'lucide-react';

interface Props {
  variety: GrapeVariety;
}

export default function VarietyHeader({ variety }: Props) {
  const winegrowers = variety.uses?.length || 0;

  return (
    <div className="bg-gradient-to-br from-purple-700 via-purple-600 to-indigo-600 text-white">
      <div className="container mx-auto px-4 py-12 max-w-7xl">
        {/* Title Row */}
        <div className="flex items-start gap-4 mb-8">
          <div className="bg-white/20 rounded-lg p-3">
            <Wine className="w-12 h-12" />
          </div>
          <div className="flex-1">
            <h1 className="text-5xl font-bold mb-2">{variety.name}</h1>
            <div className="flex flex-wrap gap-4 text-purple-100">
              {variety.vivc_number && (
                <a
                  href={`https://www.vivc.de/index.php?r=passport%2Fview&id=${variety.vivc_number}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 hover:text-white transition-colors"
                >
                  VIVC #{variety.vivc_number}
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
              {variety.aliases.length > 0 && (
                <span className="text-purple-200">
                  Also known as: {variety.aliases.slice(0, 3).join(', ')}
                  {variety.aliases.length > 3 && ` +${variety.aliases.length - 3} more`}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {variety.species && (
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-purple-200 text-sm mb-1">Species</p>
              <p className="text-xl font-semibold">{variety.species}</p>
            </div>
          )}
          {variety.berry_skin_color && (
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-purple-200 text-sm mb-1">Berry Color</p>
              <p className="text-xl font-semibold">{variety.berry_skin_color}</p>
            </div>
          )}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <p className="text-purple-200 text-sm mb-1">Winegrowers</p>
            <p className="text-xl font-semibold">{winegrowers}</p>
          </div>
          {variety.country_of_origin && (
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-purple-200 text-sm mb-1">Origin</p>
              <p className="text-xl font-semibold">{variety.country_of_origin}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
