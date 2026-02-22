/**
 * Database Access Layer for GrapeGeek SQLite Database
 *
 * Type-safe database queries for Next.js Static Site Generation.
 * Mirrors the Python implementation from src/includes/database.py
 *
 * Usage:
 *   import { getDatabase } from '@/lib/database';
 *
 *   const db = getDatabase();
 *   const winegrower = db.getWinegrower('AV006', true);
 *   const varieties = db.getAllVarieties();
 *   db.close();
 */

import Database from 'better-sqlite3';
import path from 'path';
import { slugify } from './utils';
import {
  Winegrower,
  Wine,
  WineGrape,
  GrapeVariety,
  GrapeUse,
  MapMarker,
  DatabaseStats,
  VarietyProductionStats,
  VarietalStats,
  BlendPartner,
  PlantedNeighbor,
  ProducerUsage,
  GeographicDistribution,
  SearchVarietyItem,
  SearchWinegrowerItem,
} from './types';

const EXPECTED_SCHEMA_VERSION = 1;

/**
 * Validate that database schema matches expected version
 */
function validateSchemaVersion(db: Database.Database): void {
  const result = db.prepare(
    'SELECT value FROM schema_info WHERE key = ?'
  ).get('version') as { value: string } | undefined;

  if (!result) {
    throw new Error(
      'Database missing schema version info. ' +
      'Please rebuild database: uv run src/09_build_database.py'
    );
  }

  const version = parseInt(result.value);
  if (version !== EXPECTED_SCHEMA_VERSION) {
    throw new Error(
      `Schema version mismatch: expected ${EXPECTED_SCHEMA_VERSION}, got ${version}. ` +
      'Please rebuild database: uv run src/09_build_database.py'
    );
  }
}

/**
 * Type-safe database query interface for GrapeGeek
 */
export class GrapeGeekDB {
  private db: Database.Database;

  constructor(dbPath?: string) {
    const defaultPath = path.join(process.cwd(), 'data', 'grapegeek.db');
    const resolvedPath = dbPath || defaultPath;

    this.db = new Database(resolvedPath, { readonly: true });
    validateSchemaVersion(this.db);
  }

  // ========================================
  // Winegrower queries (table: producers)
  // ========================================

  /**
   * Get winegrower by permit ID with optional relationships
   */
  getWinegrower(permitId: string, includeRelationships = false): Winegrower | null {
    const row = this.db.prepare(
      'SELECT * FROM producers WHERE permit_id = ?'
    ).get(permitId) as any;

    if (!row) {
      return null;
    }

    const winegrower = this.rowToWinegrower(row);

    if (includeRelationships) {
      this.loadWinegrowerRelationships(winegrower);
    }

    return winegrower;
  }

  /**
   * Get winegrower by URL slug with optional relationships
   */
  getWinegrowerBySlug(slug: string, includeRelationships = false): Winegrower | null {
    const rows = this.db.prepare(
      'SELECT * FROM producers ORDER BY business_name'
    ).all() as any[];

    // Find the winegrower with matching slug
    const row = rows.find(r => slugify(r.business_name) === slug);

    if (!row) {
      return null;
    }

    const winegrower = this.rowToWinegrower(row);

    if (includeRelationships) {
      this.loadWinegrowerRelationships(winegrower);
    }

    return winegrower;
  }

  /**
   * Get all winegrower slugs (for SSG page generation)
   */
  getAllWinegrowerSlugs(): string[] {
    const rows = this.db.prepare(
      'SELECT business_name FROM producers ORDER BY business_name'
    ).all() as { business_name: string }[];

    return rows.map(row => slugify(row.business_name));
  }

  /**
   * Get all winegrower permit IDs (for SSG page generation)
   * @deprecated Use getAllWinegrowerSlugs() instead for SEO-friendly URLs
   */
  getAllWinegrowerIds(): string[] {
    const rows = this.db.prepare(
      'SELECT permit_id FROM producers ORDER BY business_name'
    ).all() as { permit_id: string }[];

    return rows.map(row => row.permit_id);
  }

  /**
   * Get all winegrowers (basic info only)
   */
  getAllWinegrowers(includeRelationships = false): Winegrower[] {
    const rows = this.db.prepare(
      'SELECT * FROM producers ORDER BY business_name'
    ).all() as any[];

    const winegrowers = rows.map(row => this.rowToWinegrower(row));

    if (includeRelationships) {
      winegrowers.forEach(winegrower => this.loadWinegrowerRelationships(winegrower));
    }

    return winegrowers;
  }

  /**
   * Get winegrowers by country
   */
  getWinegrowersByCountry(country: string): Winegrower[] {
    const rows = this.db.prepare(
      'SELECT * FROM producers WHERE country = ? ORDER BY business_name'
    ).all(country) as any[];

    return rows.map(row => this.rowToWinegrower(row));
  }

  /**
   * Get winegrowers by state/province
   */
  getWinegrowersByStateProvince(stateProvince: string): Winegrower[] {
    const rows = this.db.prepare(
      'SELECT * FROM producers WHERE state_province = ? ORDER BY business_name'
    ).all(stateProvince) as any[];

    return rows.map(row => this.rowToWinegrower(row));
  }

  /**
   * Full-text search across winegrowers
   * Searches business_name, permit_holder, wine_label, and city
   */
  searchWinegrowers(query: string): Winegrower[] {
    const rows = this.db.prepare(`
      SELECT p.*
      FROM producers p
      JOIN producers_fts ON producers_fts.rowid = p.id
      WHERE producers_fts MATCH ?
      ORDER BY p.business_name
    `).all(query) as any[];

    return rows.map(row => this.rowToWinegrower(row));
  }

  // ========================================
  // Grape variety queries
  // ========================================

  /**
   * Get grape variety by name with optional relationships
   */
  getVariety(name: string, includeRelationships = false): GrapeVariety | null {
    const row = this.db.prepare(
      'SELECT * FROM grape_varieties WHERE name = ?'
    ).get(name) as any;

    if (!row) {
      return null;
    }

    const variety = this.rowToVariety(row);

    if (includeRelationships) {
      this.loadVarietyRelationships(variety);
    }

    return variety;
  }

  /**
   * Get variety by VIVC number
   */
  getVarietyByVivcId(vivcId: number, includeRelationships = false): GrapeVariety | null {
    const row = this.db.prepare(
      'SELECT * FROM grape_varieties WHERE vivc_number = ?'
    ).get(vivcId) as any;

    if (!row) {
      return null;
    }

    const variety = this.rowToVariety(row);

    if (includeRelationships) {
      this.loadVarietyRelationships(variety);
    }

    return variety;
  }

  /**
   * Get all variety names (for SSG page generation)
   */
  getAllVarietyNames(): string[] {
    const rows = this.db.prepare(
      'SELECT name FROM grape_varieties ORDER BY name'
    ).all() as { name: string }[];

    return rows.map(row => row.name);
  }

  /**
   * Get all variety slugs (for SSG page generation).
   * Appends VIVC number when two varieties produce the same base slug.
   */
  getAllVarietySlugs(): string[] {
    const rows = this.db.prepare(
      'SELECT name, vivc_number FROM grape_varieties ORDER BY name'
    ).all() as { name: string; vivc_number: number | null }[];

    const count: Record<string, number> = {};
    rows.forEach(r => { const s = slugify(r.name); count[s] = (count[s] || 0) + 1; });

    return rows.map(r => {
      const s = slugify(r.name);
      return count[s] > 1 ? `${s}-${r.vivc_number}` : s;
    });
  }

  /**
   * Get variety by URL slug
   */
  getVarietyBySlug(slug: string, includeRelationships = false): GrapeVariety | null {
    const rows = this.db.prepare(
      'SELECT name, vivc_number FROM grape_varieties'
    ).all() as { name: string; vivc_number: number | null }[];

    const count: Record<string, number> = {};
    rows.forEach(r => { const s = slugify(r.name); count[s] = (count[s] || 0) + 1; });

    const row = rows.find(r => {
      const s = slugify(r.name);
      const fullSlug = count[s] > 1 ? `${s}-${r.vivc_number}` : s;
      return fullSlug === slug;
    });
    if (!row) return null;

    return this.getVariety(row.name, includeRelationships);
  }

  /**
   * Get all varieties (basic info only)
   */
  getAllVarieties(includeRelationships = false): GrapeVariety[] {
    const rows = this.db.prepare(
      'SELECT * FROM grape_varieties ORDER BY name'
    ).all() as any[];

    const varieties = rows.map(row => this.rowToVariety(row));

    if (includeRelationships) {
      varieties.forEach(variety => this.loadVarietyRelationships(variety));
    }

    return varieties;
  }

  /**
   * Get varieties by species
   */
  getVarietiesBySpecies(species: string): GrapeVariety[] {
    const rows = this.db.prepare(
      'SELECT * FROM grape_varieties WHERE species = ? ORDER BY name'
    ).all(species) as any[];

    return rows.map(row => this.rowToVariety(row));
  }

  /**
   * Get varieties by berry color
   */
  getVarietiesByColor(color: string): GrapeVariety[] {
    const rows = this.db.prepare(
      'SELECT * FROM grape_varieties WHERE berry_skin_color = ? ORDER BY name'
    ).all(color) as any[];

    return rows.map(row => this.rowToVariety(row));
  }

  /**
   * Search grape varieties by name (LIKE search)
   */
  searchVarieties(query: string): GrapeVariety[] {
    const rows = this.db.prepare(`
      SELECT * FROM grape_varieties
      WHERE name LIKE ?
      ORDER BY name
    `).all(`%${query}%`) as any[];

    return rows.map(row => this.rowToVariety(row));
  }

  // ========================================
  // Wine queries
  // ========================================

  /**
   * Get wine by ID with grape composition
   */
  getWine(wineId: number, includeGrapes = true): Wine | null {
    const row = this.db.prepare(
      'SELECT * FROM wines WHERE id = ?'
    ).get(wineId) as any;

    if (!row) {
      return null;
    }

    const wine = this.rowToWine(row);

    if (includeGrapes) {
      this.loadWineGrapes(wine);
    }

    return wine;
  }

  /**
   * Get all wines for a winegrower
   */
  getWinesByWinegrower(permitId: string): Wine[] {
    const rows = this.db.prepare(`
      SELECT w.*
      FROM wines w
      JOIN producers p ON w.producer_id = p.id
      WHERE p.permit_id = ?
      ORDER BY w.name
    `).all(permitId) as any[];

    const wines = rows.map(row => this.rowToWine(row));
    wines.forEach(wine => this.loadWineGrapes(wine));

    return wines;
  }

  /**
   * Get all wines using a specific grape variety
   */
  getWinesWithVariety(varietyName: string): Wine[] {
    const rows = this.db.prepare(`
      SELECT w.*
      FROM wines w
      JOIN wine_grapes wg ON w.id = wg.wine_id
      JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
      WHERE gv.name = ?
      ORDER BY w.name
    `).all(varietyName) as any[];

    const wines = rows.map(row => this.rowToWine(row));
    wines.forEach(wine => this.loadWineGrapes(wine));

    return wines;
  }

  /**
   * Full-text search across wines
   */
  searchWines(query: string): Wine[] {
    const rows = this.db.prepare(`
      SELECT w.*
      FROM wines w
      JOIN wines_fts ON wines_fts.rowid = w.id
      WHERE wines_fts MATCH ?
      ORDER BY w.name
    `).all(query) as any[];

    const wines = rows.map(row => this.rowToWine(row));
    wines.forEach(wine => this.loadWineGrapes(wine));

    return wines;
  }

  // ========================================
  // Statistics
  // ========================================

  /**
   * Get comprehensive database statistics
   */
  getStats(): DatabaseStats {
    const stats: DatabaseStats = {
      total_winegrowers: 0,
      total_varieties: 0,
      total_wines: 0,
      true_grapes: 0,
      countries: {},
      top_states_provinces: {},
      species: {},
      berry_colors: {},
      geolocated_winegrowers: 0,
      winegrowers_with_websites: 0
    };

    // Basic counts
    stats.total_winegrowers = (this.db.prepare(
      'SELECT COUNT(*) as count FROM producers'
    ).get() as { count: number }).count;

    stats.total_varieties = (this.db.prepare(
      'SELECT COUNT(*) as count FROM grape_varieties'
    ).get() as { count: number }).count;

    stats.total_wines = (this.db.prepare(
      'SELECT COUNT(*) as count FROM wines'
    ).get() as { count: number }).count;

    stats.true_grapes = (this.db.prepare(
      'SELECT COUNT(*) as count FROM grape_varieties WHERE is_grape = 1'
    ).get() as { count: number }).count;

    // Country breakdown
    const countryRows = this.db.prepare(`
      SELECT country, COUNT(*) as count
      FROM producers
      GROUP BY country
      ORDER BY count DESC
    `).all() as { country: string; count: number }[];

    countryRows.forEach(row => {
      stats.countries[row.country] = row.count;
    });

    // State/Province breakdown (top 10)
    const stateRows = this.db.prepare(`
      SELECT state_province, COUNT(*) as count
      FROM producers
      WHERE state_province IS NOT NULL
      GROUP BY state_province
      ORDER BY count DESC
      LIMIT 10
    `).all() as { state_province: string; count: number }[];

    stateRows.forEach(row => {
      stats.top_states_provinces[row.state_province] = row.count;
    });

    // Species breakdown
    const speciesRows = this.db.prepare(`
      SELECT species, COUNT(*) as count
      FROM grape_varieties
      WHERE species IS NOT NULL
      GROUP BY species
      ORDER BY count DESC
    `).all() as { species: string; count: number }[];

    speciesRows.forEach(row => {
      stats.species[row.species] = row.count;
    });

    // Berry color breakdown
    const colorRows = this.db.prepare(`
      SELECT berry_skin_color, COUNT(*) as count
      FROM grape_varieties
      WHERE berry_skin_color IS NOT NULL
      GROUP BY berry_skin_color
      ORDER BY count DESC
    `).all() as { berry_skin_color: string; count: number }[];

    colorRows.forEach(row => {
      stats.berry_colors[row.berry_skin_color] = row.count;
    });

    // Geolocated winegrowers
    stats.geolocated_winegrowers = (this.db.prepare(
      'SELECT COUNT(*) as count FROM producers WHERE latitude IS NOT NULL AND longitude IS NOT NULL'
    ).get() as { count: number }).count;

    // Winegrowers with websites
    stats.winegrowers_with_websites = (this.db.prepare(
      "SELECT COUNT(*) as count FROM producers WHERE website IS NOT NULL AND website != ''"
    ).get() as { count: number }).count;

    return stats;
  }

  // ========================================
  // Map data
  // ========================================

  /**
   * Get all winegrowers with coordinates for map display
   */
  getMapMarkers(): MapMarker[] {
    const rows = this.db.prepare(`
      SELECT
        p.permit_id,
        p.business_name as name,
        p.latitude as lat,
        p.longitude as lng,
        p.city,
        p.state_province,
        p.country
      FROM producers p
      WHERE p.latitude IS NOT NULL AND p.longitude IS NOT NULL
      ORDER BY p.business_name
    `).all() as any[];

    return rows.map(row => ({
      permit_id: row.permit_id,
      name: row.name,
      lat: row.lat,
      lng: row.lng,
      city: row.city,
      state_province: row.state_province,
      country: row.country,
      varieties: this.getVarietiesForWinegrower(row.permit_id),
      wine_types: this.getWineTypesForWinegrower(row.permit_id)
    }));
  }

  // ========================================
  // Helper methods
  // ========================================

  private rowToWinegrower(row: any): Winegrower {
    return {
      id: row.id,
      permit_id: row.permit_id,
      slug: slugify(row.business_name),
      business_name: row.business_name,
      city: row.city,
      state_province: row.state_province,
      country: row.country,
      latitude: row.latitude,
      longitude: row.longitude,
      website: row.website,
      wine_label: row.wine_label,
      permit_holder: row.permit_holder,
      address: row.address,
      postal_code: row.postal_code,
      classification: row.classification,
      verified_wine_producer: Boolean(row.verified_wine_producer),
      source: row.source,
      geocoding_method: row.geocoding_method,
      enriched_at: row.enriched_at,
      created_at: row.created_at
    };
  }

  private rowToVariety(row: any): GrapeVariety {
    const variety: GrapeVariety = {
      id: row.id,
      name: row.name,
      is_grape: Boolean(row.is_grape),
      vivc_number: row.vivc_number,
      berry_skin_color: row.berry_skin_color,
      country_of_origin: row.country_of_origin,
      species: row.species,
      parent1_name: row.parent1_name,
      parent2_name: row.parent2_name,
      sex_of_flower: row.sex_of_flower,
      year_of_crossing: row.year_of_crossing,
      vivc_assignment_status: row.vivc_assignment_status,
      no_wine: Boolean(row.no_wine),
      source: row.source,
      aliases: [],
      photos: []
    };

    // Load photos from database
    this.loadVarietyPhotos(variety);

    return variety;
  }

  private loadVarietyPhotos(variety: GrapeVariety): void {
    const photoRows = this.db.prepare(`
      SELECT id, photo_type, filename, gcs_url, vivc_url, credits
      FROM grape_variety_photos
      WHERE grape_variety_id = ?
      ORDER BY
        CASE photo_type
          WHEN 'Cluster in the field' THEN 1
          WHEN 'Mature leaf' THEN 2
          ELSE 3
        END
    `).all(variety.id) as any[];

    variety.photos = photoRows.map(row => ({
      id: row.id,
      filename: row.filename,
      type: row.photo_type,
      gcs_url: row.gcs_url,
      vivc_url: row.vivc_url,
      credits: row.credits
    }));
  }

  private rowToWine(row: any): Wine {
    return {
      id: row.id,
      winegrower_id: row.producer_id,
      name: row.name,
      description: row.description,
      winemaking: row.winemaking,
      type: row.type,
      vintage: row.vintage,
      grapes: []
    };
  }

  private loadWinegrowerRelationships(winegrower: Winegrower): void {
    // Load wines
    const wineRows = this.db.prepare(
      'SELECT * FROM wines WHERE producer_id = ? ORDER BY name'
    ).all(winegrower.id) as any[];

    winegrower.wines = wineRows.map(row => {
      const wine = this.rowToWine(row);
      this.loadWineGrapes(wine);
      return wine;
    });

    // Load social media
    const socialRows = this.db.prepare(
      'SELECT url FROM producer_social_media WHERE producer_id = ?'
    ).all(winegrower.id) as { url: string }[];

    winegrower.social_media = socialRows.map(row => row.url);

    // Load activities
    const activityRows = this.db.prepare(
      'SELECT activity FROM producer_activities WHERE producer_id = ?'
    ).all(winegrower.id) as { activity: string }[];

    winegrower.activities = activityRows.map(row => row.activity);
  }

  private loadVarietyRelationships(variety: GrapeVariety): void {
    // Load aliases
    const aliasRows = this.db.prepare(
      'SELECT alias FROM grape_aliases WHERE grape_variety_id = ?'
    ).all(variety.id) as { alias: string }[];

    variety.aliases = aliasRows.map(row => row.alias);

    // Load producer count directly from database
    const producerCount = this.db.prepare(`
      SELECT COUNT(DISTINCT w.producer_id) as count
      FROM wines w
      JOIN wine_grapes wg ON w.id = wg.wine_id
      JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
      WHERE gv.name = ?
    `).get(variety.name) as { count: number } | undefined;

    // Load usage from database (which winegrowers use this variety)
    const producerRows = this.db.prepare(`
      SELECT DISTINCT p.permit_id as winegrower_id, p.business_name as winegrower_name
      FROM producers p
      JOIN wines w ON p.id = w.producer_id
      JOIN wine_grapes wg ON w.id = wg.wine_id
      JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
      WHERE gv.name = ?
      ORDER BY p.business_name
    `).all(variety.name) as { winegrower_id: string; winegrower_name: string }[];

    variety.uses = producerRows.map(row => ({
      wine_id: 0, // Not needed for producer count
      wine_name: '', // Not needed for producer count
      winegrower_id: row.winegrower_id,
      winegrower_name: row.winegrower_name
    }));
  }

  private loadWineGrapes(wine: Wine): void {
    const grapeRows = this.db.prepare(`
      SELECT gv.name as variety_name
      FROM wine_grapes wg
      JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
      WHERE wg.wine_id = ?
      ORDER BY gv.name
    `).all(wine.id) as { variety_name: string }[];

    wine.grapes = grapeRows.map(row => ({
      variety_name: row.variety_name
    }));
  }

  private getVarietiesForWinegrower(permitId: string): string[] {
    const rows = this.db.prepare(`
      SELECT DISTINCT gv.name
      FROM wines w
      JOIN producers p ON w.producer_id = p.id
      JOIN wine_grapes wg ON w.id = wg.wine_id
      JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
      WHERE p.permit_id = ?
      ORDER BY gv.name
    `).all(permitId) as { name: string }[];

    return rows.map(row => row.name);
  }

  private getWineTypesForWinegrower(permitId: string): string[] {
    const rows = this.db.prepare(`
      SELECT DISTINCT w.type
      FROM wines w
      JOIN producers p ON w.producer_id = p.id
      WHERE p.permit_id = ? AND w.type IS NOT NULL
      ORDER BY w.type
    `).all(permitId) as { type: string }[];

    return rows.map(row => row.type);
  }

  /**
   * Get minimal data for client-side search (varieties + winegrowers with aliases)
   */
  getSearchData(): { varieties: SearchVarietyItem[]; winegrowers: SearchWinegrowerItem[] } {
    const varietyRows = this.db.prepare(`
      SELECT gv.name, gv.berry_skin_color, gv.country_of_origin,
             GROUP_CONCAT(ga.alias, '|||') as aliases_str
      FROM grape_varieties gv
      LEFT JOIN grape_aliases ga ON ga.grape_variety_id = gv.id
      GROUP BY gv.id
      ORDER BY gv.name
    `).all() as Array<{ name: string; berry_skin_color?: string; country_of_origin?: string; aliases_str?: string }>;

    const winegrowerRows = this.db.prepare(`
      SELECT business_name, city, state_province, country
      FROM producers
      ORDER BY business_name
    `).all() as Array<{ business_name: string; city?: string; state_province?: string; country?: string }>;

    return {
      varieties: varietyRows.map(v => ({
        type: 'variety' as const,
        name: v.name,
        color: v.berry_skin_color,
        country: v.country_of_origin,
        aliases: v.aliases_str ? v.aliases_str.split('|||') : [],
      })),
      winegrowers: winegrowerRows.map(w => ({
        type: 'winegrower' as const,
        name: w.business_name,
        slug: slugify(w.business_name),
        city: w.city,
        state: w.state_province,
        country: w.country,
      })),
    };
  }

  /**
   * Get top varieties by usage count (number of wines)
   */
  getTopVarietiesByUsage(limit = 20): Array<{ name: string; count: number; winegrowers: number }> {
    const rows = this.db.prepare(`
      SELECT
        gv.name,
        COUNT(DISTINCT wg.wine_id) as count,
        COUNT(DISTINCT w.producer_id) as winegrowers
      FROM grape_varieties gv
      JOIN wine_grapes wg ON gv.id = wg.grape_variety_id
      JOIN wines w ON wg.wine_id = w.id
      GROUP BY gv.id, gv.name
      ORDER BY count DESC, winegrowers DESC
      LIMIT ?
    `).all(limit) as Array<{ name: string; count: number; winegrowers: number }>;

    return rows;
  }

  // ========================================
  // Production Statistics
  // ========================================

  /**
   * Get production statistics for a grape variety
   */
  getVarietyProductionStats(varietyName: string): VarietyProductionStats | null {
    // Check if variety exists
    const variety = this.getVariety(varietyName);
    if (!variety) return null;

    return {
      varietal_stats: this.getVarietalStats(varietyName),
      common_blends: this.getCommonBlends(varietyName),
      planted_neighbors: this.getPlantedNeighbors(varietyName),
      top_producers: this.getTopProducers(varietyName),
      geographic_distribution: this.getGeographicDistribution(varietyName)
    };
  }

  /**
   * Calculate proportion of varietal vs blended wines
   */
  private getVarietalStats(varietyName: string): VarietalStats {
    const result = this.db.prepare(`
      WITH variety_wines AS (
        SELECT
          wg.wine_id,
          (SELECT COUNT(*) FROM wine_grapes wg2 WHERE wg2.wine_id = wg.wine_id) as grape_count
        FROM wine_grapes wg
        JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
        WHERE gv.name = ?
      )
      SELECT
        SUM(CASE WHEN grape_count = 1 THEN 1 ELSE 0 END) as varietal_count,
        SUM(CASE WHEN grape_count > 1 THEN 1 ELSE 0 END) as blended_count,
        COUNT(*) as total_wines,
        ROUND(100.0 * SUM(CASE WHEN grape_count = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as varietal_percentage
      FROM variety_wines
    `).get(varietyName) as any;

    return result || { varietal_count: 0, blended_count: 0, total_wines: 0, varietal_percentage: 0 };
  }

  /**
   * Get most common blend partners for a variety
   */
  private getCommonBlends(varietyName: string, limit = 10): BlendPartner[] {
    const rows = this.db.prepare(`
      WITH target_wines AS (
        SELECT DISTINCT wg.wine_id
        FROM wine_grapes wg
        JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
        WHERE gv.name = ?
      ),
      wine_count AS (
        SELECT COUNT(*) as total FROM target_wines
      )
      SELECT
        gv2.name as variety_name,
        COUNT(DISTINCT tw.wine_id) as co_occurrence_count,
        ROUND(100.0 * COUNT(DISTINCT tw.wine_id) / (SELECT total FROM wine_count), 1) as percentage
      FROM target_wines tw
      JOIN wine_grapes wg2 ON tw.wine_id = wg2.wine_id
      JOIN grape_varieties gv2 ON wg2.grape_variety_id = gv2.id
      WHERE gv2.name != ?
      GROUP BY gv2.name
      ORDER BY co_occurrence_count DESC
      LIMIT ?
    `).all(varietyName, varietyName, limit) as any[];

    return rows;
  }

  /**
   * Get varieties commonly planted at the same winegrowers
   */
  private getPlantedNeighbors(varietyName: string, limit = 10): PlantedNeighbor[] {
    const rows = this.db.prepare(`
      WITH target_producers AS (
        SELECT DISTINCT w.producer_id
        FROM wines w
        JOIN wine_grapes wg ON w.id = wg.wine_id
        JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
        WHERE gv.name = ?
      ),
      producer_count AS (
        SELECT COUNT(*) as total FROM target_producers
      )
      SELECT
        gv2.name as variety_name,
        COUNT(DISTINCT tp.producer_id) as producer_count,
        ROUND(100.0 * COUNT(DISTINCT tp.producer_id) / (SELECT total FROM producer_count), 1) as percentage
      FROM target_producers tp
      JOIN wines w2 ON tp.producer_id = w2.producer_id
      JOIN wine_grapes wg2 ON w2.id = wg2.wine_id
      JOIN grape_varieties gv2 ON wg2.grape_variety_id = gv2.id
      WHERE gv2.name != ?
      GROUP BY gv2.name
      ORDER BY producer_count DESC
      LIMIT ?
    `).all(varietyName, varietyName, limit) as any[];

    return rows;
  }

  /**
   * Get producers who use this variety most frequently
   */
  private getTopProducers(varietyName: string, minWines = 3, limit = 15): ProducerUsage[] {
    const rows = this.db.prepare(`
      WITH producer_totals AS (
        SELECT
          p.id,
          p.permit_id,
          p.business_name,
          p.state_province,
          p.country,
          COUNT(DISTINCT w.id) as total_wines
        FROM producers p
        JOIN wines w ON p.id = w.producer_id
        GROUP BY p.id
      ),
      producer_variety_usage AS (
        SELECT
          p.id,
          COUNT(DISTINCT w.id) as wines_with_variety
        FROM producers p
        JOIN wines w ON p.id = w.producer_id
        JOIN wine_grapes wg ON w.id = wg.wine_id
        JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
        WHERE gv.name = ?
        GROUP BY p.id
        HAVING COUNT(DISTINCT w.id) >= ?
      )
      SELECT
        pt.permit_id as producer_id,
        pt.business_name,
        pvu.wines_with_variety,
        pt.total_wines,
        ROUND(100.0 * pvu.wines_with_variety / pt.total_wines, 1) as usage_percentage,
        pt.state_province,
        pt.country
      FROM producer_totals pt
      JOIN producer_variety_usage pvu ON pt.id = pvu.id
      ORDER BY usage_percentage DESC, wines_with_variety DESC
      LIMIT ?
    `).all(varietyName, minWines, limit) as any[];

    return rows;
  }

  /**
   * Get geographic distribution of variety usage
   */
  private getGeographicDistribution(varietyName: string, limit = 15): GeographicDistribution[] {
    const rows = this.db.prepare(`
      WITH total_wines AS (
        SELECT COUNT(DISTINCT w.id) as total
        FROM wines w
        JOIN wine_grapes wg ON w.id = wg.wine_id
        JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
        WHERE gv.name = ?
      )
      SELECT
        p.state_province,
        p.country,
        COUNT(DISTINCT p.id) as producer_count,
        COUNT(DISTINCT w.id) as wine_count,
        ROUND(100.0 * COUNT(DISTINCT w.id) / (SELECT total FROM total_wines), 1) as percentage
      FROM producers p
      JOIN wines w ON p.id = w.producer_id
      JOIN wine_grapes wg ON w.id = wg.wine_id
      JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
      WHERE gv.name = ?
        AND p.state_province IS NOT NULL
        AND p.state_province != ''
      GROUP BY p.state_province, p.country
      ORDER BY wine_count DESC
      LIMIT ?
    `).all(varietyName, varietyName, limit) as any[];

    return rows;
  }

  /**
   * Get photo thumbnails for multiple varieties
   * Returns a map of variety name -> photo URL
   */
  getVarietyPhotoThumbnails(varietyNames: string[]): Map<string, string> {
    const photoMap = new Map<string, string>();

    if (varietyNames.length === 0) {
      return photoMap;
    }

    // Build placeholders for SQL IN clause
    const placeholders = varietyNames.map(() => '?').join(',');

    const rows = this.db.prepare(`
      SELECT
        gv.name,
        gvp.gcs_url
      FROM grape_varieties gv
      LEFT JOIN grape_variety_photos gvp ON gv.id = gvp.grape_variety_id
      WHERE gv.name IN (${placeholders})
        AND (gvp.photo_type = 'Cluster in the field' OR gvp.photo_type IS NULL)
      GROUP BY gv.name
    `).all(...varietyNames) as any[];

    rows.forEach(row => {
      // Use GCS URL directly
      if (row.gcs_url) {
        photoMap.set(row.name, row.gcs_url);
      }
    });

    return photoMap;
  }

  /**
   * Get list of indexed states/provinces (regions with winegrowers)
   * Used for map overlay to show coverage
   */
  getIndexedRegions(): Array<{ state_province: string; country: string; count: number }> {
    const rows = this.db.prepare(`
      SELECT
        state_province,
        country,
        COUNT(*) as count
      FROM producers
      WHERE state_province IS NOT NULL
        AND state_province != ''
      GROUP BY state_province, country
      ORDER BY country, state_province
    `).all() as any[];

    return rows.map(row => ({
      state_province: row.state_province,
      country: row.country,
      count: row.count
    }));
  }

  /**
   * Close database connection
   */
  close(): void {
    if (this.db) {
      this.db.close();
    }
  }
}

// ========================================
// Database factory
// ========================================

/**
 * Get database instance
 *
 * Creates a new instance for each call to avoid connection conflicts
 * during Next.js static site generation (SSG) where pages are built in parallel.
 *
 * SQLite connections are lightweight and better-sqlite3 handles them efficiently.
 */
export function getDatabase(dbPath?: string): GrapeGeekDB {
  return new GrapeGeekDB(dbPath);
}
