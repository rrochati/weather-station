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
from datetime import datetime, timedelta

LOG_FILE = os.getenv("LOG_FILE", "/home/rrocha/logs/weather_station.log")

LATITUDE = os.getenv("LATITUDE", "38.683822")  # Replace with your LATITUDE
LONGITUDE = os.getenv("LONGITUDE", "-9.149931")  # Replace with your LONGITUDE
API_KEY = os.getenv("API_KEY", "none")  # API key from OpenWeatherMap

WEATHER_UPDATE_INTERVAL_HOURS = 2  # Update weather data every 2 hours
SENSOR_READ_INTERVAL_MINUTES = 1   # Read BME280 every minute

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # This ensures output goes to stdout
        logging.FileHandler(LOG_FILE, mode='a') # Send logs to file
    ]
)

logger = logging.getLogger(__name__)

# CSV file setup
#CSV_FILE = "/home/rrocha/logs/weather_log_trash.csv"

# Initialize file with headers (if new)
#with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
#    writer = csv.writer(f)
#    if f.tell() == 0:  # file empty
#        writer.writerow([
#            "timestamp", "temperature_C", "humidity_%", "pressure_hPa",
#            "altitude", 
#            "wind_speed_m_s", "wind_dir_deg", "wind_vane_voltage_V",
#            "rain_interval_mm"
#        ])


class WeatherStationManager:
    def __init__(self):
        self.current_slp = 1013.25  # Default sea level pressure
        self.last_weather_update = None
        self.bme280 = None
        self.weather_data = None
        
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
                
                self.last_weather_update = datetime.now()
                logger.info("Weather data updated successfully")
                logger.info("%s", print_detailed_weather_data(self.weather_data))
            else:
                logger.error("Failed to fetch weather data, using default sea level pressure")
                
        except Exception as e:
            logger.error("Error updating weather data: %s", e)
            logger.info("Continuing with previous sea level pressure: %.2f hPa", self.current_slp)

    def should_update_weather(self):
        """Check if it's time to update weather data"""
        if self.last_weather_update is None:
            return True
        
        time_since_update = datetime.now() - self.last_weather_update
        return time_since_update >= timedelta(hours=WEATHER_UPDATE_INTERVAL_HOURS)
    
    def log_initial_air_quality(self):
        """Log air quality once at startup"""
        try:
            logger.info("Fetching initial air quality data...")
            air_quality = get_air_quality(API_KEY, LATITUDE, LONGITUDE)
            
            if air_quality:
                logger.info("=== INITIAL AIR QUALITY DATA ===")
                logger.info("Air Quality Index: %s", air_quality['air_quality_index'])
                logger.info("CO: %s μg/m³", air_quality['co'])
                logger.info("NO2: %s μg/m³", air_quality['no2'])
                logger.info("O3: %s μg/m³", air_quality['o3'])
                logger.info("PM2.5: %s μg/m³", air_quality['pm2_5'])
                logger.info("PM10: %s μg/m³", air_quality['pm10'])
                logger.info("================================")
            else:
                logger.warning("Could not fetch air quality data")
                
        except Exception as e:
            logger.error("Error fetching initial air quality data: %s", e)
    
#    def initialize_csv(self):
#        """Initialize CSV file with headers if new"""
#        try:
#            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
#                writer = csv.writer(f)
#                if f.tell() == 0:  # file empty
#                    writer.writerow([
#                        "timestamp", "temperature_C", "humidity_%", "pressure_hPa",
#                        "altitude_m", "sea_level_pressure_hPa"
#                    ])
#                    logger.info(f"Created CSV file: {CSV_FILE}")
#        except Exception as e:
#            logger.error(f"Error initializing CSV: {e}")

    def run(self):
        """Main monitoring loop"""
        if not self.initialize_sensor():
            logger.fatal("Failed to initialize sensor. Exiting.")
            return
        
        # Initialize database
        logger.info("Initializing database...")
        db = WeatherDatabase()

        # Print database stats
        stats = db.get_database_stats()
        logger.info("Database stats: %s", stats)
        
        # Initialize CSV file
        #self.initialize_csv()
        
        # Log initial air quality (only once at startup)
        self.log_initial_air_quality()
        
        logger.info("=== WEATHER STATION CONFIGURATION ===")
        logger.info(f"Weather data updates: every {WEATHER_UPDATE_INTERVAL_HOURS} hours")
        logger.info(f"Sensor readings: every {SENSOR_READ_INTERVAL_MINUTES} minute(s)")
        #logger.info(f"CSV log file: {CSV_FILE}")
        logger.info("====================================")
        
        logger.info("Starting weather station monitoring...")
        
        reading_count = 0
        
        while True:
            try:
                # Update weather data and sea level pressure if needed
                if self.should_update_weather():
                    self.update_weather_data()
                
                # Read sensor data
                temperature = self.bme280.temperature
                humidity = self.bme280.humidity
                pressure = self.bme280.pressure
                altitude = self.bme280.altitude
                
                reading_count += 1
                
                # Log sensor readings (simplified output for continuous monitoring)
                logger.info(f"Reading #{reading_count}: T={temperature:.2f}°C, H={humidity:.2f}%, P={pressure:.2f}hPa, Alt={altitude:.1f}m (SLP={self.current_slp:.2f}hPa)")
                
                # Write to CSV
                #self.write_to_csv(temperature, humidity, pressure, altitude)
                
                #Save sensor data to database
                timestamp = datetime.now().isoformat(timespec='seconds')
                
                # Calculate time until next weather update
                if self.last_weather_update:
                    time_since_update = datetime.now() - self.last_weather_update
                    time_until_next_update = timedelta(hours=WEATHER_UPDATE_INTERVAL_HOURS) - time_since_update
                    hours_remaining = time_until_next_update.total_seconds() / 3600
                    
                    # Log weather update countdown every 30 readings (30 minutes)
                    if reading_count % 30 == 0:
                        logger.info(f"Next weather update in {hours_remaining:.1f} hours")
                
                # Wait for next reading
                time.sleep(SENSOR_READ_INTERVAL_MINUTES * 60)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received. Stopping weather station...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.info("Retrying in 30 seconds...")
                time.sleep(30)  # Wait before retrying
        
        logger.info("Weather station stopped.")

if __name__ == "__main__":
    logger.info("Starting Weather Station Manager...")
    station = WeatherStationManager()
    station.run()