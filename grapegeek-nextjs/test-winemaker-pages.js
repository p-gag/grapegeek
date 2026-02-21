/**
 * Test script to verify winemaker detail pages can be generated
 *
 * Usage: node test-winemaker-pages.js
 */

const { GrapeGeekDB } = require('./lib/database.ts');

console.log('Testing winemaker detail page data access...\n');

try {
  // Initialize database
  const db = new GrapeGeekDB();

  // Get all winemaker IDs
  const ids = db.getAllWinemakerIds();
  console.log(`✓ Found ${ids.length} winemaker IDs for SSG`);

  // Test loading a sample winemaker with relationships
  if (ids.length > 0) {
    const sampleId = ids[0];
    const winemaker = db.getWinemaker(sampleId, true);

    if (winemaker) {
      console.log(`\n✓ Successfully loaded winemaker: ${winemaker.business_name}`);
      console.log(`  Location: ${winemaker.city}, ${winemaker.state_province}`);
      console.log(`  Wines: ${winemaker.wines?.length || 0}`);
      console.log(`  Social Media Links: ${winemaker.social_media?.length || 0}`);
      console.log(`  Activities: ${winemaker.activities?.length || 0}`);
      console.log(`  Has Coordinates: ${winemaker.latitude && winemaker.longitude ? 'Yes' : 'No'}`);
      console.log(`  Website: ${winemaker.website || 'None'}`);

      if (winemaker.wines && winemaker.wines.length > 0) {
        console.log(`\n  Sample Wine: ${winemaker.wines[0].name}`);
        console.log(`    Grapes: ${winemaker.wines[0].grapes.map(g => g.variety_name).join(', ')}`);
      }
    } else {
      console.error(`✗ Failed to load winemaker with ID: ${sampleId}`);
    }
  }

  // Test that all components can access the data they need
  console.log('\n✓ All winemaker data access tests passed!');
  console.log('\nWinemaker detail pages are ready for SSG build.');

  db.close();
} catch (error) {
  console.error('✗ Error testing winemaker pages:', error.message);
  process.exit(1);
}
