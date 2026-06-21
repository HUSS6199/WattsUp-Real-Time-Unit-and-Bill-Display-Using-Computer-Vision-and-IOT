"""Initialize database for Weather Dashboard."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'weather_dashboard.db'


def init_database():
    """
    Initialize SQLite database with required tables.
    """
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Create locations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            latitude REAL,
            longitude REAL,
            is_favorite BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, country)
        )
    ''')
    
    # Create weather cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER,
            data TEXT NOT NULL,
            cache_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(location_id) REFERENCES locations(id)
        )
    ''')
    
    # Create alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            severity TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(location_id) REFERENCES locations(id)
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_locations_name ON locations(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_locations_favorite ON locations(is_favorite)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_cache_location ON weather_cache(location_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_location ON alerts(location_id)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at {DB_PATH}")


if __name__ == '__main__':
    init_database()
