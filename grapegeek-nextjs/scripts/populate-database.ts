#!/usr/bin/env tsx
/**
 * Populate SQLite database from JSONL source data
 * Run with: npx tsx scripts/populate-database.ts
 */

import Database from 'better-sqlite3';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';

interface JSONLProducer {
  permit_id: string;
  source: string;
  country: string;
  state_province: string;
  business_name: string;
  permit_holder: string;
  address?: string;
  city: string;
  postal_code?: string;
  classification: string;
  website?: string;
  social_media?: string[];
  latitude?: number;
  longitude?: number;
  geocoding_method?: string;
  verified_wine_producer?: boolean;
  wines?: Array<{
    name: string;
    description?: string;
    winemaking?: string;
    cepages?: string[];
    type?: string;
    vintage?: string;
  }>;
}

const DB_PATH = path.join(process.cwd(), 'data', 'grapegeek.db');
const JSONL_PATH = path.join(process.cwd(), '..', 'data', '05_wine_producers_final_normalized.jsonl');

async function populateDatabase() {
  console.log('Opening database:', DB_PATH);
  const db = new Database(DB_PATH);

  // Enable foreign keys
  db.pragma('foreign_keys = ON');

  // Start transaction for better performance
  db.exec('BEGIN TRANSACTION');

  try {
    // Clear existing data
    console.log('Clearing existing data...');
    db.exec('DELETE FROM wine_grapes');
    db.exec('DELETE FROM wines');
    db.exec('DELETE FROM producer_social_media');

    // Prepare statements
    const getProducerId = db.prepare('SELECT id FROM producers WHERE permit_id = ?');
    const insertWine = db.prepare(`
      INSERT INTO wines (producer_id, name, description, winemaking, type, vintage)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    const insertWineGrape = db.prepare(`
      INSERT INTO wine_grapes (wine_id, variety_name)
      VALUES (?, ?)
    `);
    const insertSocialMedia = db.prepare(`
      INSERT INTO producer_social_media (producer_id, url)
      VALUES (?, ?)
    `);

    // Read and process JSONL file
    console.log('Reading JSONL file:', JSONL_PATH);
    const fileStream = fs.createReadStream(JSONL_PATH);
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    let lineNumber = 0;
    let producersProcessed = 0;
    let winesAdded = 0;
    let socialLinksAdded = 0;
    let varietiesAdded = 0;

    for await (const line of rl) {
      lineNumber++;
      if (!line.trim()) continue;

      try {
        const producer: JSONLProducer = JSON.parse(line);

        // Get producer ID from database
        const producerRow = getProducerId.get(producer.permit_id) as { id: number } | undefined;
        if (!producerRow) {
          console.warn(`Producer not found in database: ${producer.permit_id} (${producer.business_name})`);
          continue;
        }

        const producerId = producerRow.id;
        producersProcessed++;

        // Add social media links
        if (producer.social_media && producer.social_media.length > 0) {
          for (const url of producer.social_media) {
            insertSocialMedia.run(producerId, url);
            socialLinksAdded++;
          }
        }

        // Add wines and grape varieties
        if (producer.wines && producer.wines.length > 0) {
          for (const wine of producer.wines) {
            const wineResult = insertWine.run(
              producerId,
              wine.name,
              wine.description || null,
              wine.winemaking || null,
              wine.type || null,
              wine.vintage || null
            );
            winesAdded++;

            const wineId = wineResult.lastInsertRowid as number;

            // Add grape varieties for this wine
            if (wine.cepages && wine.cepages.length > 0) {
              for (const variety of wine.cepages) {
                insertWineGrape.run(wineId, variety);
                varietiesAdded++;
              }
            }
          }
        }

        if (producersProcessed % 100 === 0) {
          console.log(`Processed ${producersProcessed} producers...`);
        }
      } catch (error) {
        console.error(`Error processing line ${lineNumber}:`, error);
      }
    }

    // Commit transaction
    db.exec('COMMIT');

    console.log('\n✅ Database population complete!');
    console.log(`   Producers processed: ${producersProcessed}`);
    console.log(`   Wines added: ${winesAdded}`);
    console.log(`   Social media links added: ${socialLinksAdded}`);
    console.log(`   Grape varieties added: ${varietiesAdded}`);

    // Verify counts
    const wineCount = db.prepare('SELECT COUNT(*) as count FROM wines').get() as { count: number };
    const socialCount = db.prepare('SELECT COUNT(*) as count FROM producer_social_media').get() as { count: number };
    const varietyCount = db.prepare('SELECT COUNT(*) as count FROM wine_grapes').get() as { count: number };

    console.log('\n📊 Database verification:');
    console.log(`   Wines in DB: ${wineCount.count}`);
    console.log(`   Social links in DB: ${socialCount.count}`);
    console.log(`   Wine-grape relationships in DB: ${varietyCount.count}`);

  } catch (error) {
    db.exec('ROLLBACK');
    console.error('❌ Error populating database:', error);
    throw error;
  } finally {
    db.close();
  }
}

// Run the population script
populateDatabase().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
