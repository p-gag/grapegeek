#!/usr/bin/env python3
"""
Database Builder for GrapeGeek
Converts JSONL data to SQLite database with proper schema, indexes, and FTS.

Usage:
    uv run src/09_build_database.py [options]

Options:
    --output PATH     Custom database output path (default: data/grapegeek.db)
    --verbose         Show detailed progress information
    --validate        Validate database after creation and exit
"""

import sqlite3
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime


class DatabaseBuilder:
    """Builds SQLite database from JSONL source files"""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str = "data/grapegeek.db", verbose: bool = False):
        self.db_path = Path(db_path)
        self.verbose = verbose
        self.conn: Optional[sqlite3.Connection] = None

        # Statistics
        self.stats = {
            'varieties_imported': 0,
            'aliases_imported': 0,
            'photos_imported': 0,
            'producers_imported': 0,
            'wines_imported': 0,
            'relationships_created': 0,
            'social_media_imported': 0,
            'activities_imported': 0,
            'skipped_records': 0,
            'warnings': []
        }

    def log(self, message: str):
        """Print message if verbose mode enabled"""
        if self.verbose:
            print(f"  {message}")

    def create_schema(self):
        """Create all tables, indexes, and FTS tables"""
        print("📊 Creating database schema...")

        # Schema version tracking
        self.conn.execute("""
            CREATE TABLE schema_info (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        self.conn.execute(
            "INSERT INTO schema_info (key, value) VALUES (?, ?)",
            ('version', str(self.SCHEMA_VERSION))
        )
        self.conn.execute(
            "INSERT INTO schema_info (key, value) VALUES (?, ?)",
            ('created_at', datetime.now().isoformat())
        )

        # Producers table
        self.conn.execute("""
            CREATE TABLE producers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                permit_id TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                country TEXT NOT NULL,
                state_province TEXT,
                business_name TEXT NOT NULL,
                permit_holder TEXT,
                address TEXT,
                city TEXT,
                postal_code TEXT,
                classification TEXT,
                website TEXT,
                wine_label TEXT,
                latitude REAL,
                longitude REAL,
                geocoding_method TEXT,
                verified_wine_producer BOOLEAN DEFAULT 1,
                enriched_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Wines table
        self.conn.execute("""
            CREATE TABLE wines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producer_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                winemaking TEXT,
                type TEXT,
                vintage TEXT,
                FOREIGN KEY (producer_id) REFERENCES producers(id) ON DELETE CASCADE
            )
        """)

        # Grape varieties table
        self.conn.execute("""
            CREATE TABLE grape_varieties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                is_grape BOOLEAN NOT NULL DEFAULT 1,
                vivc_number INTEGER,
                berry_skin_color TEXT,
                country_of_origin TEXT,
                species TEXT,
                parent1_name TEXT,
                parent2_name TEXT,
                sex_of_flower TEXT,
                year_of_crossing TEXT,
                vivc_assignment_status TEXT,
                no_wine BOOLEAN DEFAULT 0,
                source TEXT DEFAULT 'grapegeek'
            )
        """)

        # Wine-Grape many-to-many relationship
        self.conn.execute("""
            CREATE TABLE wine_grapes (
                wine_id INTEGER NOT NULL,
                grape_variety_id INTEGER NOT NULL,
                PRIMARY KEY (wine_id, grape_variety_id),
                FOREIGN KEY (wine_id) REFERENCES wines(id) ON DELETE CASCADE,
                FOREIGN KEY (grape_variety_id) REFERENCES grape_varieties(id) ON DELETE CASCADE
            )
        """)

        # Grape variety aliases
        self.conn.execute("""
            CREATE TABLE grape_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grape_variety_id INTEGER NOT NULL,
                alias TEXT NOT NULL,
                FOREIGN KEY (grape_variety_id) REFERENCES grape_varieties(id) ON DELETE CASCADE
            )
        """)

        # Grape variety photos
        self.conn.execute("""
            CREATE TABLE grape_variety_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grape_variety_id INTEGER NOT NULL,
                photo_type TEXT NOT NULL,
                filename TEXT NOT NULL,
                gcs_url TEXT,
                vivc_url TEXT,
                credits TEXT,
                FOREIGN KEY (grape_variety_id) REFERENCES grape_varieties(id) ON DELETE CASCADE
            )
        """)

        # Producer social media
        self.conn.execute("""
            CREATE TABLE producer_social_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producer_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                FOREIGN KEY (producer_id) REFERENCES producers(id) ON DELETE CASCADE
            )
        """)

        # Producer activities
        self.conn.execute("""
            CREATE TABLE producer_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producer_id INTEGER NOT NULL,
                activity TEXT NOT NULL,
                FOREIGN KEY (producer_id) REFERENCES producers(id) ON DELETE CASCADE
            )
        """)

        self.log("Created core tables")

        # Create indexes
        self.conn.execute("CREATE INDEX idx_producers_state ON producers(state_province)")
        self.conn.execute("CREATE INDEX idx_producers_country ON producers(country)")
        self.conn.execute("CREATE INDEX idx_producers_classification ON producers(classification)")
        self.conn.execute("CREATE INDEX idx_wines_producer ON wines(producer_id)")
        self.conn.execute("CREATE INDEX idx_wines_type ON wines(type)")
        self.conn.execute("CREATE INDEX idx_wine_grapes_wine ON wine_grapes(wine_id)")
        self.conn.execute("CREATE INDEX idx_wine_grapes_grape ON wine_grapes(grape_variety_id)")
        self.conn.execute("CREATE INDEX idx_grape_aliases_variety ON grape_aliases(grape_variety_id)")
        self.conn.execute("CREATE INDEX idx_grape_varieties_vivc ON grape_varieties(vivc_number)")
        self.conn.execute("CREATE INDEX idx_grape_variety_photos_variety ON grape_variety_photos(grape_variety_id)")

        self.log("Created indexes")

        # Create FTS tables
        self.conn.execute("""
            CREATE VIRTUAL TABLE wines_fts USING fts5(
                name,
                description,
                winemaking,
                content=wines,
                content_rowid=id
            )
        """)

        self.conn.execute("""
            CREATE VIRTUAL TABLE producers_fts USING fts5(
                business_name,
                permit_holder,
                wine_label,
                city,
                content=producers,
                content_rowid=id
            )
        """)

        self.log("Created FTS tables")
        print("✓ Schema created")

    def import_grape_varieties(self, jsonl_path: str):
        """Import grape varieties and aliases from JSONL"""
        print("🍇 Importing grape varieties...")

        path = Path(jsonl_path)
        if not path.exists():
            print(f"⚠️  Warning: {jsonl_path} not found, skipping grape varieties")
            self.stats['warnings'].append(f"Grape variety file not found: {jsonl_path}")
            return

        varieties_added = 0
        aliases_added = 0
        photos_added = 0

        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())

                    # Insert variety
                    name = data.get('name')
                    if not name:
                        self.log(f"Skipping line {line_num}: missing name")
                        self.stats['skipped_records'] += 1
                        continue

                    # Determine if it's actually a grape
                    is_grape = data.get('is_grape', True)

                    # Extract data from portfolio if it exists (new format)
                    portfolio = data.get('portfolio', {})
                    grape_info = portfolio.get('grape', {}) if isinstance(portfolio, dict) else {}

                    # Get VIVC number from portfolio or top level (for backwards compatibility)
                    vivc_number = None
                    if isinstance(grape_info, dict):
                        vivc_number = grape_info.get('vivc_number')
                    if not vivc_number:
                        vivc_number = data.get('vivc_number')

                    # Get other fields from portfolio or top level
                    berry_skin_color = portfolio.get('berry_skin_color') if isinstance(portfolio, dict) else None
                    if not berry_skin_color:
                        berry_skin_color = data.get('berry_skin_color')

                    species = portfolio.get('species') if isinstance(portfolio, dict) else None
                    if not species:
                        species = data.get('species')

                    country_of_origin = portfolio.get('country_of_origin') if isinstance(portfolio, dict) else None
                    if not country_of_origin:
                        country_of_origin = data.get('country_of_origin')

                    # Get parent names from portfolio or top level
                    parent1_name = None
                    parent2_name = None
                    if isinstance(portfolio, dict):
                        parent1 = portfolio.get('parent1', {})
                        parent2 = portfolio.get('parent2', {})
                        if isinstance(parent1, dict):
                            parent1_name = parent1.get('name')
                        if isinstance(parent2, dict):
                            parent2_name = parent2.get('name')
                    if not parent1_name:
                        parent1_name = data.get('parent1_name')
                    if not parent2_name:
                        parent2_name = data.get('parent2_name')

                    cursor = self.conn.execute("""
                        INSERT OR IGNORE INTO grape_varieties (
                            name, is_grape, vivc_number, berry_skin_color,
                            country_of_origin, species, parent1_name, parent2_name,
                            sex_of_flower, year_of_crossing, vivc_assignment_status,
                            no_wine, source
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        name,
                        is_grape,
                        vivc_number,
                        berry_skin_color,
                        country_of_origin,
                        species,
                        parent1_name,
                        parent2_name,
                        portfolio.get('sex_of_flower') or data.get('sex_of_flower'),
                        portfolio.get('year_of_crossing') or data.get('year_of_crossing'),
                        data.get('vivc_assignment_status'),
                        data.get('no_wine', False),
                        data.get('source', 'grapegeek')
                    ))

                    if cursor.rowcount > 0:
                        varieties_added += 1
                        variety_id = cursor.lastrowid

                        # Insert aliases
                        aliases = data.get('aliases', [])
                        for alias in aliases:
                            if alias and alias != name:  # Don't add duplicate of main name
                                self.conn.execute("""
                                    INSERT INTO grape_aliases (grape_variety_id, alias)
                                    VALUES (?, ?)
                                """, (variety_id, alias))
                                aliases_added += 1

                        # Insert photos from portfolio
                        portfolio = data.get('portfolio', {})
                        if isinstance(portfolio, dict):
                            photos = portfolio.get('photos', [])
                            for photo in photos:
                                if isinstance(photo, dict):
                                    filename = photo.get('filename', '')

                                    # Use image_url from JSONL (may be GCS or VIVC)
                                    # Use download_url as fallback (original VIVC URL)
                                    image_url = photo.get('image_url', '')
                                    download_url = photo.get('download_url', '')

                                    # Determine which is GCS and which is VIVC
                                    gcs_url = None
                                    vivc_url = None

                                    if 'storage.googleapis.com' in image_url:
                                        gcs_url = image_url
                                        vivc_url = download_url  # Fallback to original VIVC
                                    else:
                                        vivc_url = image_url  # Use VIVC as primary
                                        gcs_url = None

                                    self.conn.execute("""
                                        INSERT INTO grape_variety_photos (
                                            grape_variety_id, photo_type, filename,
                                            gcs_url, vivc_url, credits
                                        ) VALUES (?, ?, ?, ?, ?, ?)
                                    """, (
                                        variety_id,
                                        photo.get('photo_type', ''),
                                        filename,
                                        gcs_url,
                                        vivc_url,
                                        photo.get('credits', '')
                                    ))
                                    photos_added += 1

                except json.JSONDecodeError as e:
                    self.log(f"JSON error on line {line_num}: {e}")
                    self.stats['skipped_records'] += 1
                except Exception as e:
                    self.log(f"Error on line {line_num}: {e}")
                    self.stats['skipped_records'] += 1

        self.stats['varieties_imported'] = varieties_added
        self.stats['aliases_imported'] = aliases_added
        self.stats['photos_imported'] = photos_added
        print(f"✓ Imported {varieties_added:,} varieties with {aliases_added:,} aliases and {photos_added:,} photos")

    def import_producers(self, jsonl_path: str):
        """Import producers, wines, and related data from JSONL"""
        print("🏭 Importing producers and wines...")

        path = Path(jsonl_path)
        if not path.exists():
            print(f"⚠️  Warning: {jsonl_path} not found, skipping producers")
            self.stats['warnings'].append(f"Producer file not found: {jsonl_path}")
            return

        producers_added = 0
        wines_added = 0

        # Build a cache of grape variety name -> id for performance
        variety_cache = {}
        cursor = self.conn.execute("SELECT id, name FROM grape_varieties")
        for row in cursor:
            variety_cache[row[1].lower()] = row[0]

        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())

                    # Insert producer
                    permit_id = data.get('permit_id')
                    business_name = data.get('business_name')

                    if not permit_id or not business_name:
                        self.log(f"Skipping line {line_num}: missing permit_id or business_name")
                        self.stats['skipped_records'] += 1
                        continue

                    cursor = self.conn.execute("""
                        INSERT OR IGNORE INTO producers (
                            permit_id, source, country, state_province,
                            business_name, permit_holder, address, city,
                            postal_code, classification, website, wine_label,
                            latitude, longitude, geocoding_method,
                            verified_wine_producer, enriched_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        permit_id,
                        data.get('source', ''),
                        data.get('country', ''),
                        data.get('state_province'),
                        business_name,
                        data.get('permit_holder'),
                        data.get('address'),
                        data.get('city'),
                        data.get('postal_code'),
                        data.get('classification'),
                        data.get('website'),
                        data.get('wine_label'),
                        data.get('latitude'),
                        data.get('longitude'),
                        data.get('geocoding_method'),
                        data.get('verified_wine_producer', True),
                        data.get('enriched_at')
                    ))

                    if cursor.rowcount == 0:
                        # Producer already exists, skip
                        continue

                    producers_added += 1
                    producer_id = cursor.lastrowid

                    # Insert social media
                    social_media = data.get('social_media', [])
                    if social_media:
                        for url in social_media:
                            if url:
                                self.conn.execute("""
                                    INSERT INTO producer_social_media (producer_id, url)
                                    VALUES (?, ?)
                                """, (producer_id, url))
                                self.stats['social_media_imported'] += 1

                    # Insert activities (if present)
                    activities = data.get('activities', [])
                    if activities:
                        for activity in activities:
                            if activity:
                                self.conn.execute("""
                                    INSERT INTO producer_activities (producer_id, activity)
                                    VALUES (?, ?)
                                """, (producer_id, activity))
                                self.stats['activities_imported'] += 1

                    # Insert wines
                    wines = data.get('wines', [])
                    for wine in wines:
                        wine_name = wine.get('name')
                        if not wine_name:
                            continue

                        wine_cursor = self.conn.execute("""
                            INSERT INTO wines (
                                producer_id, name, description, winemaking, type, vintage
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            producer_id,
                            wine_name,
                            wine.get('description'),
                            wine.get('winemaking'),
                            wine.get('type'),
                            wine.get('vintage')
                        ))

                        wines_added += 1
                        wine_id = wine_cursor.lastrowid

                        # Link grape varieties to wine
                        cepages = wine.get('cepages', [])
                        for grape_name in cepages:
                            if not grape_name:
                                continue

                            # Try to find variety in cache
                            variety_id = variety_cache.get(grape_name.lower())
                            if variety_id:
                                try:
                                    self.conn.execute("""
                                        INSERT OR IGNORE INTO wine_grapes (wine_id, grape_variety_id)
                                        VALUES (?, ?)
                                    """, (wine_id, variety_id))
                                    self.stats['relationships_created'] += 1
                                except Exception as e:
                                    self.log(f"Error linking grape '{grape_name}' to wine: {e}")
                            else:
                                # Grape variety not found - this is expected for some entries
                                self.log(f"Grape variety not found in mapping: {grape_name}")

                except json.JSONDecodeError as e:
                    self.log(f"JSON error on line {line_num}: {e}")
                    self.stats['skipped_records'] += 1
                except Exception as e:
                    self.log(f"Error on line {line_num}: {e}")
                    self.stats['skipped_records'] += 1

        self.stats['producers_imported'] = producers_added
        self.stats['wines_imported'] = wines_added
        print(f"✓ Imported {producers_added:,} producers with {wines_added:,} wines")

    def populate_fts(self):
        """Populate full-text search tables"""
        print("🔍 Populating full-text search indexes...")

        # Populate wines FTS
        self.conn.execute("""
            INSERT INTO wines_fts(rowid, name, description, winemaking)
            SELECT id, name, description, winemaking FROM wines
        """)

        # Populate producers FTS
        self.conn.execute("""
            INSERT INTO producers_fts(rowid, business_name, permit_holder, wine_label, city)
            SELECT id, business_name, permit_holder, wine_label, city FROM producers
        """)

        print("✓ FTS indexes populated")

    def validate(self) -> bool:
        """Run validation queries and return True if all pass"""
        print("✅ Validating database...")

        all_valid = True

        # Check schema version
        result = self.conn.execute(
            "SELECT value FROM schema_info WHERE key = 'version'"
        ).fetchone()
        if result and result[0] == str(self.SCHEMA_VERSION):
            print(f"  ✓ Schema version: {self.SCHEMA_VERSION}")
        else:
            print(f"  ✗ Schema version mismatch")
            all_valid = False

        # Check record counts
        tables = [
            ('producers', self.stats['producers_imported']),
            ('wines', self.stats['wines_imported']),
            ('grape_varieties', self.stats['varieties_imported']),
        ]

        for table, expected in tables:
            result = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            actual = result[0]
            if actual == expected:
                print(f"  ✓ {table}: {actual:,} records")
            else:
                print(f"  ⚠️  {table}: {actual:,} records (expected {expected:,})")

        # Test FTS
        try:
            result = self.conn.execute(
                "SELECT COUNT(*) FROM producers_fts WHERE producers_fts MATCH 'wine'"
            ).fetchone()
            print(f"  ✓ FTS working (found {result[0]:,} matches for 'wine')")
        except Exception as e:
            print(f"  ✗ FTS error: {e}")
            all_valid = False

        # Test relationships
        result = self.conn.execute("""
            SELECT COUNT(*) FROM wine_grapes
            JOIN wines ON wine_grapes.wine_id = wines.id
            JOIN grape_varieties ON wine_grapes.grape_variety_id = grape_varieties.id
        """).fetchone()
        print(f"  ✓ Wine-grape relationships: {result[0]:,}")

        return all_valid

    def print_stats(self):
        """Print comprehensive import statistics"""
        print("\n📈 Import Statistics:")
        print(f"  Grape varieties:    {self.stats['varieties_imported']:,}")
        print(f"  Grape aliases:      {self.stats['aliases_imported']:,}")
        print(f"  Producers:          {self.stats['producers_imported']:,}")
        print(f"  Wines:              {self.stats['wines_imported']:,}")
        print(f"  Wine-grape links:   {self.stats['relationships_created']:,}")
        print(f"  Social media URLs:  {self.stats['social_media_imported']:,}")
        print(f"  Activities:         {self.stats['activities_imported']:,}")

        if self.stats['skipped_records'] > 0:
            print(f"  ⚠️  Skipped records:   {self.stats['skipped_records']:,}")

        if self.stats['warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in self.stats['warnings']:
                print(f"  - {warning}")

        # Database size
        db_size = self.db_path.stat().st_size / (1024 * 1024)  # MB
        print(f"\n💾 Database size: {db_size:.2f} MB")
        print(f"📁 Database path: {self.db_path.absolute()}")

    def build(self, varieties_path: str, producers_path: str):
        """Main build process"""
        # Remove existing database
        if self.db_path.exists():
            print(f"🗑️  Removing existing database: {self.db_path}")
            self.db_path.unlink()

        # Ensure output directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Connect to database
        print(f"🔨 Building database: {self.db_path}")
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        try:
            # Build database
            self.create_schema()
            self.import_grape_varieties(varieties_path)
            self.import_producers(producers_path)
            self.populate_fts()

            # Commit all changes
            self.conn.commit()

            # Validate
            is_valid = self.validate()

            # Print stats
            self.print_stats()

            if is_valid:
                print("\n✅ Database build successful!")
                return True
            else:
                print("\n⚠️  Database build completed with warnings")
                return False

        except Exception as e:
            print(f"\n❌ Error during build: {e}")
            if self.conn:
                self.conn.rollback()
            raise

        finally:
            if self.conn:
                self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Build SQLite database from JSONL source files'
    )
    parser.add_argument(
        '--output',
        default='data/grapegeek.db',
        help='Database output path (default: data/grapegeek.db)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress information'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate existing database and exit (no rebuild)'
    )
    parser.add_argument(
        '--varieties',
        default='data/grape_variety_mapping.jsonl',
        help='Path to grape varieties JSONL (default: data/grape_variety_mapping.jsonl)'
    )
    parser.add_argument(
        '--producers',
        default='data/05_wine_producers_final_normalized.jsonl',
        help='Path to producers JSONL (default: data/05_wine_producers_final_normalized.jsonl)'
    )

    args = parser.parse_args()

    builder = DatabaseBuilder(db_path=args.output, verbose=args.verbose)

    if args.validate:
        # Validate existing database
        if not Path(args.output).exists():
            print(f"❌ Database not found: {args.output}")
            return 1

        builder.conn = sqlite3.connect(args.output)
        builder.conn.row_factory = sqlite3.Row
        try:
            is_valid = builder.validate()
            return 0 if is_valid else 1
        finally:
            builder.conn.close()
    else:
        # Build database
        success = builder.build(args.varieties, args.producers)
        return 0 if success else 1


if __name__ == "__main__":
    exit(main())
