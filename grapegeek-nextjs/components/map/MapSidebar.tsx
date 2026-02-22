'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { slugify } from '@/lib/utils';
import Link from 'next/link';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

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
  locale: Locale;
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
  onToggleRegions,
  locale
}: MapSidebarProps) {
  const t = createTranslator(locale);
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleBackClick = () => {
    if (currentVariety) {
      router.push(`/${locale}/varieties/${slugify(currentVariety)}`);
    } else {
      router.back();
    }
  };

  const activeFilterCount = [filters.variety, filters.wine_type, filters.state].filter(Boolean).length;

  return (
    <>
      {/* Mobile top bar (shown when sidebar is closed) */}
      <div className="md:hidden flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200 shrink-0">
        <span className="text-sm font-medium text-gray-700">
          🗺 {filteredCount} / {totalCount}
          {currentVariety && <span className="text-gray-500"> · {currentVariety}</span>}
        </span>
        <button
          onClick={() => setMobileOpen(true)}
          className="flex items-center gap-1.5 text-sm font-medium text-brand"
        >
          ☰ {t('map.filters.title')}
          {activeFilterCount > 0 && (
            <span className="bg-brand text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">
              {activeFilterCount}
            </span>
          )}
        </button>
      </div>

      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/40 z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar panel */}
    <div className={`bg-white border-r border-gray-200 overflow-y-auto flex flex-col
      md:relative md:w-80 md:flex
      ${mobileOpen ? 'fixed inset-y-0 left-0 z-50 w-4/5 max-w-xs flex' : 'hidden md:flex'}`}>
      {/* Mobile close button */}
      <div className="md:hidden flex justify-end p-2 border-b border-gray-100">
        <button
          onClick={() => setMobileOpen(false)}
          className="text-gray-500 hover:text-gray-700 p-1 rounded"
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      {/* Breadcrumb Navigation */}
      <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center gap-2 text-sm">
        <Link href={`/${locale}/`} className="text-brand hover:text-brand-hover transition-colors">
          🍇 {t('nav.home')}
        </Link>
        <span className="text-gray-400">›</span>
        {currentVariety && (
          <>
            <button
              onClick={handleBackClick}
              className="text-brand hover:text-brand-hover transition-colors"
            >
              {currentVariety}
            </button>
            <span className="text-gray-400">›</span>
          </>
        )}
        <span className="text-gray-700 font-medium">{t('map.breadcrumb.map')}</span>
      </div>

      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-gray-900 mb-3 flex items-center gap-2">
          🗺 {t('map.title')}
        </h1>
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
          <div className="text-3xl font-bold text-brand">{filteredCount}</div>
          <div className="text-sm text-gray-600">{t('map.winegrowers.of', { total: totalCount })}</div>
          {currentVariety && (
            <div className="text-xs text-gray-500 mt-1">
              {t('map.winegrowers.growing', { variety: currentVariety })}
            </div>
          )}
        </div>
      </div>

      {/* Filters Section */}
      <div className="p-6 flex-1">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('map.filters.title')}</h3>

        {/* Variety Filter */}
        <div className="mb-4">
          <label htmlFor="variety-filter" className="block text-sm font-medium text-gray-700 mb-2">
            {t('map.filters.variety')}
          </label>
          <select
            id="variety-filter"
            value={filters.variety}
            onChange={(e) => updateFilter('variety', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand focus:border-transparent"
          >
            <option value="">{t('map.filters.allVarieties')}</option>
            {filterOptions.varieties.map(variety => (
              <option key={variety} value={variety}>{variety}</option>
            ))}
          </select>
        </div>

        {/* Wine Type Filter */}
        <div className="mb-4">
          <label htmlFor="wine-type-filter" className="block text-sm font-medium text-gray-700 mb-2">
            {t('map.filters.wineType')}
          </label>
          <select
            id="wine-type-filter"
            value={filters.wine_type}
            onChange={(e) => updateFilter('wine_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand focus:border-transparent"
          >
            <option value="">{t('map.filters.allWineTypes')}</option>
            {filterOptions.wine_types.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        {/* State/Province Filter */}
        <div className="mb-4">
          <label htmlFor="state-filter" className="block text-sm font-medium text-gray-700 mb-2">
            {t('map.filters.state')}
          </label>
          <select
            id="state-filter"
            value={filters.state}
            onChange={(e) => updateFilter('state', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand focus:border-transparent"
          >
            <option value="">{t('map.filters.allStates')}</option>
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
              className="w-4 h-4 accent-brand border-gray-300 rounded focus:ring-brand cursor-pointer"
            />
            <span className="text-sm text-gray-700 flex items-center gap-2">
              {t('map.filters.showRegions')}
              <span className="inline-block w-3 h-3 rounded-sm bg-brand-soft opacity-50"></span>
            </span>
          </label>
        </div>

        {/* Clear Filters Button */}
        <button
          onClick={clearFilters}
          className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors font-medium"
        >
          {t('map.filters.clearAll')}
        </button>
      </div>

      {/* Legend */}
      <div className="p-6 border-t border-gray-200 bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">{t('map.legend.title')}</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#6FAF8F] border-2 border-white shadow-md"></div>
            <span className="text-sm text-gray-700">{t('map.legend.openForVisits')}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500 border-2 border-white shadow-md"></div>
            <span className="text-sm text-gray-700">{t('map.legend.notOpen')}</span>
          </div>
        </div>
      </div>
    </div>
    </>
  );
}
