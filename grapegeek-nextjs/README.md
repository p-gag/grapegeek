# GrapeGeek Next.js Application

Next.js SSG application for GrapeGeek - pre-rendered static site for better SEO and performance.

**Replaces:**
- `docs/` - MkDocs site (legacy)

## Architecture

- **Framework:** Next.js 14+ with App Router
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Database:** SQLite (build-time only, via better-sqlite3)
- **Maps:** React Leaflet
- **Charts:** Recharts
- **Deployment:** Static export to GitHub Pages

## Project Structure

```
grapegeek-nextjs/
├── app/                      # Next.js App Router pages
│   ├── layout.tsx           # Root layout with Header/Footer
│   ├── page.tsx             # Homepage
│   ├── varieties/           # Grape varieties pages
│   │   ├── page.tsx        # Varieties index
│   │   └── [name]/         # Dynamic variety pages (SSG)
│   │       └── page.tsx
│   ├── winegrowers/         # Winegrower pages
│   │   ├── page.tsx        # Winegrowers index
│   │   └── [slug]/         # Dynamic winegrower pages (SSG)
│   │       └── page.tsx
│   ├── map/                 # Interactive map
│   │   └── page.tsx
│   ├── stats/               # Statistics & analytics
│   │   └── page.tsx
│   ├── tree/                # Family tree viewer
│   │   └── page.tsx
│   └── about/               # About page
│       └── page.tsx
├── components/              # React components (organized by feature)
│   ├── home/               # Homepage components
│   ├── variety/            # Variety page components
│   ├── winegrower/         # Winegrower page components
│   ├── map/                # Map components
│   ├── stats/              # Statistics components
│   ├── tree/               # Family tree components
│   └── Header.tsx          # Site navigation
├── lib/                     # Utility libraries
│   ├── types.ts            # TypeScript interfaces
│   ├── utils.ts            # Helper functions
│   └── database.ts         # SQLite access (Task #4)
├── data/                    # Database location (build-time)
│   └── .gitkeep
├── public/                  # Static assets
├── next.config.js          # Next.js configuration (static export)
├── tailwind.config.ts      # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- SQLite database built from parent directory

### Installation

```bash
# Install dependencies
npm install

# Copy database from parent directory (after running Task #1)
mkdir -p data
cp ../data/grapegeek.db data/
```

### Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000
```

### Building for Production

```bash
# Build static site
npm run build

# Output will be in ./out/ directory
```

### Preview Production Build

```bash
# After building
npx serve out
```

## Configuration

### Static Export

The `next.config.js` is configured for static export:

```javascript
output: 'export',
images: {
  unoptimized: true, // Required for static export
}
```

### Database Integration

The database integration layer (`lib/database.ts`) will be added in Task #4. It uses `better-sqlite3` to query the SQLite database **during the build process** to generate static pages.

## Key Features

### Static Site Generation (SSG)

- All variety and producer pages are pre-rendered at build time
- Uses `generateStaticParams()` to create paths from database
- Optimal SEO with meta tags and structured data
- Fast page loads with pre-rendered HTML

### TypeScript Interfaces

All data structures are strongly typed in `lib/types.ts`:
- `Producer` - Wine producer information
- `Wine` - Wine details with varieties
- `GrapeVariety` - Grape variety with VIVC data
- `MapMarker` - Geolocation data for maps

### Responsive Design

- Mobile-first approach with Tailwind CSS
- Responsive navigation and layouts
- Touch-friendly interactive elements

## Development Workflow

1. **Update Data:** Run Python pipeline to update JSONL files
2. **Build Database:** `uv run src/09_build_database.py` (Task #1)
3. **Copy Database:** Copy `grapegeek.db` to `data/` directory
4. **Build Site:** `npm run build`
5. **Deploy:** Push to GitHub (Actions handles deployment)

## Implementation Status

**Completed:**
- ✅ Database integration (`lib/database.ts`)
- ✅ Variety pages (600 varieties, SSG)
- ✅ Winegrower pages (1,491 winegrowers, SSG)
- ✅ Interactive map with region overlays
- ✅ Varieties index with filters
- ✅ Winegrowers index with filters
- ✅ Homepage with live statistics
- ✅ Stats/analytics page with charts
- ✅ Family tree viewer (React Flow)

**Pending:**
- ⏳ SEO optimization (sitemap generation)
- ⏳ Build script integration
- ⏳ GitHub Actions deployment

## Dependencies

### Core
- `next` - Next.js framework
- `react` / `react-dom` - React library
- `typescript` - TypeScript compiler

### Database
- `better-sqlite3` - SQLite database access (build-time only)

### UI
- `tailwindcss` - Utility-first CSS framework
- `lucide-react` - Icon library

### Maps & Charts
- `react-leaflet` / `leaflet` - Interactive maps
- `recharts` - Data visualization

### Utilities
- `gray-matter` - Markdown frontmatter parsing
- `date-fns` - Date formatting

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript](https://www.typescriptlang.org/docs)
- [Better SQLite3](https://github.com/WiseLibs/better-sqlite3)

## Notes

- Database is **NOT committed to git** - it's generated at build time
- All images must be in `public/` directory and use `unoptimized: true`
- Static export means no server-side runtime or API routes
- Client components (maps, charts) must be marked with `'use client'`
