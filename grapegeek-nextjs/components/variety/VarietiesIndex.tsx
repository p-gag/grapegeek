'use client'

import { useState, useMemo } from 'react'
import { GrapeVariety, DatabaseStats } from '@/lib/types'
import VarietyCard from './VarietyCard'
import VarietyFilters from './VarietyFilters'

interface Props {
  varieties: GrapeVariety[]
  stats: DatabaseStats
}

export default function VarietiesIndex({ varieties, stats }: Props) {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterSpecies, setFilterSpecies] = useState('')
  const [filterColor, setFilterColor] = useState('')
  const [showOnlyGrapes, setShowOnlyGrapes] = useState(false)

  const filteredVarieties = useMemo(() => {
    return varieties.filter(variety => {
      // Search filter
      if (searchQuery && !variety.name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false
      }

      // Species filter
      if (filterSpecies && variety.species !== filterSpecies) {
        return false
      }

      // Color filter
      if (filterColor && variety.berry_skin_color !== filterColor) {
        return false
      }

      // Show only true grapes
      if (showOnlyGrapes && !variety.is_grape) {
        return false
      }

      return true
    })
  }, [varieties, searchQuery, filterSpecies, filterColor, showOnlyGrapes])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-br from-brand-dark to-brand text-white py-12">
        <div className="container mx-auto px-4">
          <h1 className="text-5xl font-bold mb-4">Grape Varieties</h1>
          <p className="text-xl text-purple-100">
            Browse {stats.total_varieties} cold-climate grape varieties
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="container mx-auto px-4 py-8">
        <VarietyFilters
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          filterSpecies={filterSpecies}
          setFilterSpecies={setFilterSpecies}
          filterColor={filterColor}
          setFilterColor={setFilterColor}
          showOnlyGrapes={showOnlyGrapes}
          setShowOnlyGrapes={setShowOnlyGrapes}
          stats={stats}
        />

        {/* Results count */}
        <div className="mb-6">
          <p className="text-gray-600">
            Showing {filteredVarieties.length} of {varieties.length} varieties
          </p>
        </div>

        {/* Varieties grid */}
        {filteredVarieties.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVarieties.map(variety => (
              <VarietyCard key={variety.id} variety={variety} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              No varieties found matching your criteria.
            </p>
            <button
              onClick={() => {
                setSearchQuery('')
                setFilterSpecies('')
                setFilterColor('')
                setShowOnlyGrapes(false)
              }}
              className="mt-4 text-brand hover:underline"
            >
              Clear all filters
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
