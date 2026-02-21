'use client';

import { useState, useMemo } from 'react';
import { Winegrower, DatabaseStats } from '@/lib/types';
import WinegrowerCard from './WinegrowerCard';
import WinegrowerFilters from './WinegrowerFilters';

interface Props {
  winegrowers: Winegrower[];
  countries: string[];
  states: string[];
  stats: DatabaseStats;
}

export default function WinegrowersIndex({ winegrowers, countries, states, stats }: Props) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCountry, setFilterCountry] = useState('');
  const [filterState, setFilterState] = useState('');

  const filteredWinegrowers = useMemo(() => {
    return winegrowers.filter(winegrower => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesName = winegrower.business_name.toLowerCase().includes(query);
        const matchesCity = winegrower.city.toLowerCase().includes(query);

        if (!matchesName && !matchesCity) {
          return false;
        }
      }

      // Country filter
      if (filterCountry && winegrower.country !== filterCountry) {
        return false;
      }

      // State/Province filter
      if (filterState && winegrower.state_province !== filterState) {
        return false;
      }

      return true;
    });
  }, [winegrowers, searchQuery, filterCountry, filterState]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Winegrowers</h1>
        <p className="text-gray-600">
          Explore {stats.total_winegrowers} winegrowers across northeastern North America
        </p>
      </div>

      <WinegrowerFilters
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        filterCountry={filterCountry}
        setFilterCountry={setFilterCountry}
        filterState={filterState}
        setFilterState={setFilterState}
        countries={countries}
        states={states}
      />

      <div className="mt-6">
        <p className="text-sm text-gray-600 mb-4">
          Showing {filteredWinegrowers.length} of {stats.total_winegrowers} winegrowers
        </p>

        {filteredWinegrowers.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-gray-600">No winegrowers found matching your criteria.</p>
            <button
              onClick={() => {
                setSearchQuery('');
                setFilterCountry('');
                setFilterState('');
              }}
              className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredWinegrowers.map(winegrower => (
              <WinegrowerCard key={winegrower.permit_id} winegrower={winegrower} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
