# CLAUDE.md

AI agent guidance for grapegeek-nextjs/.

## Project

Next.js 14 SSG for GrapeGeek - cold-climate grapes and winegrowers.

**Routes:**
- `/` - Homepage with stats
- `/varieties` - Browse 600+ varieties
- `/varieties/[name]` - Variety details (SSG)
- `/winegrowers` - Browse 1,491 winegrowers
- `/winegrowers/[slug]` - Winegrower details (SSG)
- `/map` - Interactive map with overlays
- `/stats` - Statistics and charts
- `/tree` - Family tree viewer
- `/about` - About page

## Documentation

- **`docs/ARCHITECTURE.md`** - Patterns, standards, guidelines ⭐
- **`README.md`** - Setup and project structure
- **`QUICKSTART.md`** - Essential commands

## Navigation

```
lib/database.ts     - Database singleton, all queries
lib/types.ts        - TypeScript interfaces
app/*/page.tsx      - Page routes
components/*/       - Components by feature
```

## Core Principles

1. **Static Site Generation** - Build-time DB queries only, zero runtime queries
2. **Terminology** - Always "winegrower" (never "producer")
3. **Conciseness** - Minimum words, maximum meaning (see below)
4. **Type Safety** - Strict TypeScript, no `any`

## Documentation Standards

### Value Conciseness

**Use minimum words. Remove redundancy.**

### Don't Repeat Yourself (DRY)

**Every piece of information should exist in exactly one place.**

- One concept → One location → Link to it
- Don't duplicate information across files
- Don't repeat information in different sections
- Link to canonical source instead

Example:
- ✅ CLAUDE.md links to ARCHITECTURE.md
- ❌ CLAUDE.md repeats patterns from ARCHITECTURE.md

When information exists elsewhere, link to it:
- ✅ "See `docs/ARCHITECTURE.md#database-integration`"
- ❌ Copy-paste the database integration section

### Keep Docs Updated

When changing code:
1. Update relevant section in `docs/ARCHITECTURE.md`
2. Delete outdated content immediately
3. Remove duplicates if information repeated

## Quick Commands

```bash
npm run dev     # Dev server
npm run build   # Static export
npm test        # Run tests
```

**Database prep (required):**
```bash
cd .. && uv run src/09_build_database.py && cp data/grapegeek.db grapegeek-nextjs/data/
```

See `docs/ARCHITECTURE.md` for patterns and examples.
