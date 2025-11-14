import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
import sys

LOG_FILE=os.getenv('LOG_FILE', '/home/rrocha/logs/weather_station.log')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),  # This ensures output goes to stdout
        logging.FileHandler(LOG_FILE, mode='a') # Send logs to file
    ]
)
logger = logging.getLogger(__name__)

DB_FILE = os.getenv("DB_FILE", "/home/rrocha/data/weather_data.db")

class WeatherDatabase:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create weather_readings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS weather_readings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        sensor_temperature REAL,
                        sensor_humidity REAL,
                        sensor_pressure REAL,
                        sensor_altitude REAL,
                        sensor_wind_speed REAL,
                        sensor_wind_direction REAL,
                        sensor_wind_direction_name TEXT,
                        sensor_wind_vane_voltage REAL,
                        sensor_rain_interval REAL,
                        sea_level_pressure REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create weather_api_data table for OpenWeatherMap data
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS weather_api_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        api_location TEXT,
                        api_country TEXT,
                        api_temperature REAL,
                        api_feels_like REAL,
                        api_humidity REAL,
                        api_pressure REAL,
                        api_sea_level_pressure REAL,
                        api_ground_level_pressure REAL,
                        api_visibility REAL,
                        api_wind_speed REAL,
                        api_wind_direction REAL,
                        api_cloudiness REAL,
                        api_weather_description TEXT,
                        api_sunrise TEXT,
                        api_sunset TEXT,
                        api_timezone_offset REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create air_quality table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS air_quality (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        api_aqi INTEGER,
                        api_co REAL,
                        api_no2 REAL,
                        api_o3 REAL,
                        api_pm2_5 REAL,
                        api_pm10 REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better query performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather_readings(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_timestamp ON weather_api_data(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_air_quality_timestamp ON air_quality(timestamp)')
                
                conn.commit()
                logger.info(f"Database initialized successfully at {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def insert_weather_reading(
        self, 
        timestamp: str, 
        temperature: float, 
        humidity: float, 
        pressure: float, 
        altitude: float,
        sea_level_pressure: float,
        wind_speed: Optional[float] = None,
        wind_direction: Optional[float] = None,
        wind_direction_name: Optional[str] = None,
        wind_vane_voltage: Optional[float] = None,
        rain_interval: Optional[float] = None ) -> bool:
        """Insert a weather reading into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO weather_readings 
                    (timestamp, sensor_temperature, sensor_humidity, sensor_pressure, sensor_altitude,
                     sensor_wind_speed, sensor_wind_direction, sensor_wind_direction_name, sensor_wind_vane_voltage, sensor_rain_interval,
                     sea_level_pressure)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (timestamp, temperature, humidity, pressure, altitude,
                      wind_speed, wind_direction, wind_direction_name, wind_vane_voltage, rain_interval,
                      sea_level_pressure))
                conn.commit()
                #logger.info(f"Weather reading saved: T={temperature:.1f}°C, H={humidity:.1f}%, P={pressure:.1f}hPa, SLP={sea_level_pressure:.1f}hPa, Alt={altitude:.1f}m, Wind Speed={wind_speed:.1f} knots, Wind Dir={wind_direction}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error inserting weather reading: {e}")
            return False
    
    def insert_api_weather_data(self, timestamp: str, weather_data: Dict[str, Any]) -> bool:
        """Insert API weather data into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO weather_api_data
                    (timestamp, api_location, api_country, api_temperature ,
                     api_feels_like, api_humidity, api_pressure, api_sea_level_pressure,
                     api_ground_level_pressure, api_visibility, api_wind_speed, api_wind_direction,
                     api_cloudiness, api_weather_description, api_sunrise, api_sunset,
                     api_timezone_offset)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    weather_data.get('location'),
                    weather_data.get('country'),
                    weather_data.get('temperature'),
                    weather_data.get('feels_like'),
                    weather_data.get('humidity'),
                    weather_data.get('pressure'),
                    weather_data.get('sea_level_pressure'),
                    weather_data.get('ground_level_pressure'),
                    weather_data.get('visibility'),
                    weather_data.get('wind_speed'),
                    weather_data.get('wind_direction'),
                    weather_data.get('cloudiness'),
                    weather_data.get('weather_description'),
                    weather_data.get('sunrise'),
                    weather_data.get('sunset'),
                    weather_data.get('timezone_offset')
                ))
                conn.commit()
                logger.info("API weather data saved")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error inserting API weather data: {e}")
            return False
    
    def insert_air_quality_data(self, timestamp: str, air_quality_data: Dict[str, Any]) -> bool:
        """Insert air quality data into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO air_quality
                    ( timestamp, api_aqi, api_co, api_no2,
                     api_o3, api_pm2_5, api_pm10)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    air_quality_data.get('air_quality_index'),
                    air_quality_data.get('co'),
                    air_quality_data.get('no2'),
                    air_quality_data.get('o3'),
                    air_quality_data.get('pm2_5'),
                    air_quality_data.get('pm10')
                ))
                conn.commit()
                logger.info("Air Quality data saved to DB successfully.")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error inserting air quality data: {e}")
            return False
    
    def get_recent_readings(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent weather readings from the last N hours."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM weather_readings 
                    WHERE datetime(timestamp) >= datetime('now', '-{} hours')
                    ORDER BY timestamp DESC
                '''.format(hours))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error getting recent readings: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records in each table
                cursor.execute('SELECT COUNT(*) FROM weather_readings')
                weather_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM weather_api_data')
                api_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM air_quality')
                air_quality_count = cursor.fetchone()[0]
                
                # Get date range
                cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM weather_readings')
                date_range = cursor.fetchone()
                
                return {
                    'weather_readings': weather_count,
                    'api_data_records': api_count,
                    'air_quality_records': air_quality_count,
                    'earliest_reading': date_range[0],
                    'latest_reading': date_range[1],
                    'database_size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
                }
        except sqlite3.Error as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
