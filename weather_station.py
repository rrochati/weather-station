import time
import csv
from datetime import datetime, timedelta
import logging
import sys
import board # pyright: ignore[reportMissingImports]
import busio # pyright: ignore[reportMissingImports]
from adafruit_bme280 import basic as adafruit_bme280 # pyright: ignore[reportMissingImports]
from modules.openweathermap import get_detailed_weather_data, get_air_quality, print_air_quality

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Configuration
LATITUDE = 38.683822
LONGITUDE = -9.149931
API_KEY = "12a5ff2b1dcb41f0d1ee2c301244ad6d"
CSV_FILE = "../weather_log.csv"

# Update intervals (configurable)
WEATHER_UPDATE_INTERVAL_HOURS = 2  # Update weather data every 2 hours
SENSOR_READ_INTERVAL_MINUTES = 1   # Read BME280 every minute

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
            logger.error(f"Error initializing BME280: {e}")
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
                logger.info(f"Weather data updated successfully")
                logger.info(f"Sea level pressure updated: {self.current_slp:.2f} hPa")
                logger.info(f"Location: {self.weather_data['location']}, {self.weather_data['country']}")
                logger.info(f"Current weather: {self.weather_data['weather_description'].title()}")
                logger.info(f"Temperature: {self.weather_data['temperature']:.1f}°C")
                logger.info(f"Humidity: {self.weather_data['humidity']}%")
                logger.info(f"Wind: {self.weather_data['wind_speed']:.1f} m/s")
            else:
                logger.error("Failed to fetch weather data, using default sea level pressure")
                
        except Exception as e:
            logger.error(f"Error updating weather data: {e}")
            logger.info(f"Continuing with previous sea level pressure: {self.current_slp:.2f} hPa")
    
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
                logger.info(f"Air Quality Index: {air_quality['air_quality_index']}")
                logger.info(f"CO: {air_quality['co']} μg/m³")
                logger.info(f"NO2: {air_quality['no2']} μg/m³")
                logger.info(f"O3: {air_quality['o3']} μg/m³")
                logger.info(f"PM2.5: {air_quality['pm2_5']} μg/m³")
                logger.info(f"PM10: {air_quality['pm10']} μg/m³")
                logger.info("================================")
                
                # Also print using the existing function for formatted output
                print_air_quality(air_quality)
            else:
                logger.warning("Could not fetch air quality data")
                
        except Exception as e:
            logger.error(f"Error fetching initial air quality data: {e}")
    
    def initialize_csv(self):
        """Initialize CSV file with headers if new"""
        try:
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if f.tell() == 0:  # file empty
                    writer.writerow([
                        "timestamp", "temperature_C", "humidity_%", "pressure_hPa",
                        "altitude_m", "sea_level_pressure_hPa"
                    ])
                    logger.info(f"Created CSV file: {CSV_FILE}")
        except Exception as e:
            logger.error(f"Error initializing CSV: {e}")
    
    def write_to_csv(self, temperature, humidity, pressure, altitude):
        """Write sensor data to CSV file"""
        try:
            timestamp = datetime.now().isoformat(timespec='seconds')
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, 
                    round(temperature, 2), 
                    round(humidity, 2), 
                    round(pressure, 2),
                    round(altitude, 1), 
                    round(self.current_slp, 2)
                ])
                logger.debug(f"Data written to CSV: T={temperature:.2f}°C, H={humidity:.2f}%, P={pressure:.2f}hPa")
        except Exception as e:
            logger.error(f"Error writing to CSV: {e}")
    
    def run(self):
        """Main monitoring loop"""
        if not self.initialize_sensor():
            logger.fatal("Failed to initialize sensor. Exiting.")
            return
        
        # Initialize CSV file
        self.initialize_csv()
        
        # Log initial air quality (only once at startup)
        self.log_initial_air_quality()
        
        logger.info("=== WEATHER STATION CONFIGURATION ===")
        logger.info(f"Weather data updates: every {WEATHER_UPDATE_INTERVAL_HOURS} hours")
        logger.info(f"Sensor readings: every {SENSOR_READ_INTERVAL_MINUTES} minute(s)")
        logger.info(f"CSV log file: {CSV_FILE}")
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
                self.write_to_csv(temperature, humidity, pressure, altitude)
                
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
