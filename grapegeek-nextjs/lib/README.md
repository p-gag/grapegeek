# Database Integration Layer

TypeScript database access layer for GrapeGeek Next.js application using SQLite with better-sqlite3.

## Overview

This layer provides type-safe queries for Static Site Generation (SSG) in Next.js. It mirrors the Python implementation from `src/includes/database.py` but uses TypeScript and better-sqlite3.

## Important Terminology

**CRITICAL:** Throughout the codebase, we use "winegrower" terminology instead of "producer":
- Database table is still `producers` (schema unchanged)
- TypeScript interfaces use `Winemaker` type
- URLs use `/winegrower/:id`
- All user-facing text says "winegrower"

## Files

- `lib/types.ts` - TypeScript interfaces for all data types
- `lib/database.ts` - GrapeGeekDB class with query methods
- `__tests__/database.test.ts` - Comprehensive test suite
- `data/grapegeek.db` - SQLite database file

## Usage

### Basic Usage

```typescript
import { getDatabase } from '@/lib/database';

// Get singleton instance
const db = getDatabase();

// Query data
const stats = db.getStats();
const winegrower = db.getWinemaker('AV006', true);
const varieties = db.getAllVarieties();

// Close when done (optional - singleton will persist)
db.close();
```

### In Next.js Pages (SSG)

#### Generate Static Paths

```typescript
// app/winegrower/[id]/page.tsx
import { getDatabase } from '@/lib/database';

export async function generateStaticParams() {
  const db = getDatabase();
  const ids = db.getAllWinemakerIds();

  return ids.map(id => ({ id }));
}
```

#### Fetch Data for Page

```typescript
// app/winegrower/[id]/page.tsx
import { getDatabase } from '@/lib/database';
import { notFound } from 'next/navigation';

export default function WinemakerPage({ params }: { params: { id: string } }) {
  const db = getDatabase();
  const winegrower = db.getWinemaker(params.id, true);

  if (!winegrower) {
    notFound();
  }

  return (
    <div>
      <h1>{winegrower.business_name}</h1>
      <p>{winegrower.city}, {winegrower.state_province}</p>

      {winegrower.wines && (
        <ul>
          {winegrower.wines.map(wine => (
            <li key={wine.id}>
              {wine.name}
              {wine.grapes.length > 0 && (
                <span> - {wine.grapes.map(g => g.variety_name).join(', ')}</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

## API Reference

### GrapeGeekDB Class

#### Winemaker Methods

- `getWinemaker(permitId, includeRelationships?)` - Get winegrower by permit ID
- `getAllWinemakerIds()` - Get all permit IDs for SSG
- `getAllWinemakers(includeRelationships?)` - Get all winegrowers
- `getWinemakersByCountry(country)` - Filter by country
- `getWinemakersByStateProvince(state)` - Filter by state/province
- `searchWinemakers(query)` - Full-text search

#### Grape Variety Methods

- `getVariety(name, includeRelationships?)` - Get variety by name
- `getVarietyByVivcId(vivcId, includeRelationships?)` - Get by VIVC number
- `getAllVarietyNames()` - Get all names for SSG
- `getAllVarieties(includeRelationships?)` - Get all varieties
- `getVarietiesBySpecies(species)` - Filter by species
- `getVarietiesByColor(color)` - Filter by berry color
- `searchVarieties(query)` - Search by name (LIKE)

#### Wine Methods

- `getWine(wineId, includeGrapes?)` - Get wine by ID
- `getWinesByWinemaker(permitId)` - Get all wines for a winegrower
- `getWinesWithVariety(varietyName)` - Get wines using a variety
- `searchWines(query)` - Full-text search

#### Statistics & Map

- `getStats()` - Comprehensive database statistics
- `getMapMarkers()` - All winegrowers with coordinates for map

### TypeScript Interfaces

#### Winemaker

```typescript
interface Winemaker {
  id: number;
  permit_id: string;
  business_name: string;
  city: string;
  state_province: string;
  country: string;
  latitude?: number;
  longitude?: number;
  website?: string;
  wines?: Wine[];           // Loaded with includeRelationships
  social_media?: string[];  // Loaded with includeRelationships
  activities?: string[];    // Loaded with includeRelationships
}
```

#### Wine

```typescript
interface Wine {
  id: number;
  winegrower_id: number;
  name: string;
  description?: string;
  winemaking?: string;
  type?: string;
  vintage?: string;
  grapes: WineGrape[];
}

interface WineGrape {
  variety_name: string;
  percentage?: number;
}
```

#### GrapeVariety

```typescript
interface GrapeVariety {
  id: number;
  name: string;
  is_grape: boolean;
  vivc_number?: number;
  berry_skin_color?: string;
  species?: string;
  parent1_name?: string;
  parent2_name?: string;
  aliases: string[];
  uses?: GrapeUse[];  // Loaded with includeRelationships
}

interface GrapeUse {
  wine_id: number;
  wine_name: string;
  winegrower_id: string;
  winegrower_name: string;
}
```

## Performance Considerations

### Lazy Loading

Use the `includeRelationships` parameter to control data loading:

```typescript
// Fast - basic info only
const winegrowers = db.getAllWinemakers(false);

// Slower - includes wines, social media, activities
const winegrower = db.getWinemaker('AV006', true);
```

### Build-Time Only

Database access is **build-time only** for Next.js SSG:
- No runtime queries (no API routes needed)
- All data fetched during `next build`
- Results in static HTML files

### Singleton Pattern

The database connection is a singleton:

```typescript
// First call creates instance
const db = getDatabase();

// Subsequent calls return same instance
const db2 = getDatabase();  // Same instance as db

// Reset singleton (useful for testing)
resetDatabase();
```

## Testing

Run the test suite:

```bash
npm test              # Run once
npm run test:watch    # Watch mode
```

Test coverage includes:
- Schema validation
- All query methods
- Data integrity checks
- Relationship loading
- Search functionality
- Statistics generation

## Schema Version Management

The database includes a `schema_info` table with version tracking. The TypeScript layer validates the schema version on connection:

```typescript
const EXPECTED_SCHEMA_VERSION = 1;

// Throws error if version doesn't match
validateSchemaVersion(db);
```

If you see a schema version error:

```
Error: Schema version mismatch: expected 1, got 0.
Please rebuild database: uv run src/09_build_database.py
```

Rebuild the database:

```bash
cd /Users/phil/perso/grapegeek
uv run src/09_build_database.py

# Copy to Next.js project
cp data/grapegeek.db grapegeek-nextjs/data/
```

## Database Schema

### Tables

- `producers` - Winemaker info (note: table name stays "producers")
- `wines` - Wine products
- `grape_varieties` - Variety master data
- `wine_grapes` - Junction table (wine_id, grape_variety_id)
- `grape_aliases` - Alternative variety names
- `producer_social_media` - Social media links
- `producer_activities` - Activity types
- `producers_fts` - Full-text search for producers
- `wines_fts` - Full-text search for wines
- `schema_info` - Version tracking

### Full-Text Search

Full-text search uses SQLite FTS5:

```typescript
// Search winegrowers (business_name, permit_holder, wine_label, city)
const results = db.searchWinemakers('organic vineyard');

// Search wines (name, description, winemaking)
const wines = db.searchWines('ice wine');

// Search varieties (simple LIKE search)
const varieties = db.searchVarieties('pinot');
```

## Troubleshooting

### Database not found error

```
Error: Database not found: /path/to/grapegeek.db
```

**Solution:** Copy database file to Next.js project:

```bash
cp data/grapegeek.db grapegeek-nextjs/data/
```

### Schema version mismatch

**Solution:** Rebuild database:

```bash
uv run src/09_build_database.py
cp data/grapegeek.db grapegeek-nextjs/data/
```

### Test failures

**Solution:** Ensure database is present and up to date:

```bash
# Rebuild if needed
uv run src/09_build_database.py

# Copy to test location
cp data/grapegeek.db grapegeek-nextjs/data/

# Run tests
npm test
```

### SQLite column doesn't exist errors

The database schema may be missing enrichment data (species, wines, etc.). Some fields are optional and populated later by enrichment scripts.

## Next Steps

1. Create variety detail pages (`app/variety/[name]/page.tsx`)
2. Create winegrower detail pages (`app/winegrower/[id]/page.tsx`)
3. Build interactive map page (`app/map/page.tsx`)
4. Create search/index pages
5. Add statistics page

## References

- Python implementation: `/Users/phil/perso/grapegeek/src/includes/database.py`
- Database builder: `/Users/phil/perso/grapegeek/src/09_build_database.py`
- better-sqlite3 docs: https://github.com/WiseLibs/better-sqlite3
