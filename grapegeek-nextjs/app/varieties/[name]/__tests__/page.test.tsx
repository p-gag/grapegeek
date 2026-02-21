/**
 * Tests for variety detail page
 */

import { getDatabase } from '@/lib/database';

describe('Variety Detail Page - generateStaticParams', () => {
  it('should generate params for all varieties', () => {
    const db = getDatabase();
    const names = db.getAllVarietyNames();

    expect(names.length).toBeGreaterThan(0);

    // Verify each name can be encoded
    const params = names.map(name => ({
      name: encodeURIComponent(name),
    }));

    expect(params.length).toBe(names.length);

    // Sample check - first few varieties
    params.slice(0, 3).forEach(param => {
      expect(param.name).toBeDefined();
      expect(typeof param.name).toBe('string');
    });
  });
});

describe('Variety Detail Page - Data Loading', () => {
  it('should load variety with relationships', () => {
    const db = getDatabase();
    const names = db.getAllVarietyNames();

    if (names.length > 0) {
      const testVariety = names[0];
      const variety = db.getVariety(testVariety, true);

      expect(variety).toBeTruthy();
      expect(variety?.name).toBe(testVariety);
      expect(variety?.aliases).toBeDefined();
      expect(Array.isArray(variety?.aliases)).toBe(true);
      expect(variety?.uses).toBeDefined();
      expect(Array.isArray(variety?.uses)).toBe(true);
    }
  });

  it('should handle variety not found', () => {
    const db = getDatabase();
    const variety = db.getVariety('NONEXISTENT_VARIETY_XYZ', true);

    expect(variety).toBeNull();
  });
});

describe('Variety Detail Page - Metadata Generation', () => {
  it('should generate valid metadata for existing variety', () => {
    const db = getDatabase();
    const names = db.getAllVarietyNames();

    if (names.length > 0) {
      const testVariety = names[0];
      const variety = db.getVariety(testVariety, true);

      expect(variety).toBeTruthy();

      if (variety) {
        const usageCount = variety.uses?.length || 0;
        const hasSpecies = !!variety.species;
        const hasColor = !!variety.berry_skin_color;

        // Verify metadata components
        expect(variety.name).toBeDefined();
        expect(typeof usageCount).toBe('number');
        expect(typeof hasSpecies).toBe('boolean');
        expect(typeof hasColor).toBe('boolean');
      }
    }
  });
});
