'use client'

import { Search, Filter, X } from 'lucide-react'
import { DatabaseStats } from '@/lib/types'

interface Props {
  searchQuery: string
  setSearchQuery: (query: string) => void
  filterSpecies: string
  setFilterSpecies: (species: string) => void
  filterColor: string
  setFilterColor: (color: string) => void
  showOnlyGrapes: boolean
  setShowOnlyGrapes: (show: boolean) => void
  stats: DatabaseStats
}

export default function VarietyFilters({
  searchQuery,
  setSearchQuery,
  filterSpecies,
  setFilterSpecies,
  filterColor,
  setFilterColor,
  showOnlyGrapes,
  setShowOnlyGrapes,
  stats
}: Props) {
  const hasActiveFilters = searchQuery || filterSpecies || filterColor || showOnlyGrapes

  const clearAllFilters = () => {
    setSearchQuery('')
    setFilterSpecies('')
    setFilterColor('')
    setShowOnlyGrapes(false)
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-8">
      <div className="flex items-center gap-2 mb-4">
        <Filter className="w-5 h-5 text-gray-600" />
        <h2 className="text-lg font-semibold">Filter Varieties</h2>
        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            className="ml-auto flex items-center gap-1 text-sm text-brand hover:underline"
          >
            <X className="w-4 h-4" />
            Clear all
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search box */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search varieties..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand focus:border-transparent"
          />
        </div>

        {/* Species filter */}
        <div>
          <select
            value={filterSpecies}
            onChange={(e) => setFilterSpecies(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand focus:border-transparent"
          >
            <option value="">All Species</option>
            {Object.entries(stats.species)
              .sort((a, b) => b[1] - a[1])
              .map(([species, count]) => (
                <option key={species} value={species}>
                  {species} ({count})
                </option>
              ))}
          </select>
        </div>

        {/* Berry color filter */}
        <div>
          <select
            value={filterColor}
            onChange={(e) => setFilterColor(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand focus:border-transparent"
          >
            <option value="">All Colors</option>
            {Object.entries(stats.berry_colors)
              .sort((a, b) => b[1] - a[1])
              .map(([color, count]) => (
                <option key={color} value={color}>
                  {color} ({count})
                </option>
              ))}
          </select>
        </div>

        {/* True grapes toggle */}
        <div className="flex items-center">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showOnlyGrapes}
              onChange={(e) => setShowOnlyGrapes(e.target.checked)}
              className="w-4 h-4 text-brand rounded focus:ring-brand"
            />
            <span className="text-sm text-gray-700">
              True grapes only ({stats.true_grapes})
            </span>
          </label>
        </div>
      </div>
    </div>
  )
}
