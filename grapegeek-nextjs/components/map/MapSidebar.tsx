'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface Filters {
  variety: string;
  wine_type: string;
  state: string;
  open_for_visits: string;
}

interface FilterOptions {
  varieties: string[];
  wine_types: string[];
  states_provinces: string[];
}

interface MapSidebarProps {
  filters: Filters;
  updateFilter: (filterType: keyof Filters, value: string) => void;
  clearFilters: () => void;
  filterOptions: FilterOptions;
  totalCount: number;
  filteredCount: number;
  currentVariety?: string;
  showRegions: boolean;
  onToggleRegions: (show: boolean) => void;
}

export default function MapSidebar({
  filters,
  updateFilter,
  clearFilters,
  filterOptions,
  totalCount,
  filteredCount,
  currentVariety,
  showRegions,
  onToggleRegions
}: MapSidebarProps) {
  const router = useRouter();

  const handleBackClick = () => {
    if (currentVariety) {
      const varietySlug = currentVariety.toLowerCase().replace(/\s+/g, '-');
      router.push(`/variety/${varietySlug}`);
    } else {
      router.back();
    }
  };

  return (
    <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto flex flex-col">
      {/* Breadcrumb Navigation */}
      <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center gap-2 text-sm">
        <Link href="/" className="text-green-600 hover:text-green-700 transition-colors">
          🍇 GrapeGeek
        </Link>
        <span className="text-gray-400">›</span>
        {currentVariety && (
          <>
            <button
              onClick={handleBackClick}
              className="text-green-600 hover:text-green-700 transition-colors"
            >
              {currentVariety}
            </button>
            <span className="text-gray-400">›</span>
          </>
        )}
        <span className="text-gray-700 font-medium">Map</span>
      </div>

      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-gray-900 mb-3 flex items-center gap-2">
          🗺 Winegrower Map
        </h1>
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="text-3xl font-bold text-green-700">{filteredCount}</div>
          <div className="text-sm text-gray-600">of {totalCount} winegrowers</div>
          {currentVariety && (
            <div className="text-xs text-gray-500 mt-1">
              growing <strong>{currentVariety}</strong>
            </div>
          )}
        </div>
      </div>

      {/* Filters Section */}
      <div className="p-6 flex-1">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>

        {/* Variety Filter */}
        <div className="mb-4">
          <label htmlFor="variety-filter" className="block text-sm font-medium text-gray-700 mb-2">
            Grape Variety:
          </label>
          <select
            id="variety-filter"
            value={filters.variety}
            onChange={(e) => updateFilter('variety', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            <option value="">All varieties</option>
            {filterOptions.varieties.map(variety => (
              <option key={variety} value={variety}>{variety}</option>
            ))}
          </select>
        </div>

        {/* Wine Type Filter */}
        <div className="mb-4">
          <label htmlFor="wine-type-filter" className="block text-sm font-medium text-gray-700 mb-2">
            Wine Type:
          </label>
          <select
            id="wine-type-filter"
            value={filters.wine_type}
            onChange={(e) => updateFilter('wine_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            <option value="">All wine types</option>
            {filterOptions.wine_types.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        {/* State/Province Filter */}
        <div className="mb-4">
          <label htmlFor="state-filter" className="block text-sm font-medium text-gray-700 mb-2">
            State/Province:
          </label>
          <select
            id="state-filter"
            value={filters.state}
            onChange={(e) => updateFilter('state', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            <option value="">All states/provinces</option>
            {filterOptions.states_provinces.map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>

        {/* Show Indexed Regions Toggle */}
        <div className="mb-4 pb-4 border-b border-gray-200">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={showRegions}
              onChange={(e) => onToggleRegions(e.target.checked)}
              className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500 cursor-pointer"
            />
            <span className="text-sm text-gray-700 flex items-center gap-2">
              Show indexed regions
              <span className="inline-block w-3 h-3 rounded-sm bg-green-500 opacity-50"></span>
            </span>
          </label>
        </div>

        {/* Clear Filters Button */}
        <button
          onClick={clearFilters}
          className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors font-medium"
        >
          Clear All Filters
        </button>
      </div>

      {/* Legend */}
      <div className="p-6 border-t border-gray-200 bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Legend</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-600 border-2 border-white shadow-md"></div>
            <span className="text-sm text-gray-700">Open for visits</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500 border-2 border-white shadow-md"></div>
            <span className="text-sm text-gray-700">Not open for visits</span>
          </div>
        </div>
      </div>
    </div>
  );
}
