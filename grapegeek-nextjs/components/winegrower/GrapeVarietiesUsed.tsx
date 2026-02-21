import { Wine } from '@/lib/types';
import { Grape } from 'lucide-react';
import Link from 'next/link';

interface GrapeVarietiesUsedProps {
  wines: Wine[];
}

export default function GrapeVarietiesUsed({ wines }: GrapeVarietiesUsedProps) {
  // Extract unique grape varieties from all wines
  const uniqueVarieties = Array.from(
    new Set(
      wines.flatMap((wine) => wine.grapes.map((grape) => grape.variety_name))
    )
  ).sort();

  if (uniqueVarieties.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center gap-3 mb-6">
        <Grape className="w-6 h-6 text-brand" />
        <h2 className="text-2xl font-bold">
          Grape Varieties Used ({uniqueVarieties.length})
        </h2>
      </div>

      <p className="text-gray-600 mb-4">
        This winegrower uses {uniqueVarieties.length} different grape{' '}
        {uniqueVarieties.length === 1 ? 'variety' : 'varieties'} in their wines.
      </p>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {uniqueVarieties.map((variety) => (
          <Link
            key={variety}
            href={`/varieties/${encodeURIComponent(variety)}`}
            className="px-4 py-3 bg-purple-50 text-purple-800 rounded-lg hover:bg-purple-100 transition text-center font-medium border border-purple-200 hover:border-brand-soft"
          >
            {variety}
          </Link>
        ))}
      </div>
    </div>
  );
}
