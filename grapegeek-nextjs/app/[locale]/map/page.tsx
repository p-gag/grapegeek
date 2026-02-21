'use client';

import { useState, useMemo, useEffect, Suspense } from 'react';
import dynamic from 'next/dynamic';
import { useSearchParams } from 'next/navigation';
import MapSidebar from '@/components/map/MapSidebar';
import { MapMarker } from '@/lib/types';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

// Dynamic import to avoid SSR issues with Leaflet
const MapView = dynamic(() => import('@/components/map/MapView'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand mx-auto mb-4"></div>
        <p className="text-gray-600">Loading map...</p>
      </div>
    </div>
  )
});

interface FilterOptions {
  varieties: string[];
  wine_types: string[];
  states_provinces: string[];
}

interface Filters {
  variety: string;
  wine_type: string;
  state: string;
  open_for_visits: string;
}

function MapPageContent({ locale }: { locale: Locale }) {
  const t = createTranslator(locale);
  const searchParams = useSearchParams();

  const [allMarkers, setAllMarkers] = useState<MapMarker[]>([]);
  const [indexedRegions, setIndexedRegions] = useState<Array<{ state_province: string; country: string }>>([]);
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    varieties: [],
    wine_types: [],
    states_provinces: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filters, setFilters] = useState<Filters>({
    variety: searchParams.get('variety') || '',
    wine_type: searchParams.get('wine_type') || '',
    state: searchParams.get('state') || '',
    open_for_visits: searchParams.get('open_for_visits') || ''
  });

  const [showRegions, setShowRegions] = useState(false);

  // Load map data on mount
  useEffect(() => {
    const loadMapData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/map-data');
        if (!response.ok) {
          throw new Error(`Failed to load map data: ${response.status}`);
        }
        const data = await response.json();
        setAllMarkers(data.markers);
        setFilterOptions(data.filterOptions);
        setIndexedRegions(data.indexedRegions || []);
      } catch (err) {
        console.error('Error loading map data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load map data');
      } finally {
        setLoading(false);
      }
    };

    loadMapData();
  }, []);

  // Filter markers based on current filters
  const filteredMarkers = useMemo(() => {
    if (!allMarkers.length) return [];

    let filtered = [...allMarkers];

    if (filters.variety) {
      filtered = filtered.filter(marker =>
        marker.varieties.includes(filters.variety)
      );
    }

    if (filters.wine_type) {
      filtered = filtered.filter(marker =>
        marker.wine_types.includes(filters.wine_type)
      );
    }

    if (filters.state) {
      filtered = filtered.filter(marker =>
        marker.state_province === filters.state
      );
    }

    return filtered;
  }, [allMarkers, filters]);

  const updateFilter = (filterType: keyof Filters, value: string) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      variety: '',
      wine_type: '',
      state: '',
      open_for_visits: ''
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-brand mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">{t('map.loadingData')}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center max-w-md">
          <div className="text-red-600 text-6xl mb-4">⚠</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">{t('map.error.title')}</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-brand text-white px-6 py-2 rounded-lg hover:bg-brand-hover transition-colors"
          >
            {t('map.error.tryAgain')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <MapSidebar
        filters={filters}
        updateFilter={updateFilter}
        clearFilters={clearFilters}
        filterOptions={filterOptions}
        totalCount={allMarkers.length}
        filteredCount={filteredMarkers.length}
        currentVariety={filters.variety}
        showRegions={showRegions}
        onToggleRegions={setShowRegions}
        locale={locale}
      />

      {/* Map */}
      <div className="flex-1">
        <MapView markers={filteredMarkers} indexedRegions={indexedRegions} showRegions={showRegions} locale={locale} />
      </div>
    </div>
  );
}

export default function MapPage({ params }: { params: { locale: Locale } }) {
  const { locale } = params;
  const t = createTranslator(locale);
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-brand mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">{t('map.loadingGeneral')}</p>
        </div>
      </div>
    }>
      <MapPageContent locale={locale} />
    </Suspense>
  );
}
