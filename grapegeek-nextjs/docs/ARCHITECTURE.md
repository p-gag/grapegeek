# GrapeGeek Next.js Architecture Guide

This document outlines the core architectural decisions, patterns, and guidelines for the GrapeGeek Next.js application.

---

## Core Principles

### Static Site Generation (SSG)
- **All pages pre-rendered at build time** - No runtime database queries
- Database accessed only during `next build`
- Results in static HTML files for GitHub Pages deployment
- Zero server-side runtime requirements

### Terminology Standards
- **User-facing:** Always use "winegrower" (never "producer")
- **Database schema:** Tables still named "producers" (no schema changes)
- **TypeScript:** Use `Winegrower` interface
- **URLs:** `/winegrowers/[slug]` routes
- **Components:** Named `Winegrower*` (e.g., `WinegrowerCard`, `WinegrowerHeader`)

---

## Database Integration

### Database Factory
```typescript
const db = getDatabase();  // Creates database instance
```

### Lazy Loading for Performance
```typescript
// Fast - basic info only
const winegrower = db.getWinegrower('slug', false);

// Slower - includes wines, social media, activities
const winegrower = db.getWinegrower('slug', true);
```

### Build-Time Only Access
- Database queries execute during `next build`
- No API routes needed for SSG
- All data embedded in static HTML
- Database file lives in `data/grapegeek.db` (NOT committed to git)

### Build-Time Data Pipelines
Map and tree data are queried directly from the database at build time via `force-static` API routes — no intermediate files.

**Map** (`/api/map-data`):
- `db.getMapMarkers()` → markers with varieties/wine_types per winegrower
- `db.getIndexedRegions()` → region overlay data
- Consumed by: `map/page.tsx`, `MapPreviewLeaflet.tsx`

**Family tree** (`/api/tree-data`):
- `db.getTreeData()` → nodes (variety metadata) + edges (parent→child via VIVC number joins)
- Consumed by: `hooks/useTreeData.ts` → `TreePageContent.tsx`

### Full-Text Search
- Uses SQLite FTS5 for search functionality
- Available methods:
  - `searchWinegrowers(query)` - Full-text search
  - `searchWines(query)` - Full-text search
  - `searchVarieties(query)` - LIKE search

---

## Page Generation Pattern

### Dynamic Routes with SSG
```typescript
// 1. Generate all possible paths at build time
export async function generateStaticParams() {
  const db = getDatabase();
  return db.getAllVarietyNames().map(name => ({
    name: encodeURIComponent(name)
  }));
}

// 2. Generate SEO metadata per page
export async function generateMetadata({ params }) {
  const db = getDatabase();
  const variety = db.getVariety(params.name);
  return {
    title: `${variety.name} - Grape Variety | GrapeGeek`,
    description: `${variety.name} is a ${variety.species} grape variety...`
  };
}

// 3. Render page with data
export default function Page({ params }) {
  const db = getDatabase();
  const variety = db.getVariety(params.name, true);
  return <div>{/* Render variety data */}</div>;
}
```

### 404 Handling
- Create `not-found.tsx` alongside dynamic routes
- Provide friendly error pages with navigation back
- Maintain consistent theming

---

## Component Architecture

### Server vs Client Components

**Server Components (Default):**
- All pages and most components
- Database access allowed
- No client-side JavaScript
- Better performance and SEO

**Client Components (`'use client'`):**
- Maps (React Leaflet)
- Interactive charts
- Forms and user input
- Browser APIs usage

### Component Organization
```
components/
├── home/           # Homepage-specific components
├── variety/        # Variety page components
├── winegrower/      # Winemaker page components
├── map/            # Map page components
├── stats/          # Statistics page components
└── Header.tsx      # Shared navigation
```

### Reusable Component Pattern
```typescript
interface CardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  href?: string;
}

export function Card({ title, description, icon, href }: CardProps) {
  // Implementation with TypeScript types
}
```

---

## TypeScript Standards

### Strict Typing
- No `any` usage
- All interfaces defined in `lib/types.ts`
- Props fully typed
- Database return types explicit

### Key Interfaces
See `lib/types.ts` for complete definitions. Core types:
- `Winegrower` - Producer with optional wines/social/activities
- `GrapeVariety` - Variety with VIVC data, aliases, usage
- `Wine` - Wine with grape composition
- `MapMarker` - Geolocation data

### Optional Fields
- Use `?` for fields that may not exist
- Handle gracefully in components
- Provide empty states when data is missing

---

## Styling Guidelines

### Tailwind CSS
- Mobile-first responsive design
- Utility classes only (no custom CSS)
- Consistent color scheme:
  - Primary: Purple (purple-600, purple-700)
  - Secondary: Blue
  - Accent: Green
  - Background: Gray-50
  - Cards: White with shadow

### Responsive Patterns
```typescript
// Mobile: 1 column, Tablet: 2 columns, Desktop: 3 columns
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

### Hover Effects
- Scale icons: `hover:scale-110 transition-transform`
- Color changes: `hover:text-purple-600`
- Shadows: `hover:shadow-lg transition-shadow`

---

## Data Loading Patterns

### Empty State Handling
```typescript
// Always provide empty states
{winegrower.wines?.length ? (
  <WineList wines={winegrower.wines} />
) : (
  <EmptyState message="No wines cataloged for this winegrower" />
)}
```

### Conditional Rendering
```typescript
// Check for optional data before rendering
{variety.vivc_number && (
  <a href={`https://www.vivc.de/index.php?r=passport/view&id=${variety.vivc_number}`}>
    VIVC #{variety.vivc_number}
  </a>
)}
```

### Relationship Loading
- Load relationships only when needed
- Use `includeRelationships` parameter
- Balance performance vs completeness

---

## Testing Standards

### Unit Tests with Jest
```bash
# Run tests
npm test

# Watch mode
npm run test:watch
```

### Test Coverage Required
- Database query methods
- Component rendering
- Data loading with relationships
- Error handling (404s, missing data)
- Metadata generation

### Test Organization
```
__tests__/
├── database.test.ts      # Database integration tests
└── homepage.test.ts      # Component tests

app/varieties/[name]/__tests__/
└── page.test.tsx         # Page-specific tests
```

---

## Performance Guidelines

### Build Performance
- Pre-render all static paths at build time
- Use `generateStaticParams()` for dynamic routes
- Keep relationship loading selective

### Runtime Performance
- Zero database queries at runtime
- Minimal client-side JavaScript
- Pre-rendered HTML for instant loads
- Images must use `unoptimized: true` for static export

### Expected Metrics
- Time to First Byte: <50ms
- First Contentful Paint: <200ms
- Lighthouse Score: 95-100

---

## SEO Best Practices

### Metadata per Page
- Unique `title` and `description` for each page
- Use `generateMetadata()` function
- Include relevant keywords naturally
- Keep titles under 60 characters
- Keep descriptions under 160 characters

### URL Structure
- Clean, readable URLs
- Use slugs for names (encoded)
- Consistent patterns: `/varieties/[name]`, `/winegrower/[id]`

---

## File Organization

### Critical Paths
```
grapegeek-nextjs/
├── app/                    # Next.js App Router pages
├── components/             # React components (organized by feature)
├── lib/
│   ├── database.ts        # Database singleton and queries
│   ├── types.ts           # TypeScript interfaces
│   └── utils.ts           # Helper functions
├── data/
│   └── grapegeek.db       # SQLite database (NOT in git)
├── public/                 # Static assets
└── __tests__/             # Test suites
```

### What NOT to Commit
- `node_modules/`
- `.next/`
- `out/`
- `*.db` (database files)
- `.DS_Store`
- `*.tsbuildinfo`

---

## Build & Deployment

### Local Development
```bash
npm run dev              # Development server (http://localhost:3000)
```

### Production Build
```bash
npm run build           # Build static site to ./out/
npx serve out           # Preview production build
```

### Database Preparation
```bash
# Database must be built first
cd ..
uv run src/09_build_database.py

# Copy to Next.js project
cp data/grapegeek.db grapegeek-nextjs/data/
```

### Build Order
1. Build database (Python pipeline)
2. Copy database to `grapegeek-nextjs/data/`
3. Run `npm run build`
4. Deploy `out/` directory

---

## Common Patterns

### Link to Variety Pages
```typescript
<Link href={`/varieties/${encodeURIComponent(varietyName)}`}>
  {varietyName}
</Link>
```

### Link to Winegrower Pages
```typescript
<Link href={`/winegrowers/${slug}`}>
  {businessName}
</Link>
```

### External Links
```typescript
<a
  href={url}
  target="_blank"
  rel="noopener noreferrer"
  className="inline-flex items-center gap-1"
>
  Visit Website
  <ExternalLink className="h-4 w-4" />
</a>
```

### Number Formatting
```typescript
// Use locale string for large numbers
{winegrowerCount.toLocaleString()} Winemakers
```

---

## Error Handling

### Missing Data
- Provide empty states
- Show helpful messages
- Offer navigation to other pages

### Invalid Routes
- Create `not-found.tsx` for 404s
- Maintain consistent styling
- Provide links back to main sections

### Database Errors
- Validate schema version on connection
- Log errors clearly
- Fail fast during build (don't deploy broken data)

---

## Future Considerations

### Data Pipeline Integration
- Database must be rebuilt before Next.js build
- Consider automation in CI/CD
- Handle schema migrations gracefully

### Content Updates
- Rebuild site when database changes
- No hot reloading of data (static site)
- Plan for incremental builds if needed

### Scaling
- Monitor build times as data grows
- Consider pagination for large lists
- Optimize relationship loading
