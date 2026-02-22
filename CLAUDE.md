# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Running the Application
```bash
# Generate a technical article for a grape variety
uv run main.py grape <variety_name> --type technical

# Generate winemaking stories for a grape variety
uv run main.py grape <variety_name> --type story

# Dry run (show prompts without calling OpenAI)
uv run main.py grape <variety_name> --dry-run
uv run main.py region <region_name> --dry-run
```

### Wine Producer Pipeline

See **`src/README.md`** for the full pipeline with commands, data flow diagram, and testing instructions.

⚠️ Never change GPT models without explicit approval.

### VIVC Photo Pipeline
Downloads grape variety photos from VIVC with proper credit attribution and uploads to Google Cloud Storage.

```bash
# Analyze credit distribution
uv run analyze_photo_credit_distribution.py

# Sync photos to GCS
uv run src/08a_photo_sync_gcs.py --force
uv run src/08a_photo_sync_gcs.py --vivc 17638  # Specific variety
```

**Features:**
- Extracts credits from JavaScript-loaded foto2 modals
- Verifies against whitelist (6 JKI/VIVC formats + Tom Plocher)
- Cache-aware, incremental saving, progressive delays
- ⚠️ **Visible warnings** for unknown external sources

**📖 See [PHOTO_CREDITS_NOTES.md](photos_to_clean/docs/PHOTO_CREDITS_NOTES.md) for technical details, credit formats, and troubleshooting.**

### Next.js Site Development (New)
```bash
# Development server
cd grapegeek-nextjs
npm run dev              # Start dev server at http://localhost:3000

# Production build
npm run build            # Build static site to ./out/
npx serve out            # Preview production build

# Verification
./verify-setup.sh        # Run all setup verification checks

# Prerequisites: Database must be built first
cd ..
uv run src/09_build_database.py
cp data/grapegeek.db grapegeek-nextjs/data/
```

### Dependencies
```bash
uv sync  # Install dependencies
```

Always use `uv run <script>` to execute Python scripts. Never use `python` directly.

### Environment Setup
- Requires `OPENAI_API_KEY` environment variable (uses OpenAI Responses API with web_search tools)
- Uses `.env` file for environment variables

## Documentation Standards

### Value Conciseness

**Use minimum words. Remove redundancy.**

### Don't Repeat Yourself (DRY)

**Every piece of information should exist in exactly one place.**

- One concept → One location → Link to it
- Don't duplicate information across files
- Don't repeat information in different sections
- Link to canonical source instead

When information exists elsewhere, link to it:
- ✅ "See `src/PHOTO_PIPELINE_USAGE.md`"
- ❌ Copy-paste the pipeline section

### Keep Docs Updated

When changing code:
1. Update the relevant section in CLAUDE.md or the linked doc
2. Delete outdated content immediately
3. Remove duplicates if information is repeated

### Root Directory Policy

Root contains named entry points only (`main.py`, `sync_french.py`). All other scripts go in `src/`. Tests go in `tests/` using pytest — no ad-hoc test scripts at root.

## Project Architecture

### Core Structure
This is an AI-powered content generation system for creating magazine-style articles about cold-climate grape varieties, focused on hybrid grapes in northeastern US and eastern Canada.

**Main Components:**
- `main.py`: CLI entry point with subcommands for grape articles and region research
- `src/grapegeek/base.py`: BaseGenerator class with shared OpenAI integration and file handling
- `src/grapegeek/grape_article_generator.py`: GrapeArticleGenerator for variety-specific content
- `src/grapegeek/region_researcher.py`: RegionResearcher for regional variety discovery
- `src/includes/database.py`: Type-safe SQLite access layer (Producer, GrapeVariety, Wine dataclasses + FTS) — see `src/DATABASE.md`
- `src/09_build_database.py`: Builds `data/grapegeek.db` from JSONL sources (required for Next.js)

### Prompt System Architecture
The application uses a layered prompt system:

1. **General Prompts** (`prompts/general/`): System-wide instructions for tone, citation style
2. **Content-Type Prompts** (`prompts/grapes/`): 
   - `technical_prompt.md`: Comprehensive technical analysis template
   - `art_prompt.md`: Winemaking story and narrative template
3. **Entity Context** (`prompts/grapes/articles/`, `prompts/regions/`): 
   - YAML frontmatter files with variety/region-specific context
   - Prevents AI confusion by providing precise identification context

### OpenAI Integration
- Uses OpenAI Responses API with `gpt-5` model
- Includes `web_search` tool for real-time research and citation gathering
- All API calls go through `BaseGenerator.call_openai()` method
- Dry run mode shows full prompt structure and debug information without API calls

### Output Organization
- `output/articles/`: Generated English grape variety articles
  - Technical: `{variety_name}.md` 
  - Stories: `{variety_name}_winemaking_stories.md`
- `output/regions/`: Regional research results as `{region_name}_varieties.md`
- `output/fr/`: French translations of articles (generated by `french_generator.py`)
- `debug/`: Dry run outputs with `_debug.md` suffix

### Site Structure (MkDocs)
- `docs/`: English site content
  - `index.md`: English homepage
  - `about.md`: English about page  
  - `varieties/index.md`: English grape varieties section
  - `ai-usage.md`: AI transparency page
- `docs/fr/`: French site content
  - `index.md`: French homepage (Accueil)
  - `a-propos.md`: French about page (À propos)
  - `varietes/index.md`: French grape varieties section
  - `usage-ia.md`: AI transparency page (French)

### Photo Sync Pipeline
VIVC grape photos are synced to Google Cloud Storage for use on the website:
- **Script**: `src/08a_photo_sync_gcs.py` - Downloads photos from VIVC, uploads to GCS
- **When**: After VIVC consolidation, before database generation
- **Default behavior**: Only processes varieties without photos (safe, resumable)
- **Rate limiting**: 3 seconds between VIVC requests (respectful, configurable)
- **Storage**: `gs://grapegeek-data/photos/varieties/vivc/`
- **Usage guide**: See `src/PHOTO_PIPELINE_USAGE.md` for complete documentation
- **GCS setup**: See `infrastructure/GCP.md`

```bash
# Default: Process varieties missing photos with "Cluster in the field" photos
uv run src/08a_photo_sync_gcs.py

# Force reprocess all varieties (including those with photos)
uv run src/08a_photo_sync_gcs.py --force

# Override to download multiple photo types
uv run src/08a_photo_sync_gcs.py --photo-types "Cluster in the field,Mature leaf"
```

### Variety Context System
Each grape variety can have a context file at `prompts/grapes/articles/{variety_name}.md` with YAML frontmatter:
```yaml
---
name: "Official Variety Name"
prompt: "Minimal context to avoid confusion with similarly named varieties"
---
```

### Region Context System  
Each region can have a context file at `prompts/regions/{region_name}.md` with YAML frontmatter:
```yaml
---
name: "Region Name"
summary: "Brief regional description"
known_varieties: "List of known varieties"
trade_association: "Association name"
trade_association_url: "URL"
---
```

### French Translation System
- `sync_french.py`: Unified French synchronization script with hash-based change detection
- Uses OpenAI Responses API with `gpt-5` model and Quebec French context
- Only translates files that have changed since last sync (tracked via YAML frontmatter hashes)
- Preserves technical terms, citations, and markdown formatting
- **Identical directory structure**: All files maintain the same names and paths (`docs/en/about.md` → `docs/fr/about.md`)
- Auto-discovers all markdown files in main docs directory
- Unified sync method for both variety articles and main site content
- Automatic YAML frontmatter management for change tracking

## Development Notes

### Content Publishing Workflow
1. **Generate and publish**: Use `main.py grape <variety> --type technical --publish` to auto-generate and publish to MkDocs site
2. **Sync French content**: Run `uv run sync_french.py` to translate changed content to French site
3. **Deploy**: Commit changes → GitHub Actions automatically builds and deploys MkDocs site

**Auto-publish features:**
- Technical articles automatically copied to `docs/varieties/` with proper YAML frontmatter
- Varieties index page automatically updated with new entries
- Only technical articles auto-publish; stories remain manual workflow

### Site Deployment
- **Live site**: https://grapegeek.com (custom domain) and https://p-gag.github.io/grapegeek/
- **Auto-deployment**: GitHub Actions workflow builds MkDocs on every push to main branch
- **Bilingual navigation**: Material theme with language selector in top bar
- **Local testing**: Use `mkdocs serve` to preview changes before publishing

### File Handling Patterns
- All file operations use `pathlib.Path` 
- YAML frontmatter parsing handles missing files gracefully with defaults
- Output directories are created automatically
- Generated files in `output/` and `debug/` are git-ignored

### Error Handling
- OpenAI API errors are caught and returned as error strings
- Missing prompt files return empty strings rather than failing
- Dry run mode provides comprehensive debugging without API calls

### Code Organization
- Shared functionality is in `BaseGenerator` base class
- Generator classes inherit common file operations and OpenAI integration
- CLI uses argparse with subcommands for different content types
- French translation is separate standalone script (simpler than base class inheritance)