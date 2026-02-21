#!/usr/bin/env python3
"""
Database Access Layer for GrapeGeek SQLite Database

Type-safe query utilities for the GrapeGeek SQLite database.
Provides dataclasses and methods for querying producers, grape varieties, and wines.

Usage:
    from src.includes.database import GrapeGeekDatabase

    db = GrapeGeekDatabase()
    producer = db.get_producer('AV006')
    varieties = db.get_all_varieties()
    stats = db.get_stats()
    db.close()
"""

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any


# Expected schema version - must match database
EXPECTED_SCHEMA_VERSION = 1


@dataclass
class Producer:
    """Wine producer with location, contact info, and products"""
    id: int
    permit_id: str
    source: str
    country: str
    business_name: str
    state_province: Optional[str] = None
    permit_holder: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    classification: Optional[str] = None
    website: Optional[str] = None
    wine_label: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geocoding_method: Optional[str] = None
    verified_wine_producer: bool = True
    enriched_at: Optional[str] = None
    created_at: Optional[str] = None

    # Related data (loaded on demand)
    wines: List[Dict[str, Any]] = field(default_factory=list)
    social_media: List[str] = field(default_factory=list)
    activities: List[str] = field(default_factory=list)


@dataclass
class GrapeVariety:
    """Grape variety with pedigree and usage information"""
    id: int
    name: str
    is_grape: bool = True
    vivc_number: Optional[int] = None
    berry_skin_color: Optional[str] = None
    country_of_origin: Optional[str] = None
    species: Optional[str] = None
    parent1_name: Optional[str] = None
    parent2_name: Optional[str] = None
    sex_of_flower: Optional[str] = None
    year_of_crossing: Optional[str] = None
    vivc_assignment_status: Optional[str] = None
    no_wine: bool = False
    source: str = 'grapegeek'

    # Related data (loaded on demand)
    aliases: List[str] = field(default_factory=list)
    uses: List[Dict[str, Any]] = field(default_factory=list)  # List of {wine_id, wine_name, producer_id}


@dataclass
class Wine:
    """Wine product with grape composition"""
    id: int
    producer_id: int
    name: str
    description: Optional[str] = None
    winemaking: Optional[str] = None
    type: Optional[str] = None
    vintage: Optional[str] = None

    # Related data (loaded on demand)
    grapes: List[str] = field(default_factory=list)  # List of grape variety names
    producer_name: Optional[str] = None  # Populated when needed


def validate_schema_version(conn: sqlite3.Connection):
    """
    Ensure database schema matches expected version.

    Args:
        conn: SQLite connection

    Raises:
        ValueError: If schema version doesn't match or is missing
    """
    result = conn.execute(
        "SELECT value FROM schema_info WHERE key = 'version'"
    ).fetchone()

    if not result:
        raise ValueError(
            "Database missing schema version info. "
            "Please rebuild database: python src/09_build_database.py"
        )

    version = int(result[0])
    if version != EXPECTED_SCHEMA_VERSION:
        raise ValueError(
            f"Schema version mismatch: expected {EXPECTED_SCHEMA_VERSION}, got {version}. "
            "Please rebuild database: python src/09_build_database.py"
        )


class GrapeGeekDatabase:
    """
    Type-safe database query interface for GrapeGeek SQLite database.

    Provides methods for querying producers, grape varieties, and wines
    with full-text search support.

    Example:
        db = GrapeGeekDatabase()
        producer = db.get_producer('AV006')
        varieties = db.search_varieties('pinot')
        stats = db.get_stats()
        db.close()
    """

    def __init__(self, db_path: str = "data/grapegeek.db"):
        """
        Initialize database connection and validate schema version.

        Args:
            db_path: Path to SQLite database file

        Raises:
            FileNotFoundError: If database file doesn't exist
            ValueError: If schema version doesn't match
        """
        self.db_path = Path(db_path)

        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}. "
                "Please build database: python src/09_build_database.py"
            )

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        # Validate schema version on connection
        validate_schema_version(self.conn)

    # ========================================
    # Producer queries
    # ========================================

    def get_producer(self, permit_id: str, include_relationships: bool = True) -> Optional[Producer]:
        """
        Get producer by permit ID with optional relationships.

        Args:
            permit_id: Producer permit ID
            include_relationships: Load wines, social media, and activities

        Returns:
            Producer object or None if not found
        """
        row = self.conn.execute(
            "SELECT * FROM producers WHERE permit_id = ?",
            (permit_id,)
        ).fetchone()

        if not row:
            return None

        producer = self._row_to_producer(row)

        if include_relationships:
            self._load_producer_relationships(producer)

        return producer

    def get_all_producers(self, include_relationships: bool = False) -> List[Producer]:
        """
        Get all producers.

        Args:
            include_relationships: Load wines, social media, and activities

        Returns:
            List of Producer objects
        """
        rows = self.conn.execute("SELECT * FROM producers ORDER BY business_name").fetchall()
        producers = [self._row_to_producer(row) for row in rows]

        if include_relationships:
            for producer in producers:
                self._load_producer_relationships(producer)

        return producers

    def search_producers(self, query: str) -> List[Producer]:
        """
        Full-text search across producers.

        Searches business_name, permit_holder, wine_label, and city.

        Args:
            query: Search query

        Returns:
            List of matching Producer objects
        """
        rows = self.conn.execute("""
            SELECT p.*
            FROM producers p
            JOIN producers_fts ON producers_fts.rowid = p.id
            WHERE producers_fts MATCH ?
            ORDER BY p.business_name
        """, (query,)).fetchall()

        return [self._row_to_producer(row) for row in rows]

    def get_producers_by_country(self, country: str) -> List[Producer]:
        """Get all producers in a specific country"""
        rows = self.conn.execute(
            "SELECT * FROM producers WHERE country = ? ORDER BY business_name",
            (country,)
        ).fetchall()

        return [self._row_to_producer(row) for row in rows]

    def get_producers_by_state_province(self, state_province: str) -> List[Producer]:
        """Get all producers in a specific state/province"""
        rows = self.conn.execute(
            "SELECT * FROM producers WHERE state_province = ? ORDER BY business_name",
            (state_province,)
        ).fetchall()

        return [self._row_to_producer(row) for row in rows]

    # ========================================
    # Grape variety queries
    # ========================================

    def get_variety(self, name: str, include_relationships: bool = True) -> Optional[GrapeVariety]:
        """
        Get grape variety by name with optional relationships.

        Args:
            name: Variety name
            include_relationships: Load aliases and usage data

        Returns:
            GrapeVariety object or None if not found
        """
        row = self.conn.execute(
            "SELECT * FROM grape_varieties WHERE name = ?",
            (name,)
        ).fetchone()

        if not row:
            return None

        variety = self._row_to_variety(row)

        if include_relationships:
            self._load_variety_relationships(variety)

        return variety

    def get_variety_by_vivc_id(self, vivc_id: int, include_relationships: bool = True) -> Optional[GrapeVariety]:
        """
        Get grape variety by VIVC number.

        Args:
            vivc_id: VIVC number
            include_relationships: Load aliases and usage data

        Returns:
            GrapeVariety object or None if not found
        """
        row = self.conn.execute(
            "SELECT * FROM grape_varieties WHERE vivc_number = ?",
            (vivc_id,)
        ).fetchone()

        if not row:
            return None

        variety = self._row_to_variety(row)

        if include_relationships:
            self._load_variety_relationships(variety)

        return variety

    def get_all_varieties(self, include_relationships: bool = False) -> List[GrapeVariety]:
        """
        Get all grape varieties.

        Args:
            include_relationships: Load aliases and usage data

        Returns:
            List of GrapeVariety objects
        """
        rows = self.conn.execute("SELECT * FROM grape_varieties ORDER BY name").fetchall()
        varieties = [self._row_to_variety(row) for row in rows]

        if include_relationships:
            for variety in varieties:
                self._load_variety_relationships(variety)

        return varieties

    def search_varieties(self, query: str) -> List[GrapeVariety]:
        """
        Search grape varieties by name (case-insensitive partial match).

        Note: This uses LIKE search, not FTS, since variety names are short.

        Args:
            query: Search query

        Returns:
            List of matching GrapeVariety objects
        """
        rows = self.conn.execute("""
            SELECT * FROM grape_varieties
            WHERE name LIKE ?
            ORDER BY name
        """, (f'%{query}%',)).fetchall()

        return [self._row_to_variety(row) for row in rows]

    def get_varieties_by_species(self, species: str) -> List[GrapeVariety]:
        """Get all varieties of a specific species"""
        rows = self.conn.execute(
            "SELECT * FROM grape_varieties WHERE species = ? ORDER BY name",
            (species,)
        ).fetchall()

        return [self._row_to_variety(row) for row in rows]

    def get_varieties_by_color(self, color: str) -> List[GrapeVariety]:
        """Get all varieties with a specific berry color"""
        rows = self.conn.execute(
            "SELECT * FROM grape_varieties WHERE berry_skin_color = ? ORDER BY name",
            (color,)
        ).fetchall()

        return [self._row_to_variety(row) for row in rows]

    # ========================================
    # Wine queries
    # ========================================

    def get_wine(self, wine_id: int, include_grapes: bool = True) -> Optional[Wine]:
        """
        Get wine by ID with optional grape composition.

        Args:
            wine_id: Wine ID
            include_grapes: Load grape variety list

        Returns:
            Wine object or None if not found
        """
        row = self.conn.execute(
            "SELECT * FROM wines WHERE id = ?",
            (wine_id,)
        ).fetchone()

        if not row:
            return None

        wine = self._row_to_wine(row)

        if include_grapes:
            self._load_wine_grapes(wine)

        return wine

    def get_wines_by_producer(self, permit_id: str) -> List[Wine]:
        """
        Get all wines for a producer.

        Args:
            permit_id: Producer permit ID

        Returns:
            List of Wine objects
        """
        rows = self.conn.execute("""
            SELECT w.*
            FROM wines w
            JOIN producers p ON w.producer_id = p.id
            WHERE p.permit_id = ?
            ORDER BY w.name
        """, (permit_id,)).fetchall()

        wines = [self._row_to_wine(row) for row in rows]

        for wine in wines:
            self._load_wine_grapes(wine)

        return wines

    def get_wines_with_variety(self, variety_name: str) -> List[Wine]:
        """
        Get all wines using a specific grape variety.

        Args:
            variety_name: Grape variety name

        Returns:
            List of Wine objects
        """
        rows = self.conn.execute("""
            SELECT w.*
            FROM wines w
            JOIN wine_grapes wg ON w.id = wg.wine_id
            JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
            WHERE gv.name = ?
            ORDER BY w.name
        """, (variety_name,)).fetchall()

        wines = [self._row_to_wine(row) for row in rows]

        for wine in wines:
            self._load_wine_grapes(wine)

        return wines

    def search_wines(self, query: str) -> List[Wine]:
        """
        Full-text search across wines.

        Searches name, description, and winemaking notes.

        Args:
            query: Search query

        Returns:
            List of matching Wine objects
        """
        rows = self.conn.execute("""
            SELECT w.*
            FROM wines w
            JOIN wines_fts ON wines_fts.rowid = w.id
            WHERE wines_fts MATCH ?
            ORDER BY w.name
        """, (query,)).fetchall()

        wines = [self._row_to_wine(row) for row in rows]

        for wine in wines:
            self._load_wine_grapes(wine)

        return wines

    # ========================================
    # Statistics
    # ========================================

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.

        Returns:
            Dictionary with counts and breakdowns
        """
        stats = {}

        # Basic counts
        stats['total_producers'] = self.conn.execute("SELECT COUNT(*) FROM producers").fetchone()[0]
        stats['total_varieties'] = self.conn.execute("SELECT COUNT(*) FROM grape_varieties").fetchone()[0]
        stats['total_wines'] = self.conn.execute("SELECT COUNT(*) FROM wines").fetchone()[0]

        # True grapes only
        stats['true_grapes'] = self.conn.execute(
            "SELECT COUNT(*) FROM grape_varieties WHERE is_grape = 1"
        ).fetchone()[0]

        # Country breakdown
        country_rows = self.conn.execute("""
            SELECT country, COUNT(*) as count
            FROM producers
            GROUP BY country
            ORDER BY count DESC
        """).fetchall()
        stats['countries'] = {row[0]: row[1] for row in country_rows}

        # State/Province breakdown (top 10)
        state_rows = self.conn.execute("""
            SELECT state_province, COUNT(*) as count
            FROM producers
            WHERE state_province IS NOT NULL
            GROUP BY state_province
            ORDER BY count DESC
            LIMIT 10
        """).fetchall()
        stats['top_states_provinces'] = {row[0]: row[1] for row in state_rows}

        # Species breakdown
        species_rows = self.conn.execute("""
            SELECT species, COUNT(*) as count
            FROM grape_varieties
            WHERE species IS NOT NULL
            GROUP BY species
            ORDER BY count DESC
        """).fetchall()
        stats['species'] = {row[0]: row[1] for row in species_rows}

        # Berry color breakdown
        color_rows = self.conn.execute("""
            SELECT berry_skin_color, COUNT(*) as count
            FROM grape_varieties
            WHERE berry_skin_color IS NOT NULL
            GROUP BY berry_skin_color
            ORDER BY count DESC
        """).fetchall()
        stats['berry_colors'] = {row[0]: row[1] for row in color_rows}

        # Producers with geolocation
        stats['geolocated_producers'] = self.conn.execute(
            "SELECT COUNT(*) FROM producers WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
        ).fetchone()[0]

        # Producers with websites
        stats['producers_with_websites'] = self.conn.execute(
            "SELECT COUNT(*) FROM producers WHERE website IS NOT NULL AND website != ''"
        ).fetchone()[0]

        return stats

    # ========================================
    # Helper methods
    # ========================================

    def _row_to_producer(self, row: sqlite3.Row) -> Producer:
        """Convert database row to Producer dataclass"""
        return Producer(
            id=row['id'],
            permit_id=row['permit_id'],
            source=row['source'],
            country=row['country'],
            business_name=row['business_name'],
            state_province=row['state_province'],
            permit_holder=row['permit_holder'],
            address=row['address'],
            city=row['city'],
            postal_code=row['postal_code'],
            classification=row['classification'],
            website=row['website'],
            wine_label=row['wine_label'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            geocoding_method=row['geocoding_method'],
            verified_wine_producer=bool(row['verified_wine_producer']),
            enriched_at=row['enriched_at'],
            created_at=row['created_at']
        )

    def _row_to_variety(self, row: sqlite3.Row) -> GrapeVariety:
        """Convert database row to GrapeVariety dataclass"""
        return GrapeVariety(
            id=row['id'],
            name=row['name'],
            is_grape=bool(row['is_grape']),
            vivc_number=row['vivc_number'],
            berry_skin_color=row['berry_skin_color'],
            country_of_origin=row['country_of_origin'],
            species=row['species'],
            parent1_name=row['parent1_name'],
            parent2_name=row['parent2_name'],
            sex_of_flower=row['sex_of_flower'],
            year_of_crossing=row['year_of_crossing'],
            vivc_assignment_status=row['vivc_assignment_status'],
            no_wine=bool(row['no_wine']),
            source=row['source']
        )

    def _row_to_wine(self, row: sqlite3.Row) -> Wine:
        """Convert database row to Wine dataclass"""
        return Wine(
            id=row['id'],
            producer_id=row['producer_id'],
            name=row['name'],
            description=row['description'],
            winemaking=row['winemaking'],
            type=row['type'],
            vintage=row['vintage']
        )

    def _load_producer_relationships(self, producer: Producer):
        """Load wines, social media, and activities for a producer"""
        # Load wines
        wine_rows = self.conn.execute(
            "SELECT * FROM wines WHERE producer_id = ? ORDER BY name",
            (producer.id,)
        ).fetchall()
        producer.wines = [dict(row) for row in wine_rows]

        # Load social media
        social_rows = self.conn.execute(
            "SELECT url FROM producer_social_media WHERE producer_id = ?",
            (producer.id,)
        ).fetchall()
        producer.social_media = [row[0] for row in social_rows]

        # Load activities
        activity_rows = self.conn.execute(
            "SELECT activity FROM producer_activities WHERE producer_id = ?",
            (producer.id,)
        ).fetchall()
        producer.activities = [row[0] for row in activity_rows]

    def _load_variety_relationships(self, variety: GrapeVariety):
        """Load aliases and usage data for a variety"""
        # Load aliases
        alias_rows = self.conn.execute(
            "SELECT alias FROM grape_aliases WHERE grape_variety_id = ?",
            (variety.id,)
        ).fetchall()
        variety.aliases = [row[0] for row in alias_rows]

        # Load usage (wines using this variety)
        use_rows = self.conn.execute("""
            SELECT w.id as wine_id, w.name as wine_name, p.permit_id as producer_id, p.business_name
            FROM wine_grapes wg
            JOIN wines w ON wg.wine_id = w.id
            JOIN producers p ON w.producer_id = p.id
            WHERE wg.grape_variety_id = ?
            ORDER BY p.business_name, w.name
        """, (variety.id,)).fetchall()

        variety.uses = [
            {
                'wine_id': row[0],
                'wine_name': row[1],
                'producer_id': row[2],
                'producer_name': row[3]
            }
            for row in use_rows
        ]

    def _load_wine_grapes(self, wine: Wine):
        """Load grape varieties for a wine"""
        grape_rows = self.conn.execute("""
            SELECT gv.name
            FROM wine_grapes wg
            JOIN grape_varieties gv ON wg.grape_variety_id = gv.id
            WHERE wg.wine_id = ?
            ORDER BY gv.name
        """, (wine.id,)).fetchall()

        wine.grapes = [row[0] for row in grape_rows]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()


# ========================================
# Convenience functions
# ========================================

def get_database(db_path: str = "data/grapegeek.db") -> GrapeGeekDatabase:
    """
    Get a database instance (convenience function).

    Args:
        db_path: Path to database file

    Returns:
        GrapeGeekDatabase instance

    Example:
        db = get_database()
        stats = db.get_stats()
        db.close()
    """
    return GrapeGeekDatabase(db_path)


if __name__ == "__main__":
    # Simple test/demo
    print("GrapeGeek Database Access Layer")
    print("=" * 50)

    try:
        db = get_database()

        print("\nDatabase Statistics:")
        stats = db.get_stats()
        print(f"  Total Producers: {stats['total_producers']:,}")
        print(f"  Total Varieties: {stats['total_varieties']:,}")
        print(f"  True Grapes: {stats['true_grapes']:,}")
        print(f"  Total Wines: {stats['total_wines']:,}")
        print(f"  Geolocated Producers: {stats['geolocated_producers']:,}")

        print("\nCountries:")
        for country, count in stats['countries'].items():
            print(f"  {country}: {count:,}")

        print("\nTop Species:")
        for species, count in list(stats['species'].items())[:5]:
            print(f"  {species}: {count:,}")

        # Test producer query
        print("\nTesting Producer Query:")
        producers = db.get_all_producers()
        if producers:
            first = producers[0]
            print(f"  First producer: {first.business_name}")
            print(f"  Location: {first.city}, {first.state_province}, {first.country}")
            print(f"  Coordinates: {first.latitude}, {first.longitude}")

        # Test variety query
        print("\nTesting Variety Query:")
        varieties = db.get_all_varieties()
        if varieties:
            first = varieties[0]
            print(f"  First variety: {first.name}")
            print(f"  Species: {first.species}")
            print(f"  Color: {first.berry_skin_color}")

        db.close()
        print("\n✓ Database access layer working correctly!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
