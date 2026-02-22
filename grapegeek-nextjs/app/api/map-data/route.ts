import { NextResponse } from 'next/server';
import { getDatabase } from '@/lib/database';

// Force this route to be static (pre-rendered at build time)
export const dynamic = 'force-static';
export const revalidate = false;

/**
 * GET /api/map-data
 * Returns all map markers and filter options for the interactive map
 * This route is pre-rendered at build time for optimal performance
 */
export async function GET() {
  try {
    const db = getDatabase();
    const markers = db.getMapMarkers();
    const indexedRegions = db.getIndexedRegions();
    db.close();

    // Build filter options from the markers
    const varietiesSet = new Set<string>();
    const wineTypesSet = new Set<string>();
    const statesProvincesSet = new Set<string>();

    markers.forEach((marker) => {
      marker.varieties.forEach((v) => varietiesSet.add(v));
      marker.wine_types.forEach((t) => wineTypesSet.add(t));
      statesProvincesSet.add(marker.state_province);
    });

    const filterOptions = {
      varieties: Array.from(varietiesSet).sort(),
      wine_types: Array.from(wineTypesSet).sort(),
      states_provinces: Array.from(statesProvincesSet).sort()
    };

    return NextResponse.json({
      markers,
      filterOptions,
      indexedRegions: indexedRegions.map(r => ({
        state_province: r.state_province,
        country: r.country
      })),
      total: markers.length
    });
  } catch (error) {
    console.error('Error loading map data:', error);
    return NextResponse.json(
      { error: 'Failed to load map data' },
      { status: 500 }
    );
  }
}
