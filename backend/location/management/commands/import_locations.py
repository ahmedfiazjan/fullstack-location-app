import logging
from contextlib import closing
from typing import Dict, List, Any
import sqlite3
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.db.models import Model
from location.models import Country, State, City, Location
from tqdm import tqdm
import os
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import location data from SQLite database efficiently'

    BATCH_SIZE = 10000  # Increased batch size for better performance
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.models_map: Dict[str, Dict[int, Model]] = {
            'countries': {},
            'states': {},
            'cities': {},
        }

    def add_arguments(self, parser):
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'allcountries.sqlite3')
        parser.add_argument(
            '--database-path',
            type=str,
            default=path,
            help='Path to SQLite database file'
        )

    def disable_indexes(self):
        """Temporarily disable indexes for faster bulk insertion"""
        with connection.cursor() as cursor:
            cursor.execute('DROP INDEX IF EXISTS location_location_zip_code_idx;')
            cursor.execute('DROP INDEX IF EXISTS location_location_city_id_idx;')

    def enable_indexes(self):
        """Re-enable indexes after import"""
        with connection.cursor() as cursor:
            cursor.execute('CREATE INDEX location_location_zip_code_idx ON location_location(zip_code);')
            cursor.execute('CREATE INDEX location_location_city_id_idx ON location_location(city_id);')

    def bulk_create_with_progress(self, model_class: Model, objects: List[Any], 
                                desc: str) -> None:
        """Bulk create objects with progress bar"""
        total_objects = len(objects)
        created_objects = []
        
        with tqdm(total=total_objects, desc=desc) as pbar:
            for i, obj in enumerate(objects, 1):
                created_objects.append(obj)
                
                if i % self.BATCH_SIZE == 0 or i == total_objects:
                    model_class.objects.bulk_create(created_objects)
                    pbar.update(len(created_objects))
                    created_objects = []

    def import_data(self, source_cursor: sqlite3.Cursor) -> None:
        """Import data from source database with optimized batching"""
        
        # Import countries
        logger.info("Importing countries...")
        source_cursor.execute('SELECT id, name, alpha2, alpha3, iso FROM countries')
        country_batch = []
        for row in source_cursor.fetchall():
            country = Country(
                name=row[1],
                alpha2=row[2] if row[2] else '',
                alpha3=row[3] if row[3] else ''
            )
            country_batch.append(country)
            self.models_map['countries'][row[0]] = country
        self.bulk_create_with_progress(Country, country_batch, "Importing countries")

        # Import states
        logger.info("Importing states...")
        source_cursor.execute('''
            SELECT id, name, country_id, abbr 
            FROM states 
            ORDER BY country_id
        ''')
        state_batch = []
        for row in source_cursor.fetchall():
            try:
                state = State(
                    name=row[1],
                    country=self.models_map['countries'][row[2]],
                    abbreviation=row[3] if row[3] else ''
                )
                state_batch.append(state)
                self.models_map['states'][row[0]] = state
            except KeyError:
                logger.warning(f"Country not found for state: {row[1]}")
                continue
        self.bulk_create_with_progress(State, state_batch, "Importing states")

        # Import cities from zipcodes table
        logger.info("Importing cities...")
        source_cursor.execute('''
            SELECT DISTINCT city, state_id 
            FROM zipcodes 
            WHERE city IS NOT NULL 
              AND state_id IS NOT NULL 
              AND city != ''
            ORDER BY state_id, city
        ''')
        city_batch = []
        city_cache = set()  # To prevent duplicates
        
        for row in source_cursor.fetchall():
            city_name = row[0]
            state_id = row[1]
            
            try:
                # Create unique key for city+state combination
                cache_key = f"{city_name}_{state_id}"
                if cache_key in city_cache:
                    continue
                
                city = City(
                    name=city_name,
                    state=self.models_map['states'][state_id]
                )
                city_batch.append(city)
                city_cache.add(cache_key)
            except KeyError:
                logger.warning(f"State not found for city: {city_name}")
                continue
            
        self.bulk_create_with_progress(City, city_batch, "Importing cities")

        # Create a mapping of city names to City objects for location import
        city_map = {(city.name, city.state_id): city for city in City.objects.all()}

        # Import locations from zipcodes table
        logger.info("Importing locations...")
        source_cursor.execute('''
            SELECT code, city, state_id, lat, lon, area_code 
            FROM zipcodes 
            WHERE city IS NOT NULL 
              AND state_id IS NOT NULL 
              AND code IS NOT NULL
              AND city != ''
            ORDER BY state_id, city
        ''')
        
        location_batch = []
        total_locations = 0
        
        with tqdm(desc="Importing locations") as pbar:
            while True:
                rows = source_cursor.fetchmany(self.BATCH_SIZE)
                if not rows:
                    break
                    
                for row in rows:
                    try:
                        zip_code = row[0]
                        city_name = row[1]
                        state_id = row[2]
                        state = self.models_map['states'][state_id]
                        
                        city = city_map.get((city_name, state_id))
                        if city is None:
                            logger.warning(f"City not found: {city_name}, {state_id}")
                            continue

                        location = Location(
                            city=city,
                            state=state,
                            country=state.country,
                            zip_code=zip_code,
                            latitude=row[3],
                            longitude=row[4]
                        )
                        location_batch.append(location)
                        total_locations += 1
                    except (KeyError, IndexError) as e:
                        logger.warning(f"Error processing zipcode row: {row} - {str(e)}")
                        continue
                
                if location_batch:
                    Location.objects.bulk_create(location_batch)
                    pbar.update(len(location_batch))
                    location_batch = []

        logger.info(f"Imported {total_locations} locations")

    def validate_database(self, cursor: sqlite3.Cursor) -> bool:
        """Validate that the database has all required tables and columns"""
        required_tables = {
            'countries': ['id', 'alpha2', 'alpha3', 'iso', 'name'],
            'states': ['id', 'country_id', 'abbr', 'name'],
            'counties': ['id', 'state_id', 'abbr', 'name', 'county_seat'],
            'zipcodes': ['id', 'code', 'state_id', 'city', 'area_code', 'lat', 'lon', 'accuracy']
        }

        # Get list of tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = {row[0] for row in cursor.fetchall()}

        for table, columns in required_tables.items():
            if table not in existing_tables:
                self.stderr.write(self.style.ERROR(
                    f"Missing required table: {table}"
                ))
                return False

            # Check columns in each table
            cursor.execute(f"PRAGMA table_info({table});")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            missing_columns = set(columns) - existing_columns
            if missing_columns:
                self.stderr.write(self.style.ERROR(
                    f"Missing columns in {table}: {', '.join(missing_columns)}"
                ))
                return False

        return True

    def handle(self, *args, **options):
        start_time = time.time()
        database_path = options['database_path']
        
        # Check if database file exists
        if not os.path.exists(database_path):
            self.stderr.write(self.style.ERROR(
                f"Database file not found: {database_path}"
            ))
            return

        try:
            # Connect to source database using context manager
            with closing(sqlite3.connect(database_path)) as source_db, \
                 closing(source_db.cursor()) as source_cursor:
                
                # Validate database structure
                if not self.validate_database(source_cursor):
                    self.stderr.write(self.style.ERROR(
                        "Database validation failed. Please check the database structure."
                    ))
                    return

                # Set pragmas for better SQLite performance
                source_cursor.execute('PRAGMA cache_size = -2000000')  # 2GB cache
                source_cursor.execute('PRAGMA temp_store = MEMORY')
                source_cursor.execute('PRAGMA synchronous = OFF')
                source_cursor.execute('PRAGMA journal_mode = MEMORY')
                
                # Disable indexes temporarily
                self.disable_indexes()
                
                try:
                    # Import all data in a single transaction
                    with transaction.atomic():
                        self.import_data(source_cursor)
                    
                    # Re-enable indexes
                    self.enable_indexes()
                    
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'Data import completed successfully in {elapsed_time:.2f} seconds'
                    ))
                except Exception as e:
                    # Make sure indexes are re-enabled even if import fails
                    self.enable_indexes()
                    raise
                
        except sqlite3.Error as e:
            self.stderr.write(self.style.ERROR(
                f"SQLite error: {str(e)}"
            ))
            logger.error(f"SQLite error: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"Import failed: {str(e)}"
            ))
            logger.error(f"Import failed: {str(e)}", exc_info=True)
            raise