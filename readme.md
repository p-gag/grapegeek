# Grape Geek

Welcome to **Grape Geek**! 🍇

This repository contains the source code and content generation system for the [Grape Geek project](https://www.grapegeek.com).

## Quick Start

### Content Generation
```bash
# Generate a technical article for a grape variety
python variety/generate.py grape <variety_name> --type technical

# Generate winemaking stories for a grape variety  
python variety/generate.py grape <variety_name> --type story

# Research grape varieties in a region
python variety/generate.py region <region_name>

# Dry run (show prompts without calling OpenAI)
python variety/generate.py grape <variety_name> --dry-run
python variety/generate.py region <region_name> --dry-run
```

### Wine Producer Data Pipeline
```bash
# Run complete producer data pipeline (RACJ → enrichment → map)
python producer/pipeline.py --full

# Individual steps
python producer/fetch_producers.py    # Fetch RACJ data
python producer/enrich_data.py        # AI enrichment
python producer/generate_map.py       # Generate GeoJSON map
```

### Data Normalization
```bash
# Normalize grape variety names
python normalization/normalize.py --grapes

# Run all normalization processes
python normalization/normalize.py --all
```

### Site Management
```bash
# Test site locally
uv run mkdocs serve

# Sync French translations
uv run python sync_french.py

# Manual site build (GitHub Actions handles deployment automatically)
uv run mkdocs build
```

### Setup
```bash
# Install dependencies using uv (preferred)
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY
```

## Project Structure

### 📁 **producer/** - Wine Producer Data Pipeline
- RACJ data fetching, AI enrichment, GeoJSON map generation

### 📁 **variety/** - Grape Variety Content
- Article generation, region research, content creation

### 📁 **normalization/** - Data Normalization  
- Grape variety and wine type standardization

### 📁 **utils/** - Site Management + Internationalization
- French translation, index updates, site building

### 📁 **shared/** - Common utilities
- Shared functionality and development tools

## Documentation

- **`CLAUDE.md`** - Developer guidance for Claude Code
- **`README_NEW_STRUCTURE.md`** - Detailed structure documentation
- See `docs/` for user-facing documentation

## Contributing

This is a personal project focused on hybrid grapes in cold climates. See `docs/en/about.md` for the project philosophy and approach.
