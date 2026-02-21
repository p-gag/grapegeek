# Quick Start

## Setup

```bash
npm install
cp ../data/grapegeek.db data/
npm run dev  # http://localhost:3000
```

## Build

```bash
npm run build    # → out/
npx serve out    # Preview
```

## Commands

```bash
npm test         # Tests
npm run lint     # Linting
npx tsc --noEmit # Type check
```

## Troubleshooting

**Build fails:**
```bash
cd .. && uv run src/09_build_database.py && cp data/grapegeek.db grapegeek-nextjs/data/
rm -rf .next && npm run build
```

## Documentation

- **Architecture:** `docs/ARCHITECTURE.md` - Patterns, guidelines, examples
- **Project Info:** `README.md` - Setup and structure
- **Agent Guide:** `CLAUDE.md` - AI-specific guidance
