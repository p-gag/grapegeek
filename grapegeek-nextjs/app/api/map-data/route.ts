import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
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
    const mapDataPath = path.join(process.cwd(), 'public', 'data', 'map-data.json');
    const mapData = JSON.parse(fs.readFileSync(mapDataPath, 'utf-8'));

    // Transform to the format expected by MapPreviewLeaflet
    const markers = mapData.full_map.producers.map((producer: any) => ({
      permit_id: producer.id,
      name: producer.name,
      lat: producer.coordinates[1], // Leaflet uses [lat, lng]
      lng: producer.coordinates[0],
      city: producer.city,
      state_province: producer.state_province,
      country: producer.country,
      varieties: producer.grape_varieties,
      wine_types: producer.wine_types
    }));

    // Build filter options from the markers
    const varietiesSet = new Set<string>();
    const wineTypesSet = new Set<string>();
    const statesProvincesSet = new Set<string>();

    markers.forEach((marker: any) => {
      marker.varieties.forEach((v: string) => varietiesSet.add(v));
      marker.wine_types.forEach((t: string) => wineTypesSet.add(t));
      statesProvincesSet.add(marker.state_province);
    });

    const filterOptions = {
      varieties: Array.from(varietiesSet).sort(),
      wine_types: Array.from(wineTypesSet).sort(),
      states_provinces: Array.from(statesProvincesSet).sort()
    };

    // Get indexed regions from database for map overlay
    const db = getDatabase();
    const indexedRegions = db.getIndexedRegions();
    db.close();

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
