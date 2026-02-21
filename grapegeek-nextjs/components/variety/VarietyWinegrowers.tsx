import { GrapeVariety } from '@/lib/types';
import Link from 'next/link';
import { Factory, MapPin, ExternalLink, Wine } from 'lucide-react';
import { slugify } from '@/lib/utils';

interface Props {
  variety: GrapeVariety;
}

export default function VarietyWinegrowers({ variety }: Props) {
  const uses = variety.uses || [];

  // Group wines by winegrower
  const winesByMaker = uses.reduce((acc, use) => {
    if (!acc[use.winegrower_id]) {
      acc[use.winegrower_id] = {
        id: use.winegrower_id,
        name: use.winegrower_name,
        slug: slugify(use.winegrower_name),
        wines: []
      };
    }
    acc[use.winegrower_id].wines.push({
      id: use.wine_id,
      name: use.wine_name
    });
    return acc;
  }, {} as Record<string, { id: string; name: string; slug: string; wines: Array<{ id: number; name: string }> }>);

  const winegrowers = Object.values(winesByMaker);

  if (uses.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-8">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Factory className="w-6 h-6 text-brand" />
          Winegrowers Using This Variety
        </h2>
        <div className="text-center py-12">
          <Wine className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600 text-lg mb-2">
            No winegrowers found using {variety.name}
          </p>
          <p className="text-gray-500 text-sm">
            This variety may be newly planted or not yet tracked in our database.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2 mb-2">
          <Factory className="w-6 h-6 text-brand" />
          Winegrowers Using This Variety
        </h2>
        <p className="text-gray-600">
          {winegrowers.length} winegrower{winegrowers.length !== 1 ? 's' : ''} growing {variety.name} in North America
        </p>
      </div>

      {/* Winegrowers List */}
      <div className="space-y-4">
        {winegrowers.map((winegrower) => (
          <div
            key={winegrower.id}
            className="border border-gray-200 rounded-lg p-4 hover:border-brand-soft hover:shadow-md transition-all"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <Link
                  href={`/winegrowers/${winegrower.slug}`}
                  className="text-lg font-semibold text-brand hover:text-brand-hover hover:underline transition-colors mb-2 inline-flex items-center gap-2"
                >
                  {winegrower.name}
                  <ExternalLink className="w-4 h-4" />
                </Link>

                {/* Wines made with this variety */}
                {winegrower.wines.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm text-gray-600 mb-2 font-medium">
                      Wines featuring {variety.name}:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {winegrower.wines.map((wine) => (
                        <span
                          key={wine.id}
                          className="inline-flex items-center gap-1 bg-purple-50 text-purple-800 px-3 py-1 rounded-md text-sm"
                        >
                          <Wine className="w-3 h-3" />
                          {wine.name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <Link
                href={`/winegrowers/${winegrower.slug}`}
                className="flex-shrink-0 px-4 py-2 bg-brand text-white rounded-lg hover:bg-brand-hover transition-colors text-sm font-medium"
              >
                View Details
              </Link>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Footer */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            Total wines featuring {variety.name}: <strong>{uses.length}</strong>
          </span>
          <Link
            href="/map"
            className="flex items-center gap-1 text-brand hover:text-brand font-medium"
          >
            <MapPin className="w-4 h-4" />
            View on Map
          </Link>
        </div>
      </div>
    </div>
  );
}
