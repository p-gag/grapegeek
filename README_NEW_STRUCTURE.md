# New Project Structure - GrapeGeek

## Thematic Organization

### 📁 **producer/** - Wine Producer Data Pipeline
- **`fetch_producers.py`** - RACJ data fetching (was quebec_wine_producers.py)
- **`enrich_data.py`** - AI enrichment (was enrich_wine_producers.py) 
- **`generate_map.py`** - GeoJSON creation (was create_wine_map_data.py)
- **`pipeline.py`** - Full pipeline orchestration script ⭐ NEW

### 📁 **variety/** - Grape Variety Content
- **`generate.py`** - Main CLI (was main.py)
- **`articles.py`** - Article generation (was src/grapegeek/grape_article_generator.py)
- **`research.py`** - Region research (was src/grapegeek/region_researcher.py)

### 📁 **normalization/** - Data Normalization
- **`grape_varieties.py`** - Grape normalization (was normalize_grape_varieties.py)
- **`normalize.py`** - Orchestration script ⭐ NEW

### 📁 **utils/** - Site Management + Internationalization
- **`sync_french.py`** - Main translation sync (was sync_french.py)
- **`translate.py`** - Translation utilities (was french_generator.py)
- **`update_indexes.py`** - Index generation (was update_varieties_index.py)
- **`build.py`** - Site build orchestration ⭐ NEW

### 📁 **shared/** - Common utilities
- **`base.py`** - Base functionality (was src/grapegeek/base.py)
- **`test_api.py`** - API testing (was test_web_search.py)
- **`validate_setup.py`** - Validation (was validate_prompts.py)

## Usage Examples

```bash
# Producer data pipeline
python producer/pipeline.py --full

# Variety content generation  
python variety/generate.py grape frontenac --type technical

# Data normalization
python normalization/normalize.py --grapes

# Site management
python utils/build.py --all
```

## Key Changes
- ✅ **Thematic grouping** by domain function
- ✅ **Orchestration scripts** for complex workflows  
- ✅ **Flattened structure** - no more deep src/ hierarchy
- ✅ **Clear naming** - descriptive file names
- ✅ **Functional focus** - preparing for non-OOP refactor

## Migration Status
- ✅ Files moved to new structure
- ✅ Import paths updated
- ✅ Orchestration scripts created
- ⏳ Ready for functional refactoring