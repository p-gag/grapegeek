import { Wine } from '@/lib/types';
import { Wine as WineIcon, Grape } from 'lucide-react';
import Link from 'next/link';

interface WineListProps {
  wines: Wine[];
}

export default function WineList({ wines }: WineListProps) {
  if (wines.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <WineIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-xl font-semibold text-gray-600 mb-2">No Wines Listed</h3>
        <p className="text-gray-500">
          This winegrower does not have any wines catalogued in our database yet.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center gap-3 mb-6">
        <WineIcon className="w-6 h-6 text-brand" />
        <h2 className="text-2xl font-bold">Wines ({wines.length})</h2>
      </div>

      <div className="space-y-4">
        {wines.map((wine) => (
          <div
            key={wine.id}
            className="border rounded-lg p-4 hover:border-brand-soft hover:shadow-sm transition"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-purple-900 mb-2">
                  {wine.name}
                  {wine.vintage && (
                    <span className="ml-2 text-sm font-normal text-gray-500">
                      {wine.vintage}
                    </span>
                  )}
                </h3>

                {wine.type && (
                  <div className="mb-2">
                    <span className="inline-block px-2 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
                      {wine.type}
                    </span>
                  </div>
                )}

                {wine.description && (
                  <p className="text-gray-600 text-sm mb-3">{wine.description}</p>
                )}

                {wine.winemaking && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                      Winemaking
                    </p>
                    <p className="text-sm text-gray-700">{wine.winemaking}</p>
                  </div>
                )}

                {/* Grape Varieties */}
                {wine.grapes && wine.grapes.length > 0 && (
                  <div className="flex items-start gap-2 mt-3 pt-3 border-t">
                    <Grape className="w-4 h-4 text-brand mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                        Grape Varieties
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {wine.grapes.map((grape, index) => (
                          <Link
                            key={index}
                            href={`/varieties/${encodeURIComponent(grape.variety_name)}`}
                            className="text-sm px-2 py-1 bg-purple-50 text-purple-700 rounded hover:bg-purple-100 transition"
                          >
                            {grape.variety_name}
                            {grape.percentage && ` (${grape.percentage}%)`}
                          </Link>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
