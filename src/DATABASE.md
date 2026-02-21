# Database Access Layer Documentation

## Overview

The `src/includes/database.py` module provides type-safe Python access to the GrapeGeek SQLite database. It uses dataclasses for type safety and provides query methods for all entity types.

## Features

- **Schema Version Validation**: Automatically validates database schema version on connection
- **Type-Safe Data Classes**: Producer, GrapeVariety, and Wine dataclasses with proper type hints
- **Full-Text Search**: FTS5-powered search for producers and wines
- **Relationship Loading**: Lazy loading of related data (wines, social media, activities)
- **Context Manager Support**: Use with `with` statement for automatic cleanup
- **Comprehensive Statistics**: Get database statistics and breakdowns

## Quick Start

```python
from src.includes.database import get_database

# Basic usage
db = get_database()
stats = db.get_stats()
print(f"Total producers: {stats['total_producers']:,}")
db.close()

# Context manager (recommended)
with get_database() as db:
    producer = db.get_producer('AV006')
    varieties = db.get_all_varieties()
```

## Data Classes

### Producer

```python
@dataclass
class Producer:
    id: int
    permit_id: str
    source: str
    country: str
    business_name: str
    state_province: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    website: Optional[str] = None
    # ... more fields

    # Related data (loaded on demand)
    wines: List[Dict] = field(default_factory=list)
    social_media: List[str] = field(default_factory=list)
    activities: List[str] = field(default_factory=list)
```

### GrapeVariety

```python
@dataclass
class GrapeVariety:
    id: int
    name: str
    is_grape: bool = True
    vivc_number: Optional[int] = None
    berry_skin_color: Optional[str] = None
    species: Optional[str] = None
    parent1_name: Optional[str] = None
    parent2_name: Optional[str] = None
    # ... more fields

    # Related data (loaded on demand)
    aliases: List[str] = field(default_factory=list)
    uses: List[Dict] = field(default_factory=list)
```

### Wine

```python
@dataclass
class Wine:
    id: int
    producer_id: int
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    vintage: Optional[str] = None

    # Related data (loaded on demand)
    grapes: List[str] = field(default_factory=list)
```

## Query Methods

### Producer Queries

```python
db = get_database()

# Get single producer
producer = db.get_producer('AV006')
producer_with_wines = db.get_producer('AV006', include_relationships=True)

# Get all producers
producers = db.get_all_producers()

# Search producers (FTS)
results = db.search_producers('vineyard')

# Filter by location
us_producers = db.get_producers_by_country('US')
ny_producers = db.get_producers_by_state_province('New York')
```

### Grape Variety Queries

```python
# Get single variety
variety = db.get_variety('Frontenac')
variety_with_uses = db.get_variety('Frontenac', include_relationships=True)

# Get by VIVC ID
variety = db.get_variety_by_vivc_id(17638)

# Get all varieties
varieties = db.get_all_varieties()

# Search varieties (LIKE)
results = db.search_varieties('pinot')

# Filter by attributes
red_varieties = db.get_varieties_by_color('Black')
vitis_vinifera = db.get_varieties_by_species('Vitis vinifera')
```

### Wine Queries

```python
# Get single wine
wine = db.get_wine(123)

# Get wines by producer
wines = db.get_wines_by_producer('AV006')

# Get wines with specific variety
wines = db.get_wines_with_variety('Frontenac')

# Search wines (FTS)
results = db.search_wines('dry red')
```

### Statistics

```python
stats = db.get_stats()

# Available statistics:
# - total_producers
# - total_varieties
# - total_wines
# - true_grapes
# - countries (dict: country -> count)
# - top_states_provinces (dict: state -> count)
# - species (dict: species -> count)
# - berry_colors (dict: color -> count)
# - geolocated_producers
# - producers_with_websites
```

## Relationship Loading

By default, relationships are **not loaded** for performance. Use `include_relationships=True` to load:

```python
# Without relationships (fast)
producer = db.get_producer('AV006')
print(len(producer.wines))  # 0

# With relationships (loads wines, social media, activities)
producer = db.get_producer('AV006', include_relationships=True)
print(len(producer.wines))  # Actual count
```

### Producer Relationships

```python
producer = db.get_producer('AV006', include_relationships=True)

# Wines (list of dicts)
for wine in producer.wines:
    print(wine['name'])

# Social media (list of URLs)
for url in producer.social_media:
    print(url)

# Activities (list of strings)
for activity in producer.activities:
    print(activity)
```

### Variety Relationships

```python
variety = db.get_variety('Frontenac', include_relationships=True)

# Aliases (list of strings)
for alias in variety.aliases:
    print(alias)

# Uses (list of dicts with wine info)
for use in variety.uses:
    print(f"{use['wine_name']} by {use['producer_name']}")
```

## Error Handling

### Schema Version Mismatch

```python
try:
    db = get_database()
except ValueError as e:
    print(f"Schema error: {e}")
    # Error message will suggest: "Please rebuild database: uv run src/09_build_database.py"
```

### Database Not Found

```python
try:
    db = get_database()
except FileNotFoundError as e:
    print(f"Database not found: {e}")
    # Error message will suggest building the database
```

### Handling Missing Data

All optional fields use `Optional[Type]` and return `None` if missing:

```python
producer = db.get_producer('AV006')

if producer.website:
    print(f"Website: {producer.website}")
else:
    print("No website available")

# Safe access to optional numeric fields
if producer.latitude and producer.longitude:
    print(f"Location: {producer.latitude}, {producer.longitude}")
```

## Performance Considerations

### Lazy Loading

Relationships are lazy-loaded to avoid N+1 query problems:

```python
# BAD: Loads relationships for each producer individually
producers = db.get_all_producers()
for p in producers:
    producer_with_wines = db.get_producer(p.permit_id, include_relationships=True)
    # This makes N queries!

# GOOD: Load basic info, then filter
producers = db.get_all_producers()
ny_producers = [p for p in producers if p.state_province == 'New York']
```

### Indexes

The database has indexes on frequently-queried columns:
- `producers.state_province`
- `producers.country`
- `producers.classification`
- `grape_varieties.vivc_number`
- All foreign keys

### Full-Text Search

FTS5 tables provide fast search for:
- **Producers**: business_name, permit_holder, wine_label, city
- **Wines**: name, description, winemaking

```python
# Fast FTS search
results = db.search_producers('vineyard')

# Slower LIKE search (use for short fields)
results = db.search_varieties('pin')
```

## Examples

### Find all geolocated producers in a region

```python
with get_database() as db:
    producers = db.get_producers_by_state_province('Nova Scotia')
    geolocated = [p for p in producers if p.latitude and p.longitude]

    print(f"Found {len(geolocated)} geolocated producers")
    for p in geolocated:
        print(f"{p.business_name}: {p.latitude}, {p.longitude}")
```

### Get variety pedigree information

```python
with get_database() as db:
    variety = db.get_variety('Marquette')

    if variety:
        print(f"Name: {variety.name}")
        if variety.parent1_name or variety.parent2_name:
            parents = []
            if variety.parent1_name:
                parents.append(variety.parent1_name)
            if variety.parent2_name:
                parents.append(variety.parent2_name)
            print(f"Pedigree: {' × '.join(parents)}")
```

### Export producers to GeoJSON

```python
import json

with get_database() as db:
    producers = db.get_all_producers()

    features = []
    for p in producers:
        if p.latitude and p.longitude:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [p.longitude, p.latitude]
                },
                "properties": {
                    "name": p.business_name,
                    "city": p.city,
                    "website": p.website
                }
            })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open('producers.geojson', 'w') as f:
        json.dump(geojson, f, indent=2)
```

### Generate statistics report

```python
with get_database() as db:
    stats = db.get_stats()

    print("GrapeGeek Database Statistics")
    print("=" * 50)
    print(f"Producers: {stats['total_producers']:,}")
    print(f"Grape Varieties: {stats['total_varieties']:,}")
    print(f"Wines: {stats['total_wines']:,}")
    print(f"\nBy Country:")
    for country, count in stats['countries'].items():
        pct = count / stats['total_producers'] * 100
        print(f"  {country}: {count:,} ({pct:.1f}%)")
```

## Testing

Run the test suite:

```bash
uv run test_database_access.py
```

Run the examples:

```bash
uv run example_database_usage.py
```

Test the module directly:

```bash
uv run src/includes/database.py
```

## Integration with Next.js

The TypeScript equivalent of this module is being developed in `grapegeek-nextjs/lib/database.ts`.

Key differences:
- **TypeScript interfaces** instead of Python dataclasses
- **better-sqlite3** library instead of sqlite3
- Same query methods and patterns
- Schema version validation matches Python version

Both modules share:
- Same database file (`data/grapegeek.db`)
- Same schema version constant
- Same validation logic
- Similar API design

## Troubleshooting

### "Schema version mismatch" error

Rebuild the database:
```bash
uv run src/09_build_database.py
```

### "Database not found" error

Build the database:
```bash
uv run src/09_build_database.py
```

### Missing data in relationships

Check if you're using `include_relationships=True`:
```python
# Wrong - relationships not loaded
producer = db.get_producer('AV006')
print(producer.wines)  # []

# Correct
producer = db.get_producer('AV006', include_relationships=True)
print(producer.wines)  # Actual wines
```

### Slow queries

Consider:
1. Are you loading relationships you don't need?
2. Can you filter at the database level instead of Python?
3. Are you using the right search method (FTS vs LIKE)?

```python
# Slow: Filter in Python
all_producers = db.get_all_producers()
ny_producers = [p for p in all_producers if p.state_province == 'New York']

# Fast: Filter at database level
ny_producers = db.get_producers_by_state_province('New York')
```

## See Also

- `src/09_build_database.py` - Database builder script
- `planning/DATABASE_SCHEMA_MANAGEMENT.md` - Schema versioning strategy
- `test_database_access.py` - Test suite
- `example_database_usage.py` - Usage examples
