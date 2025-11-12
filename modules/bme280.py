import logging
import board # pyright: ignore[reportMissingImports]
import busio # pyright: ignore[reportMissingImports]
from adafruit_bme280 import basic as adafruit_bme280 # pyright: ignore[reportMissingImports]

LOG_FILE=os.getenv('LOG_FILE', '/home/rrocha/jarvis/jarvis.log')

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

# Initialize I2C bus and BME280 sensor
def initialize_bme280():
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
        
        return bme280
    
    except Exception as e:
        logger.fatal(f"Error initializing BME280: {e}")
        logger.fatal("\nTroubleshooting tips:")
        logger.fatal("1. Check I2C wiring")
        logger.fatal("2. Run 'i2cdetect -y 1' to verify sensor is detected")
        logger.fatal("3. Make sure I2C is enabled in raspi-config")
        return None