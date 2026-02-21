'use client';

import { Search, Filter, X } from 'lucide-react';

interface Props {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  filterCountry: string;
  setFilterCountry: (country: string) => void;
  filterState: string;
  setFilterState: (state: string) => void;
  countries: string[];
  states: string[];
}

export default function WinegrowerFilters({
  searchQuery,
  setSearchQuery,
  filterCountry,
  setFilterCountry,
  filterState,
  setFilterState,
  countries,
  states
}: Props) {
  const hasActiveFilters = searchQuery || filterCountry || filterState;

  const clearAllFilters = () => {
    setSearchQuery('');
    setFilterCountry('');
    setFilterState('');
  };

  // Filter states by selected country
  const filteredStates = filterCountry
    ? states.filter(state => {
        // In a real implementation, you'd need country-state mapping
        // For now, just show all states when a country is selected
        return true;
      })
    : states;

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-8">
      <div className="flex items-center gap-2 mb-4">
        <Filter className="w-5 h-5 text-gray-600" />
        <h2 className="text-lg font-semibold">Filter Winegrowers</h2>
        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            className="ml-auto flex items-center gap-1 text-sm text-green-600 hover:underline"
          >
            <X className="w-4 h-4" />
            Clear all
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Search box */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name or city..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>

        {/* Country filter */}
        <div>
          <select
            value={filterCountry}
            onChange={(e) => {
              setFilterCountry(e.target.value);
              setFilterState(''); // Reset state when country changes
            }}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            <option value="">All Countries</option>
            {countries.map(country => (
              <option key={country} value={country}>
                {country}
              </option>
            ))}
          </select>
        </div>

        {/* State/Province filter */}
        <div>
          <select
            value={filterState}
            onChange={(e) => setFilterState(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            <option value="">All States/Provinces</option>
            {filteredStates.map(state => (
              <option key={state} value={state}>
                {state}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
