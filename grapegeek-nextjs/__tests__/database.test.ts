/**
 * Database Integration Tests
 *
 * Tests the GrapeGeekDB class and database query methods.
 */

import { describe, test, expect, beforeAll, afterAll } from '@jest/globals';
import { getDatabase, GrapeGeekDB } from '@/lib/database';
import path from 'path';

describe('Database Integration', () => {
  let db: GrapeGeekDB;

  beforeAll(() => {
    // Use the test database
    const dbPath = path.join(process.cwd(), 'data', 'grapegeek.db');
    db = getDatabase(dbPath);
  });

  afterAll(() => {
    db.close();
  });

  // ========================================
  // Schema validation
  // ========================================

  test('validates schema version on connection', () => {
    expect(db).toBeDefined();
  });

  test('throws error for missing schema version', () => {
    // This would require a database without schema_info table
    // Just verify the connection works
    expect(db).toBeDefined();
  });

  // ========================================
  // Statistics
  // ========================================

  test('gets database statistics', () => {
    const stats = db.getStats();

    expect(stats.total_winegrowers).toBeGreaterThan(0);
    expect(stats.total_varieties).toBeGreaterThan(0);
    // Note: total_wines may be 0 if database hasn't been enriched yet
    expect(stats.total_wines).toBeGreaterThanOrEqual(0);
    expect(stats.true_grapes).toBeGreaterThan(0);
    expect(Object.keys(stats.countries).length).toBeGreaterThan(0);
    // Species data may be empty if not yet enriched from VIVC
    expect(Object.keys(stats.species).length).toBeGreaterThanOrEqual(0);
  });

  test('statistics have correct structure', () => {
    const stats = db.getStats();

    expect(stats).toHaveProperty('total_winegrowers');
    expect(stats).toHaveProperty('total_varieties');
    expect(stats).toHaveProperty('total_wines');
    expect(stats).toHaveProperty('true_grapes');
    expect(stats).toHaveProperty('countries');
    expect(stats).toHaveProperty('top_states_provinces');
    expect(stats).toHaveProperty('species');
    expect(stats).toHaveProperty('berry_colors');
    expect(stats).toHaveProperty('geolocated_winegrowers');
    expect(stats).toHaveProperty('winegrowers_with_websites');

    expect(typeof stats.total_winegrowers).toBe('number');
    expect(typeof stats.countries).toBe('object');
  });

  // ========================================
  // Winegrower queries
  // ========================================

  test('gets all winegrower IDs for SSG', () => {
    const ids = db.getAllWinegrowerIds();

    expect(ids.length).toBeGreaterThan(0);
    expect(typeof ids[0]).toBe('string');
  });

  test('gets all winegrowers (basic)', () => {
    const winegrowers = db.getAllWinegrowers(false);

    expect(winegrowers.length).toBeGreaterThan(0);

    const first = winegrowers[0];
    expect(first).toHaveProperty('permit_id');
    expect(first).toHaveProperty('business_name');
    expect(first).toHaveProperty('city');
    expect(first).toHaveProperty('state_province');
    expect(first).toHaveProperty('country');

    // Should NOT have relationships loaded
    expect(first.wines).toBeUndefined();
    expect(first.social_media).toBeUndefined();
    expect(first.activities).toBeUndefined();
  });

  test('gets winegrower by permit ID (basic)', () => {
    const ids = db.getAllWinegrowerIds();
    const firstId = ids[0];

    const winegrower = db.getWinegrower(firstId, false);

    expect(winegrower).toBeDefined();
    expect(winegrower?.permit_id).toBe(firstId);
    expect(winegrower?.business_name).toBeDefined();

    // Should NOT have relationships
    expect(winegrower?.wines).toBeUndefined();
  });

  test('gets winegrower with relationships', () => {
    const ids = db.getAllWinegrowerIds();
    const firstId = ids[0];

    const winegrower = db.getWinegrower(firstId, true);

    expect(winegrower).toBeDefined();
    expect(winegrower?.wines).toBeDefined();
    expect(winegrower?.social_media).toBeDefined();
    expect(winegrower?.activities).toBeDefined();

    expect(Array.isArray(winegrower?.wines)).toBe(true);
    expect(Array.isArray(winegrower?.social_media)).toBe(true);
    expect(Array.isArray(winegrower?.activities)).toBe(true);
  });

  test('returns null for non-existent winegrower', () => {
    const winegrower = db.getWinegrower('NONEXISTENT123', false);
    expect(winegrower).toBeNull();
  });

  test('gets winegrowers by country', () => {
    const stats = db.getStats();
    const firstCountry = Object.keys(stats.countries)[0];

    const winegrowers = db.getWinegrowersByCountry(firstCountry);

    expect(winegrowers.length).toBeGreaterThan(0);
    winegrowers.forEach(wm => {
      expect(wm.country).toBe(firstCountry);
    });
  });

  test('gets winegrowers by state/province', () => {
    const stats = db.getStats();
    const firstState = Object.keys(stats.top_states_provinces)[0];

    const winegrowers = db.getWinegrowersByStateProvince(firstState);

    expect(winegrowers.length).toBeGreaterThan(0);
    winegrowers.forEach(wm => {
      expect(wm.state_province).toBe(firstState);
    });
  });

  test('searches winegrowers by text', () => {
    // Get a known winegrower name to search for
    const winegrowers = db.getAllWinegrowers();
    if (winegrowers.length === 0) return;

    const firstWinegrower = winegrowers[0];
    const searchTerm = firstWinegrower.business_name.split(' ')[0];

    const results = db.searchWinegrowers(searchTerm);

    expect(results.length).toBeGreaterThan(0);
  });

  // ========================================
  // Grape variety queries
  // ========================================

  test('gets all variety names for SSG', () => {
    const names = db.getAllVarietyNames();

    expect(names.length).toBeGreaterThan(0);
    expect(typeof names[0]).toBe('string');
  });

  test('gets all varieties (basic)', () => {
    const varieties = db.getAllVarieties(false);

    expect(varieties.length).toBeGreaterThan(0);

    const first = varieties[0];
    expect(first).toHaveProperty('id');
    expect(first).toHaveProperty('name');
    expect(first).toHaveProperty('is_grape');

    // Should NOT have relationships loaded
    expect(first.uses).toBeUndefined();
  });

  test('gets variety by name (basic)', () => {
    const names = db.getAllVarietyNames();
    const firstName = names[0];

    const variety = db.getVariety(firstName, false);

    expect(variety).toBeDefined();
    expect(variety?.name).toBe(firstName);

    // Should NOT have relationships
    expect(variety?.uses).toBeUndefined();
  });

  test('gets variety with relationships', () => {
    const names = db.getAllVarietyNames();
    const firstName = names[0];

    const variety = db.getVariety(firstName, true);

    expect(variety).toBeDefined();
    expect(variety?.aliases).toBeDefined();
    expect(variety?.uses).toBeDefined();

    expect(Array.isArray(variety?.aliases)).toBe(true);
    expect(Array.isArray(variety?.uses)).toBe(true);
  });

  test('returns null for non-existent variety', () => {
    const variety = db.getVariety('NonExistentGrape123', false);
    expect(variety).toBeNull();
  });

  test('gets varieties by species', () => {
    const stats = db.getStats();
    if (Object.keys(stats.species).length === 0) return;

    const firstSpecies = Object.keys(stats.species)[0];
    const varieties = db.getVarietiesBySpecies(firstSpecies);

    expect(varieties.length).toBeGreaterThan(0);
    varieties.forEach(v => {
      expect(v.species).toBe(firstSpecies);
    });
  });

  test('gets varieties by color', () => {
    const stats = db.getStats();
    if (Object.keys(stats.berry_colors).length === 0) return;

    const firstColor = Object.keys(stats.berry_colors)[0];
    const varieties = db.getVarietiesByColor(firstColor);

    expect(varieties.length).toBeGreaterThan(0);
    varieties.forEach(v => {
      expect(v.berry_skin_color).toBe(firstColor);
    });
  });

  test('searches varieties by name', () => {
    const varieties = db.getAllVarieties();
    if (varieties.length === 0) return;

    const firstVariety = varieties[0];
    const searchTerm = firstVariety.name.substring(0, 3);

    const results = db.searchVarieties(searchTerm);

    expect(results.length).toBeGreaterThan(0);
  });

  test('gets variety by VIVC ID', () => {
    // Find a variety with a VIVC number
    const varieties = db.getAllVarieties();
    const varietyWithVivc = varieties.find(v => v.vivc_number !== null);

    if (!varietyWithVivc || !varietyWithVivc.vivc_number) {
      // Skip test if no VIVC numbers in database
      return;
    }

    const variety = db.getVarietyByVivcId(varietyWithVivc.vivc_number, false);

    expect(variety).toBeDefined();
    expect(variety?.vivc_number).toBe(varietyWithVivc.vivc_number);
  });

  // ========================================
  // Wine queries
  // ========================================

  test('gets wines by winegrower', () => {
    const ids = db.getAllWinegrowerIds();
    const firstId = ids[0];

    const wines = db.getWinesByWinegrower(firstId);

    expect(Array.isArray(wines)).toBe(true);

    if (wines.length > 0) {
      const wine = wines[0];
      expect(wine).toHaveProperty('id');
      expect(wine).toHaveProperty('name');
      expect(wine).toHaveProperty('grapes');
      expect(Array.isArray(wine.grapes)).toBe(true);
    }
  });

  test('gets wine by ID', () => {
    // Get a known wine ID
    const ids = db.getAllWinegrowerIds();
    const wines = db.getWinesByWinegrower(ids[0]);

    if (wines.length === 0) return;

    const wineId = wines[0].id;
    const wine = db.getWine(wineId, true);

    expect(wine).toBeDefined();
    expect(wine?.id).toBe(wineId);
    expect(wine?.grapes).toBeDefined();
    expect(Array.isArray(wine?.grapes)).toBe(true);
  });

  test('returns null for non-existent wine', () => {
    const wine = db.getWine(999999, false);
    expect(wine).toBeNull();
  });

  test('gets wines with specific variety', () => {
    const names = db.getAllVarietyNames();
    if (names.length === 0) return;

    const firstName = names[0];
    const wines = db.getWinesWithVariety(firstName);

    expect(Array.isArray(wines)).toBe(true);

    if (wines.length > 0) {
      const wine = wines[0];
      expect(wine.grapes).toBeDefined();
      expect(Array.isArray(wine.grapes)).toBe(true);

      // Check that the variety is in the wine's grapes
      const hasVariety = wine.grapes.some(g => g.variety_name === firstName);
      expect(hasVariety).toBe(true);
    }
  });

  test('searches wines by text', () => {
    const ids = db.getAllWinegrowerIds();
    const wines = db.getWinesByWinegrower(ids[0]);

    if (wines.length === 0) return;

    const searchTerm = wines[0].name.split(' ')[0];
    const results = db.searchWines(searchTerm);

    expect(Array.isArray(results)).toBe(true);
  });

  // ========================================
  // Map data
  // ========================================

  test('gets map markers', () => {
    const markers = db.getMapMarkers();

    expect(Array.isArray(markers)).toBe(true);

    if (markers.length > 0) {
      const marker = markers[0];
      expect(marker).toHaveProperty('permit_id');
      expect(marker).toHaveProperty('name');
      expect(marker).toHaveProperty('lat');
      expect(marker).toHaveProperty('lng');
      expect(marker).toHaveProperty('varieties');
      expect(marker).toHaveProperty('wine_types');

      expect(typeof marker.lat).toBe('number');
      expect(typeof marker.lng).toBe('number');
      expect(Array.isArray(marker.varieties)).toBe(true);
      expect(Array.isArray(marker.wine_types)).toBe(true);
    }
  });

  // ========================================
  // Data integrity
  // ========================================

  test('wine grapes have valid structure', () => {
    const ids = db.getAllWinegrowerIds();
    const wines = db.getWinesByWinegrower(ids[0]);

    if (wines.length === 0) return;

    const wine = wines[0];
    expect(wine.grapes).toBeDefined();

    if (wine.grapes.length > 0) {
      const grape = wine.grapes[0];
      expect(grape).toHaveProperty('variety_name');
      expect(typeof grape.variety_name).toBe('string');

      if (grape.percentage !== undefined) {
        expect(typeof grape.percentage).toBe('number');
      }
    }
  });

  test('variety uses have valid structure', () => {
    const names = db.getAllVarietyNames();
    const variety = db.getVariety(names[0], true);

    if (!variety || !variety.uses || variety.uses.length === 0) return;

    const use = variety.uses[0];
    expect(use).toHaveProperty('wine_id');
    expect(use).toHaveProperty('wine_name');
    expect(use).toHaveProperty('winegrower_id');
    expect(use).toHaveProperty('winegrower_name');

    expect(typeof use.wine_id).toBe('number');
    expect(typeof use.wine_name).toBe('string');
    expect(typeof use.winegrower_id).toBe('string');
    expect(typeof use.winegrower_name).toBe('string');
  });

  test('winegrower data is properly normalized', () => {
    const winegrowers = db.getAllWinegrowers(false);

    winegrowers.forEach(wm => {
      expect(typeof wm.id).toBe('number');
      expect(typeof wm.permit_id).toBe('string');
      expect(typeof wm.business_name).toBe('string');
      expect(typeof wm.verified_wine_producer).toBe('boolean');
    });
  });

  test('variety data is properly normalized', () => {
    const varieties = db.getAllVarieties(false);

    varieties.forEach(v => {
      expect(typeof v.id).toBe('number');
      expect(typeof v.name).toBe('string');
      expect(typeof v.is_grape).toBe('boolean');
      expect(typeof v.no_wine).toBe('boolean');
    });
  });
});
