import time
import csv
from datetime import datetime
import logging
import sys
import board # pyright: ignore[reportMissingImports]
import busio # pyright: ignore[reportMissingImports]
from adafruit_bme280 import basic as adafruit_bme280 # pyright: ignore[reportMissingImports]
from modules.openweathermap import get_current_sea_level_pressure, get_air_quality, get_detailed_weather_data
from modules.openweathermap import print_detailed_weather_data, print_air_quality
from modules.database import WeatherDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # This ensures output goes to stdout
    ]
)

logger = logging.getLogger(__name__)

# Your location coordinates
LATITUDE = 38.683822  # Replace with your LATITUDE
LONGITUDE = -9.149931  # Replace with your LONGITUDE
API_KEY = "12a5ff2b1dcb41f0d1ee2c301244ad6d"  # API key from OpenWeatherMap

# Initialize database
logger.info("Initializing database...")
db = WeatherDatabase()

# Get current conditions from API
logger.info("Fetching current weather conditions from OpenWeatherMap...")

#current_slp = get_current_sea_level_pressure(API_KEY, LATITUDE, LONGITUDE)
try:
    detailed_weather_data = get_detailed_weather_data(API_KEY, LATITUDE, LONGITUDE)
except Exception as e:
    logger.error(f"Error fetching detailed weather data from api: {e}")
    detailed_weather_data = None
    
try:
    air_quality = get_air_quality(API_KEY, LATITUDE, LONGITUDE)
except Exception as e:
    logger.error(f"Error fetching air quality data from api: {e}")
    air_quality = None
    
current_slp = detailed_weather_data['sea_level_pressure'] if detailed_weather_data else 1013.25  # Use current pressure as sea level pressure or fallback

if detailed_weather_data:
    print_detailed_weather_data(detailed_weather_data)
    # Save API weather data to database
    timestamp = datetime.now().isoformat(timespec='seconds')
    db.insert_api_weather_data(timestamp, detailed_weather_data)

if air_quality:
    print_air_quality(air_quality)
    # Save air quality data to database
    timestamp = datetime.now().isoformat(timespec='seconds')
    logger.info(f"Saving air quality data with timestamp: {timestamp}")
    logger.info(f"Air quality data structure: {air_quality}")
    success = db.insert_air_quality_data(timestamp, air_quality)
    if not success:
        logger.error("Failed to save air quality data to database")


# CSV file setup
CSV_FILE = "/home/rrocha/logs/weather_log_trash.csv"

# Initialize file with headers (if new)
with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if f.tell() == 0:  # file empty
        writer.writerow([
            "timestamp", "temperature_C", "humidity_%", "pressure_hPa",
            "altitude", 
            "wind_speed_m_s", "wind_dir_deg", "wind_vane_voltage_V",
            "rain_interval_mm"
        ])

try:
    # I2C setup
    logger.info("Initializing I2C...")
    i2c = busio.I2C(board.SCL, board.SDA)

    logger.info("Connecting to BME280...")
    # Correct class name for the newer library version
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

    # Update sea level pressure
    bme280.sea_level_pressure = current_slp

    logger.info(f"Current sea level pressure: {current_slp:.4f} hPa")

    logger.info("BME280 initialized successfully!")
    
    # Print database stats
    stats = db.get_database_stats()
    logger.info(f"Database stats: {stats}")
    
    logger.info("Starting readings...\n")

    while True:
        try:
            temperature = bme280.temperature
            humidity = bme280.humidity
            pressure = bme280.pressure
            altitude = bme280.altitude

            timestamp = datetime.now().isoformat(timespec='seconds')
            
            # Save to SQLite database (primary storage)
            success = db.insert_weather_reading(
                timestamp=timestamp,
                temperature=temperature,
                humidity=humidity,
                pressure=pressure,
                altitude=altitude,
                sea_level_pressure=current_slp
            )
            
            if not success:
                logger.warning("Failed to save to database, continuing...")

            # Also write to CSV for backup/compatibility
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, temperature, humidity, pressure, round(altitude, 1)])


            time.sleep(60)

        except KeyboardInterrupt:
            print("\nStopping readings...")
            logger.info("\nStopping readings...")
            # Print final database stats
            final_stats = db.get_database_stats()
            logger.info(f"Final database stats: {final_stats}")
            break
        except Exception as e:
            print(f"Error reading sensor: {e}")
            logger.info(f"Error reading sensor: {e}")
            time.sleep(1)

except Exception as e:
    logger.fatal(f"Error initializing BME280: {e}")
    logger.fatal("\nTroubleshooting tips:")
    logger.fatal("1. Check I2C wiring")
    logger.fatal("2. Run 'i2cdetect -y 1' to verify sensor is detected")
    logger.fatal("3. Make sure I2C is enabled in raspi-config")
