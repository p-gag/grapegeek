# Geographic Overlay Data

## States/Provinces Coverage Map

The `na-regions.json` file contains simplified GeoJSON data for US states and Canadian provinces used to show database coverage on maps.

### File Structure

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Minnesota",
        "code": "MN",
        "country": "USA"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [...]
      }
    }
  ]
}
```

### Adding New Regions

To add a new state/province to the overlay:

1. **Find GeoJSON data**: Use sources like:
   - https://github.com/PublicaMundi/MappingAPI/tree/master/data/geojson
   - https://eric.clst.org/tech/usgeojson/
   - Natural Earth Data: https://www.naturalearthdata.com/

2. **Simplify coordinates**: Use https://mapshaper.org/ to reduce file size
   - Upload GeoJSON
   - Simplify to ~5-10% (balance detail vs file size)
   - Export as GeoJSON

3. **Add to na-regions.json**:
   - Copy the feature object
   - Ensure `properties.name` matches database `state_province` field
   - Ensure `properties.country` is "USA" or "CANADA"

4. **Database matching**: The overlay automatically highlights regions that exist in the database's `producers` table with matching `state_province` values.

### Updating Coverage

The map component queries the database at runtime:
```sql
SELECT DISTINCT state_province, country
FROM producers
WHERE state_province IS NOT NULL
```

No code changes needed - as you add winegrowers to new states, they'll automatically be highlighted on the map!

### Current Coverage

See the map legend or run:
```bash
sqlite3 grapegeek-nextjs/data/grapegeek.db "SELECT DISTINCT state_province, country FROM producers ORDER BY country, state_province;"
```
