import { useState, useEffect, useCallback, useMemo } from 'react'
import L from 'leaflet'

// Custom marker icons
const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3);"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6]
  })
}

export const greenIcon = createCustomIcon('#2E7D32')
export const yellowIcon = createCustomIcon('#FFC107')

export const useMapData = (initialVariety = '') => {
  const [mapData, setMapData] = useState(null)
  const [allProducers, setAllProducers] = useState([])
  const [filteredProducers, setFilteredProducers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentVariety, setCurrentVariety] = useState(initialVariety)

  // Filter states
  const [filters, setFilters] = useState({
    grape_variety: initialVariety || '',
    wine_type: '',
    state: '',
    open_for_visits: ''
  })

  // Filter options
  const [filterOptions, setFilterOptions] = useState({
    grape_varieties: [],
    wine_types: [],
    states_provinces: []
  })

  // Apply filters
  const applyFilters = useCallback(() => {
    if (!allProducers.length) return

    let filtered = [...allProducers]

    if (filters.grape_variety) {
      filtered = filtered.filter(producer => 
        producer.grape_varieties.includes(filters.grape_variety)
      )
    }

    if (filters.wine_type) {
      filtered = filtered.filter(producer => 
        producer.wine_types.includes(filters.wine_type)
      )
    }

    if (filters.state) {
      filtered = filtered.filter(producer => 
        producer.state_province === filters.state
      )
    }

    if (filters.open_for_visits) {
      if (filters.open_for_visits === 'yes') {
        filtered = filtered.filter(producer => producer.open_for_visits)
      } else if (filters.open_for_visits === 'no') {
        filtered = filtered.filter(producer => !producer.open_for_visits)
      }
    }

    setFilteredProducers(filtered)
  }, [allProducers, filters])

  // Update filters
  const updateFilter = useCallback((filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }))
  }, [])

  // Clear filters
  const clearFilters = useCallback(() => {
    setFilters({
      grape_variety: currentVariety || '',
      wine_type: '',
      state: '',
      open_for_visits: ''
    })
  }, [currentVariety])

  // Get producers for specific variety
  const getVarietyProducers = useCallback((varietyName) => {
    if (!varietyName || !allProducers.length) return []
    
    return allProducers.filter(producer => 
      producer.grape_varieties.includes(varietyName)
    )
  }, [allProducers])

  // Load map data
  useEffect(() => {
    const loadMapData = async () => {
      try {
        setLoading(true)
        const response = await fetch('/data/map-data.json')
        if (!response.ok) {
          throw new Error(`Failed to load map data: ${response.status}`)
        }
        const data = await response.json()
        setMapData(data)
        setAllProducers(data.full_map.producers)
        setFilterOptions(data.full_map.filter_options)
        
        // Apply initial variety filter if provided
        if (initialVariety && data.varieties[initialVariety]) {
          setFilteredProducers(data.varieties[initialVariety].producers)
        } else {
          setFilteredProducers(data.full_map.producers)
        }
      } catch (err) {
        console.error('Error loading map data:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadMapData()
  }, [initialVariety])

  // Apply filters when they change
  useEffect(() => {
    applyFilters()
  }, [applyFilters])

  // Update current variety
  useEffect(() => {
    setCurrentVariety(initialVariety)
    setFilters(prev => ({
      ...prev,
      grape_variety: initialVariety || ''
    }))
  }, [initialVariety])

  return {
    // State
    mapData,
    allProducers,
    filteredProducers,
    loading,
    error,
    currentVariety,
    filters,
    filterOptions,
    
    // Actions
    setCurrentVariety,
    updateFilter,
    clearFilters,
    
    // Functions
    getVarietyProducers,
    applyFilters
  }
}