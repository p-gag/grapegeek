# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Running the Application
```bash
# Generate a technical article for a grape variety
python main.py grape <variety_name> --type technical

# Generate and auto-publish a technical article to MkDocs site
python main.py grape <variety_name> --type technical --publish

# Generate winemaking stories for a grape variety  
python main.py grape <variety_name> --type story

# Sync all content to French site with smart change detection (varieties + main site files)
python sync_french.py

# Dry run (show prompts without calling OpenAI)
python main.py grape <variety_name> --dry-run
python main.py region <region_name> --dry-run
```

### Wine Producer Pipeline
```bash
# 1. Fetch and unify Quebec + US producer data
python src/01_producer_fetch.py

# 2. Add geolocation data (optional - can run independently)
python src/03_producer_geolocate.py

# 3. Unified research: classify + search + enrich with early exits (saves 80% cost)
python src/12_unified_producer_research.py --limit 10  # Test with limit
python src/12_unified_producer_research.py --yes      # Full run

# 4. Normalize grape varieties (run as needed when new varieties found)
python src/08_variety_normalize.py

# 5. Apply normalizations to create final dataset
python src/09_data_normalize_final.py

# 6. Generate map data and statistics
python src/10_output_geojson.py
python src/11_generate_stats.py --varieties  # Include variety list

# ⚠️  WARNING: Never change GPT models without explicit approval
```

### VIVC Photo Pipeline
Downloads grape variety photos from VIVC with proper credit attribution and uploads to Google Cloud Storage.

```bash
# Analyze credit distribution
python analyze_photo_credit_distribution.py

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

### MkDocs Site Management (Legacy)
```bash
# Install MkDocs dependencies
pip install mkdocs-material mkdocs-git-revision-date-localized-plugin

# Test site locally (simple MkDocs only - no React app)
mkdocs serve

# Manual site build (GitHub Actions handles deployment automatically)
mkdocs build
```

### Local Testing Workflow (MkDocs + React Integration)
The complete local testing workflow simulates the production GitHub Pages deployment structure:

```bash
# 1. Generate tree data for React app (if needed)
uv run src/18_generate_tree_data.py

# 1b. Generate map data for React app (if needed)
uv run src/19_generate_map_data.py

# 2. Build React family trees app
cd grape-tree-react
npm run build    # This copies tree data and builds to ../docs/family-trees/
cd ..

# 3. Build MkDocs site
mkdocs build     # Builds to site/ directory

# 4. Copy React app to MkDocs build output
cp -r docs/family-trees site/

# 5. Start local test server (simulates GitHub Pages structure)
python test-server.py

# Server will be available at:
# - Main site: http://localhost:8000 (MkDocs homepage)
# - Family trees: http://localhost:8000/family-trees/ (React app)
```

**Quick rebuild workflow** (when making React changes):
```bash
cd grape-tree-react && npm run build && cd .. && cp -r docs/family-trees site/
```

**Test server features:**
- Serves built MkDocs site (not markdown files) at root
- Family trees React app at `/family-trees/` sub-path
- Simulates exact production GitHub Pages deployment structure
- SPA routing support for React app
- Proper MIME types and static asset serving

### React Family Trees Integration ✅ COMPLETE
The family tree functionality has been **fully integrated** into the main `grape-explorer-react` application following the map integration pattern.

#### Main Application (grape-explorer-react/)
```bash
# Integrated React app with tree functionality
cd grape-explorer-react
npm run dev     # Runs on http://localhost:3000 or 3001 (auto-detects port)

# Tree dependencies are installed:
# - reactflow @reactflow/controls @reactflow/background
# - flag-icons CSS library for country flags
```

#### ✅ Completed Integration Features
- **✅ TreePreviewReactFlow**: Static preview on variety pages showing immediate family (parents/children)
- **✅ TreePage**: Full interactive tree with left sidebar layout matching MapPage exactly
- **✅ GrapeNode**: Custom React Flow node component with preserved original styling
- **✅ NodePopup**: Click-to-show popup with detailed variety information
- **✅ Route Integration**: `/tree?variety=Name` and `/variety/:slug/tree` routes
- **✅ Navigation**: Proper back button handling to return to variety pages
- **✅ Mobile Responsive**: Sidebar layout adapts to mobile (stacked layout)
- **✅ Original Functionality Preserved**: Species coloring, duplicate parents mode, hover effects

#### Legacy Reference (grape-tree-react/ - For Reference Only)
```bash
# Original standalone React app (kept for reference)
cd grape-tree-react
npm install && npm run dev     # Runs on http://localhost:5173
```
**Note**: The standalone app is no longer actively used but kept for reference.

#### Data Generation (Current)
```bash
# Generate tree data for integrated system
python src/18_generate_tree_data.py

# Data is used by:
# - grape-explorer-react/public/data/tree-data.json (main integration)
# - grape-tree-react/src/data/tree-data.json (legacy reference)
```

#### Key Integrated Components
- `grape-explorer-react/src/pages/TreePage.jsx`: Full tree page with 240px sidebar
- `grape-explorer-react/src/components/TreePreviewReactFlow.jsx`: Tree preview component  
- `grape-explorer-react/src/components/GrapeNode.jsx`: React Flow node with original styling
- `grape-explorer-react/src/components/NodePopup.jsx`: Detailed variety information popup
- `grape-explorer-react/public/data/tree-data.json`: Tree data source

### Troubleshooting Local Testing

**Common issues and solutions:**

1. **"Address already in use" error:**
   ```bash
   lsof -ti:8000 | xargs kill -9  # Kill processes on port 8000
   ```

2. **Family tree shows empty graphs:**
   - Check if tree data exists: `ls grape-tree-react/src/data/tree-data.json`
   - Regenerate data: `uv run src/18_generate_tree_data.py`
   - Rebuild React app: `cd grape-tree-react && npm run build`

3. **React app not updating after changes:**
   - Rebuild and copy: `cd grape-tree-react && npm run build && cd .. && cp -r docs/family-trees site/`

4. **MkDocs site showing directory listing:**
   - Ensure MkDocs is built: `mkdocs build`
   - Check test server is serving from `site/` not `docs/`

5. **Missing dependencies:**
   ```bash
   # React dependencies
   cd grape-tree-react && npm install
   
   # Python dependencies  
   uv sync
   
   # MkDocs dependencies
   pip install mkdocs-material mkdocs-git-revision-date-localized-plugin
   ```

### Dependencies
```bash
# Install dependencies using uv (preferred)
uv sync

# Or install with pip
pip install -e .
```

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

## Project Architecture

### Core Structure
This is an AI-powered content generation system for creating magazine-style articles about cold-climate grape varieties, focused on hybrid grapes in northeastern US and eastern Canada.

**Main Components:**
- `main.py`: CLI entry point with subcommands for grape articles and region research
- `src/grapegeek/base.py`: BaseGenerator class with shared OpenAI integration and file handling
- `src/grapegeek/grape_article_generator.py`: GrapeArticleGenerator for variety-specific content
- `src/grapegeek/region_researcher.py`: RegionResearcher for regional variety discovery

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
2. **Sync French content**: Run `python sync_french.py` to translate changed content to French site
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