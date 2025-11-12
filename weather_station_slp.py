import time
import csv
from datetime import datetime, timedelta
import logging
import sys
import os
import board # pyright: ignore[reportMissingImports]
import busio # pyright: ignore[reportMissingImports]
from adafruit_bme280 import basic as adafruit_bme280 # pyright: ignore[reportMissingImports]
from modules.openweathermap import get_current_sea_level_pressure, get_air_quality, get_detailed_weather_data
from modules.openweathermap import print_detailed_weather_data, print_air_quality
from modules.database import WeatherDatabase
from modules.anemometer import start_gpio, measure_wind_speed
from datetime import datetime, timedelta

# Configure logging
LOG_FILE = os.getenv('LOG_FILE', '/home/rrocha/logs/weather_station.log')
# Create log directory if it doesn't exist
log_dir = os.path.dirname(LOG_FILE)
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),  # This ensures output goes to stdout
        logging.FileHandler(LOG_FILE, mode='a', delay=False) # Send logs to file
    ]
)
logger = logging.getLogger(__name__)


LATITUDE = os.getenv("LATITUDE", "38.683822")  # Replace with your LATITUDE
LONGITUDE = os.getenv("LONGITUDE", "-9.149931")  # Replace with your LONGITUDE
API_KEY = os.getenv("API_KEY", "none")  # API key from OpenWeatherMap

WEATHER_UPDATE_INTERVAL_HOURS = 2  # Update weather data every 2 hours
SENSOR_READ_INTERVAL_MINUTES = 1   # Read BME280 every minute

class WeatherStationManager:
    def __init__(self):
        self.current_slp = 1013.25  # Default sea level pressure
        self.last_weather_update = None
        self.bme280 = None
        self.weather_data = None
        # Define fixed update times (hours in 24h format)
        self.update_hours = [0, 6, 12, 18]  # 00:00, 06:00, 12:00, 18:00
        
        # Initialize database
        logger.info("Initializing database...")
        self.db = WeatherDatabase()
        
    def get_next_update_time(self):
        """Calculate the next scheduled update time"""
        now = datetime.now()
        today = now.date()
        
        # Find the next update time today
        for hour in self.update_hours:
            next_update = datetime.combine(today, datetime.min.time().replace(hour=hour))
            if next_update > now:
                return next_update
        
        # If no more updates today, get the first update time tomorrow
        tomorrow = today + timedelta(days=1)
        return datetime.combine(tomorrow, datetime.min.time().replace(hour=self.update_hours[0]))
    
    def should_update_weather(self):
        """Check if it's time to update weather data based on fixed schedule"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        # Check if we're within the first 5 minutes of an update hour
        if current_hour in self.update_hours and current_minute < 5:
            # Check if we haven't updated in the last hour to avoid duplicate updates
            if self.last_weather_update is None:
                return True
            
            time_since_update = now - self.last_weather_update
            return time_since_update >= timedelta(hours=1)
        
        return False
    
    def get_time_until_next_update(self):
        """Get human-readable time until next weather update"""
        next_update = self.get_next_update_time()
        now = datetime.now()
        time_diff = next_update - now
        
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}m", next_update
    
    def initialize_sensor(self):
        """Initialize BME280 sensor"""
        try:
            logger.info("Initializing I2C...")
            i2c = busio.I2C(board.SCL, board.SDA)
            
            logger.info("Connecting to BME280...")
            self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
            
            # Get initial weather data and sea level pressure
            self.update_weather_data()
            
            logger.info("BME280 initialized successfully!")
            return True
            
        except Exception as e:
            logger.fatal("Error initializing BME280: %s", e)
            logger.fatal("\nTroubleshooting tips:")
            logger.fatal("1. Check I2C wiring")
            logger.fatal("2. Run 'i2cdetect -y 1' to verify sensor is detected")
            logger.fatal("3. Make sure I2C is enabled in raspi-config")
            return False
    
    def update_weather_data(self):
        """Update weather data and sea level pressure from OpenWeatherMap API"""
        try:
            logger.info("Fetching updated weather data from OpenWeatherMap...")
            self.weather_data = get_detailed_weather_data(API_KEY, LATITUDE, LONGITUDE)
            
            if self.weather_data:
                self.current_slp = self.weather_data['sea_level_pressure']
                
                if self.bme280:
                    self.bme280.sea_level_pressure = self.current_slp
                
                success = self.db.insert_api_weather_data(
                    timestamp=datetime.now().isoformat(timespec='seconds'),
                    weather_data=self.weather_data
                )
                
                if not success:
                    logger.warning("Failed to save api reading to database")
                
                self.last_weather_update = datetime.now()
                logger.info("Weather data updated successfully at %s", self.last_weather_update.strftime('%H:%M:%S'))
                #logger.info("%s", print_detailed_weather_data(self.weather_data))
                
                # Log next update time
                time_until_next, next_update_time = self.get_time_until_next_update()
                logger.info("Next weather update scheduled for: %s (in %s)", 
                           next_update_time.strftime('%H:%M'), time_until_next)
            else:
                logger.error("Failed to fetch weather data, using default sea level pressure")
                
        except Exception as e:
            logger.error("Error updating weather data: %s", e)
            logger.info("Continuing with previous sea level pressure: %.2f hPa", self.current_slp)

    def log_initial_air_quality(self):
        """Log air quality once at startup"""
        try:
            logger.info("Fetching initial air quality data...")
            air_quality = get_air_quality(API_KEY, LATITUDE, LONGITUDE)
            
            if air_quality:
                try:
                    self.db.insert_air_quality_data(
                        timestamp=datetime.now().isoformat(timespec='seconds'),
                        air_quality_data=air_quality
                    )

                except Exception as e:
                    logger.error("Error inserting air quality data into database: %s", e)
            else:
                logger.warning("Could not fetch air quality data")
                
        except Exception as e:
            logger.error("Error fetching initial air quality data: %s", e)


    def run(self):
        """Main monitoring loop"""
        if not self.initialize_sensor():
            logger.fatal("Failed to initialize sensor. Exiting.")
            return
        
        # Print database stats
        stats = self.db.get_database_stats()
        logger.info("Database stats: %s", stats)
        
        # Log initial air quality (only once at startup)
        self.log_initial_air_quality()
        
        logger.info("=== WEATHER STATION CONFIGURATION ===")
        logger.info("Weather data updates: 4 times daily at 00:00, 06:00, 12:00, 18:00")
        logger.info(f"Sensor readings: every {SENSOR_READ_INTERVAL_MINUTES} minute(s)")
        
        # Show next update time
        time_until_next, next_update_time = self.get_time_until_next_update()
        logger.info("Next weather update: %s (in %s)", 
                   next_update_time.strftime('%Y-%m-%d %H:%M'), time_until_next)
        logger.info("====================================")
        
        logger.info("Starting weather station monitoring...")
        
        reading_count = 0
        
        start_gpio()
        wind_read_interval = 60  # seconds
        
        while True:
            try:
                # Update weather data if it's time
                if self.should_update_weather():
                    self.update_weather_data()
                
                # Read sensor data
                temperature = self.bme280.temperature
                humidity = self.bme280.humidity
                pressure = self.bme280.pressure
                altitude = self.bme280.altitude
                
                speed, total_pulses = measure_wind_speed(wind_read_interval)
                
                reading_count += 1
                
                # Log sensor readings
                logger.info(f"Reading #{reading_count}: T={temperature:.2f}°C, H={humidity:.2f}%, P={pressure:.2f}hPa, Alt={altitude:.1f}m (SLP={self.current_slp:.2f}hPa)")
                logger.info(f"Wind: {speed:.2f} m/s ({speed*3.6:.1f} km/h, {speed*2.237:.1f} mph, {speed*1.944:.1f} knots), Pulses: {total_pulses} in last interval")
                
                # Save sensor data to database
                timestamp = datetime.now().isoformat(timespec='seconds')
                success = self.db.insert_weather_reading(
                    timestamp=timestamp,
                    temperature=temperature,
                    humidity=humidity,
                    pressure=pressure,
                    altitude=altitude,
                    sea_level_pressure=self.current_slp,
                    wind_speed=speed*1.944,  # Convert m/s to knots
                )
                
                if not success:
                    logger.warning("Failed to save reading to database")
                
                # Log next weather update info every 30 readings (30 minutes)
                if reading_count % 30 == 0:
                    time_until_next, next_update_time = self.get_time_until_next_update()
                    logger.info("Next weather update: %s (in %s)", 
                               next_update_time.strftime('%H:%M'), time_until_next)
                
                # Wait for next reading
                time.sleep(SENSOR_READ_INTERVAL_MINUTES * 60)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received. Stopping weather station...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.info("Retrying in 30 seconds...")
                time.sleep(30)
        
        logger.info("Weather station stopped.")

if __name__ == "__main__":
    logger.info("Starting Weather Station Manager...")
    station = WeatherStationManager()
    station.run()