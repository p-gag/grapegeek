import Link from 'next/link';
import { slugify } from '@/lib/utils';
import type { Locale } from '@/lib/i18n/config';

interface VarietyUsage {
  name: string;
  count: number;
  winegrowers: number;
}

interface TopVarietiesListProps {
  varieties: VarietyUsage[];
  locale?: Locale;
}

export default function TopVarietiesList({ varieties, locale = 'en' }: TopVarietiesListProps) {
  const maxValue = varieties[0]?.count || 1;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {varieties.map((variety, index) => {
        const percentage = (variety.count / maxValue) * 100;
        

        return (
          <div key={variety.name} className="flex items-center gap-3">
            <div className="flex-shrink-0 w-10 text-center">
              <span className="text-sm font-semibold text-gray-500">#{index + 1}</span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <Link
                  href={`/${locale}/varieties/${slugify(variety.name)}`}
                  className="text-sm font-medium text-gray-900 hover:text-brand transition-colors truncate"
                >
                  {variety.name}
                </Link>
                <div className="flex items-center gap-3 flex-shrink-0 ml-2">
                  <span className="text-xs text-gray-500">
                    {variety.winegrowers} {variety.winegrowers === 1 ? 'winegrower' : 'winegrowers'}
                  </span>
                  <span className="text-sm font-semibold text-brand">
                    {variety.count} {variety.count === 1 ? 'wine' : 'wines'}
                  </span>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-brand h-2 rounded-full transition-all duration-500"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          </div>
        );
      })}
      {varieties.length === 0 && (
        <p className="text-gray-500 text-center py-8 col-span-2">No data available</p>
      )}
    </div>
  );
}
