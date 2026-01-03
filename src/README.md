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
    
    %% Step 1: Data Collection
    A3 --> B1[canada_province_winery_researcher.py]
    B1 --> D1[data/can/canada_province_wineries.jsonl]
    
    %% Step 2: Unify Sources  
    A1 --> B2[01_producer_fetch.py]
    A2 --> B2
    D1 --> B2
    B2 --> D2[data/01_unified_producers.jsonl]
    B2 --> D2M[data/01_unified_producers_metadata.json]
    
    %% Step 3: Research & Enrichment
    D2 --> B3[02_producer_research.py]
    B3 --> D3A[data/enriched_producers_cache.jsonl]
    B3 --> D3B[data/producer_geolocations_cache.jsonl]
    
    %% Step 4: Variety Processing (Manual Review Needed)
    D3A --> B4[08_variety_normalize.py]
    B4 --> D4[data/grape_variety_mapping.jsonl]
    D4 --> B5[vivc_assign.py] 
    B5 --> D4
    D4 --> B6[VIVC Consolidation]
    B6 --> D4
    
    %% Step 5: Final Dataset
    D2 --> B7[05_data_final_normalized.py]
    D3A --> B7
    D3B --> B7  
    D4 --> B7
    B7 --> D7[data/05_wine_producers_final_normalized.jsonl]
    
    %% Step 6: Outputs
    D7 --> B8[10_output_geojson.py]
    B8 --> D8[docs/assets/data/wine-producers-final.geojson]
    
    D4 --> B9[build_vivc_index.py]
    B9 --> D9A[docs/en/varieties/index.md]
    B9 --> D9B[docs/fr/varieties/index.md]
    
    D7 --> B10[11_generate_stats.py]
    B10 --> D10[dataset_statistics.txt]
    
    %% Styling
    classDef script fill:#e1f5fe
    classDef datafile fill:#f3e5f5
    classDef manual fill:#fff3e0
    
    class B1,B2,B3,B4,B5,B6,B7,B8,B9,B10 script
    class D1,D2,D2M,D3A,D3B,D4,D7,D8,D9A,D9B,D10 datafile
    class B4,B5,B6 manual
```

## 🚀 Command Reference

### New Region Research (Full Pipeline)
```bash
# 1. Research Canadian provinces (current: NB, NL, NS, PE)
uv run src/canada_province_winery_researcher.py --province "NB,NL,NS,PE" --previous-list data/can/canada_province_wineries.jsonl --yes --threads 4

# 2. Unify all data sources  
uv run src/01_producer_fetch.py

# 3. Research & enrich producers
uv run src/02_producer_research.py --yes

# 4. Normalize varieties (MANUAL REVIEW NEEDED)
uv run src/08_variety_normalize.py --limit 20

# 5. Assign VIVC data
uv run src/vivc_assign.py --limit 10

# 6. Consolidate VIVC duplicates (CRITICAL)
uv run src/includes/grape_varieties.py consolidate

# 7. Generate final dataset
uv run src/05_data_final_normalized.py

# 8. Generate outputs
uv run src/10_output_geojson.py
uv run src/build_vivc_index.py  
uv run src/11_generate_stats.py
```

### Variety Updates Only
```bash
# When new varieties found - steps 4-6 only
uv run src/08_variety_normalize.py --limit 20  # Manual review needed
uv run src/vivc_assign.py
uv run src/includes/grape_varieties.py consolidate  # CRITICAL
uv run src/05_data_final_normalized.py
```

### Testing Commands
```bash
# Test producer research
uv run src/02_producer_research.py --limit 10

# Test variety processing
uv run src/08_variety_normalize.py --dry-run
uv run src/vivc_assign.py --limit 5

# Generate stats with varieties
uv run src/11_generate_stats.py --varieties
```

## 📁 Key Data Files

| File | Purpose | Updated By |
|------|---------|------------|
| `data/01_unified_producers.jsonl` | Unified producer records | `01_producer_fetch.py` |
| `data/enriched_producers_cache.jsonl` | Enriched wine producer data | `02_producer_research.py` |
| `data/grape_variety_mapping.jsonl` | **Central variety database** | `08_variety_normalize.py`, `vivc_assign.py` |
| `data/05_wine_producers_final_normalized.jsonl` | **Final production dataset** | `05_data_final_normalized.py` |

## ⚠️ Important Notes

### Manual Review Required
- **Step 4** (`08_variety_normalize.py`) output needs manual review as AI classification can be imprecise

### Critical Dependencies
- **VIVC Consolidation** MUST run after any VIVC assignments to merge duplicates
- **Final dataset** is the single source of truth for all outputs

### Pipeline Triggers
1. **New region indexing** → Full pipeline (steps 1-8)
2. **Re-running existing sources** → May find new producers/varieties
3. **New variety discoveries** → Variety processing steps (4-6)

---

*For detailed script documentation, see individual script file headers.*