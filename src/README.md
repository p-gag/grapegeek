# 🍇 Grape Research Pipeline

> Comprehensive pipeline for discovering, researching, and normalizing North American wine producer data with grape variety classification.

## 🔧 Environment Setup

See `.env.example` for required environment variables.

```bash
# Install dependencies
uv sync
```

## 📊 Pipeline Overview

```mermaid
graph TD
    %% Data Sources
    A1[Quebec RACJ API] 
    A2[US TTB CSV]
    A3[Canada Province Research]
    
    %% Step 0: Data Collection
    A3 --> B0[00_canada_province_winery_researcher.py]
    B0 --> D1[data/can/canada_province_wineries.jsonl]
    
    %% Step 1: Unify Sources  
    A1 --> B1[01_producer_fetch.py]
    A2 --> B1
    D1 --> B1
    B1 --> D2[data/01_unified_producers.jsonl]
    B1 --> D2M[data/01_unified_producers_metadata.json]
    
    %% Step 2: Research & Enrichment
    D2 --> B2[02_producer_research.py]
    B2 --> D3A[data/enriched_producers_cache.jsonl]
    B2 --> D3B[data/producer_geolocations_cache.jsonl]
    
    %% Step 3: Variety Processing (Manual Review Needed)
    D3A --> B3[03_variety_normalize.py]
    B3 --> D4[data/grape_variety_mapping.jsonl]
    D4 --> B4[04_vivc_assign.py]
    B4 --> D4
    D4 --> B4B[Portfolio Consolidation]
    B4B --> D4

    %% Step 4a: Photo Sync (NEW)
    D4 --> B4C[08a_photo_sync_gcs.py]
    B4C --> D4D[GCS Photos]
    B4C --> D4

    %% Step 4: Final Dataset
    D2 --> B5[05_data_final_normalized.py]
    D3A --> B5
    D3B --> B5  
    D4 --> B5
    B5 --> D7[data/05_wine_producers_final_normalized.jsonl]
    
    %% Step 5: Outputs
    D7 --> B7[07_generate_stats.py]
    B7 --> D10[dataset_statistics.txt]

    %% Step 6: Database Build (map data served directly from DB at build time)
    D7 --> B9[09_build_database.py]
    D4 --> B9
    B9 --> D11[data/grapegeek.db]

    %% Styling
    classDef script fill:#e1f5fe
    classDef datafile fill:#f3e5f5
    classDef manual fill:#fff3e0

    class B0,B1,B2,B3,B4,B4B,B4C,B5,B7,B9 script
    class D1,D2,D2M,D3A,D3B,D4,D4D,D7,D10,D11 datafile
    class B3,B4,B4B manual
```

## 🚀 Command Reference

### New Region Research (Full Pipeline)
```bash
# 0. Research Canadian provinces (current: NB, NL, NS, PE)
uv run src/00_canada_province_winery_researcher.py --province "NB,NL,NS,PE" --previous-list data/can/canada_province_wineries.jsonl --yes --threads 4

# 1. Unify all data sources  
uv run src/01_producer_fetch.py

# 2. Research & enrich producers
uv run src/02_producer_research.py --yes

# 3. Normalize varieties (MANUAL REVIEW NEEDED)
uv run src/03_variety_normalize.py --limit 20

# 4. Assign VIVC data
uv run src/04_vivc_assign.py --limit 10

# 5. Consolidate VIVC duplicates (CRITICAL)
uv run src/includes/grape_varieties.py consolidate
# TODO: "DIANA" (VIVC 3547) and "Diana" (VIVC 3550) survive as separate entries —
#       normalization should deduplicate same-name varieties differing only by case.

# 5a. Sync VIVC photos to GCS (NEW - optional but recommended)
# Default: only processes varieties without photos, "Cluster in the field" photos only
uv run src/08a_photo_sync_gcs.py

# 6. Generate final dataset
uv run src/05_data_final_normalized.py

# 7. Generate outputs
uv run src/07_generate_stats.py
uv run src/08_build_vivc_index.py

# 8. Build SQLite database (required for Next.js site, map data served directly from DB)
uv run src/09_build_database.py
cp data/grapegeek.db grapegeek-nextjs/data/
```

### Variety Updates Only
```bash
# When new varieties found - steps 3-6 only
uv run src/03_variety_normalize.py --limit 20  # Manual review needed
uv run src/04_vivc_assign.py
uv run src/includes/grape_varieties.py consolidate  # CRITICAL
uv run src/05_data_final_normalized.py
```

### Testing Commands
```bash
# Test producer research
uv run src/02_producer_research.py --limit 10

# Test variety processing
uv run src/03_variety_normalize.py --dry-run
uv run src/04_vivc_assign.py --limit 5

# Generate stats with varieties
uv run src/07_generate_stats.py --varieties

# Database: run tests (pytest tests/ once established)
uv run pytest tests/
```

## 📁 Key Data Files

| File | Purpose | Updated By |
|------|---------|------------|
| `data/01_unified_producers.jsonl` | Unified producer records | `01_producer_fetch.py` |
| `data/enriched_producers_cache.jsonl` | Enriched wine producer data | `02_producer_research.py` |
| `data/grape_variety_mapping.jsonl` | **Central variety database** | `03_variety_normalize.py`, `04_vivc_assign.py` |
| `data/05_wine_producers_final_normalized.jsonl` | **Final production dataset** | `05_data_final_normalized.py` |
| `data/grapegeek.db` | **SQLite database for Next.js** | `09_build_database.py` |

## ⚠️ Important Notes

### Manual Review Required
- **Step 3** (`03_variety_normalize.py`) output needs manual review as AI classification can be imprecise

### Critical Dependencies
- **VIVC Consolidation** MUST run after any VIVC assignments to merge duplicates
- **Final dataset** is the single source of truth for all outputs

### Pipeline Triggers
1. **New region indexing** → Full pipeline (steps 0-8)
2. **Re-running existing sources** → May find new producers/varieties
3. **New variety discoveries** → Variety processing steps (3-7)

---

## 🗄️ Database Access Layer

`src/includes/database.py` provides type-safe Python access to `data/grapegeek.db`.

See `src/DATABASE.md` for full API reference, dataclasses, and query examples.