#!/usr/bin/env python3
"""
Test script to verify SQLite database functionality
"""

import sqlite3
import os
from datetime import datetime
from modules.database import WeatherDatabase

def test_database():
    print("Testing SQLite database functionality...")
    
    # Test basic SQLite connection
    try:
        conn = sqlite3.connect(':memory:')  # In-memory database for testing
        cursor = conn.cursor()
        cursor.execute('SELECT sqlite_version()')
        version = cursor.fetchone()[0]
        print(f"✓ SQLite version: {version}")
        conn.close()
    except Exception as e:
        print(f"✗ SQLite test failed: {e}")
        return False
    
    # Test WeatherDatabase class
    try:
        # Use test database
        db = WeatherDatabase("test_weather.db")
        
        # Test inserting data
        timestamp = datetime.now().isoformat()
        success = db.insert_weather_reading(
            timestamp=timestamp,
            temperature=22.5,
            humidity=65.0,
            pressure=1013.25,
            altitude=100.0,
            sea_level_pressure=1013.25
        )
        
        if success:
            print("✓ Weather reading inserted successfully")
        else:
            print("✗ Failed to insert weather reading")
            return False
        
        # Test getting stats
        stats = db.get_database_stats()
        print(f"✓ Database stats: {stats}")
        
        # Test getting recent readings
        readings = db.get_recent_readings(24)
        print(f"✓ Found {len(readings)} recent readings")
        
        # Clean up test database
        if os.path.exists("test_weather.db"):
            os.remove("test_weather.db")
            print("✓ Test database cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ WeatherDatabase test failed: {e}")
        return False

if __name__ == "__main__":
    if test_database():
        print("\n✓ All database tests passed!")
    else:
        print("\n✗ Database tests failed!")