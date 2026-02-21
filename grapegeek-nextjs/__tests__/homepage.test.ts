/**
 * Homepage integration test
 * Verifies that the homepage loads with real database statistics
 */

import { getDatabase } from '@/lib/database';

describe('Homepage Statistics', () => {
  it('should load database statistics', () => {
    const db = getDatabase();
    const stats = db.getStats();

    // Verify stats have expected structure
    expect(stats).toBeDefined();
    expect(stats.total_varieties).toBeGreaterThan(0);
    expect(stats.total_winegrowers).toBeGreaterThan(0);
    expect(stats.total_wines).toBeGreaterThanOrEqual(0); // May be 0 if wines not populated yet
    expect(Object.keys(stats.countries).length).toBeGreaterThan(0);
  });

  it('should have variety and winegrower counts', () => {
    const db = getDatabase();
    const stats = db.getStats();

    console.log('Database Statistics:');
    console.log(`- Total Varieties: ${stats.total_varieties}`);
    console.log(`- Total Winegrowers: ${stats.total_winegrowers}`);
    console.log(`- Total Wines: ${stats.total_wines}`);
    console.log(`- Countries: ${Object.keys(stats.countries).length}`);
    console.log(`- Top Country: ${Object.keys(stats.countries)[0]}`);

    // Basic sanity checks
    expect(stats.total_varieties).toBeGreaterThan(50); // Should have at least 50 varieties
    expect(stats.total_winegrowers).toBeGreaterThan(10); // Should have at least 10 winegrowers
  });
});
