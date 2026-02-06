#!/usr/bin/env node

import { copyFileSync, mkdirSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Source and destination paths
const sourcePath = resolve(__dirname, 'src/data/tree-data.json');
const destPath = resolve(__dirname, '../docs/family-trees/tree-data.json');

try {
  // Ensure destination directory exists first
  mkdirSync(dirname(destPath), { recursive: true });

  // Check if source file exists
  if (!existsSync(sourcePath)) {
    console.log('⚠️  Tree data file not found, creating empty data for development');
    console.log(`   Expected: ${sourcePath}`);
    console.log('   Run: cd grape-tree-react && uv run ../src/18_generate_tree_data.py');
    
    // Create empty data structure for development
    const emptyData = {
      varieties: [],
      nodes: [],
      edges: []
    };
    
    // Write empty data using sync methods
    import('fs').then(fs => {
      fs.writeFileSync(destPath, JSON.stringify(emptyData, null, 2));
      console.log('📝 Created empty tree data file for development');
    });
    
    process.exit(0);
  }

  // Copy the file
  copyFileSync(sourcePath, destPath);
  console.log('✅ Tree data copied successfully');
  console.log(`   From: ${sourcePath}`);
  console.log(`   To: ${destPath}`);

} catch (error) {
  console.error('❌ Error copying tree data:', error.message);
  process.exit(1);
}