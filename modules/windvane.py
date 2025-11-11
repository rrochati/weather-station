import logging
import time
import board
import busio
import lgpio
import sys 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # This ensures output goes to stdout
    ]
)

logger = logging.getLogger(__name__)

# -------------------------------------------------
# Configuration
# -------------------------------------------------

# GPIO pins (BCM numbering)
ANEMO_PIN = 17       # Anemometer reed switch
gpio_handle = None

# Conversion constants
SPEED_CONV = 0.6667      # m/s per pulse/second (SparkFun spec: 1.492 mph = 2.4 km/h = 1 switch closure/second)

# -------------------------------------------------
# Global counters
# -------------------------------------------------
anemo_pulses = 0


def start_gpio():
    """Initialize GPIO"""
    global gpio_handle
    
    logger.info("🔧 Starting GPIO...")
    
    try:
        # Open GPIO chip
        gpio_handle = lgpio.gpiochip_open(0)
        logger.info("✅ GPIO chip opened successfully")
        
        # Claim pin as input with pull-up
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN)
        lgpio.gpio_set_debounce_micros(gpio_handle, ANEMO_PIN, 10000)
        logger.info(f"✅ GPIO{ANEMO_PIN} claimed as input")

    except Exception as e:
        logger.error(f"❌ Error during GPIO test: {e}")


def measure_wind_speed(interval=5):
    """
    Measure wind speed by counting rising edges over a specified interval.
    
    Args:
        interval (int): Number of seconds to measure (default 5)
        
    Returns:
        tuple: (wind_speed_m_per_s, total_pulses_counted)
    """
    global anemo_pulses
    anemo_pulses = 0
    
    # Get initial state
    last_level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
    pulses = 0
    start_time = time.time()
    
    logger.info(f"🌬️  Measuring wind for {interval} seconds...")
    
    # Monitor continuously for the specified interval
    while (time.time() - start_time) < interval:
        current_level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
        
        # Count rising edge as one pulse (low to high transition)
        if current_level == 1 and last_level == 0:
            pulses += 1
            timestamp = time.strftime("%H:%M:%S")
            print(f"   [{timestamp}] Pulse #{pulses}: Rising edge detected")
            
        last_level = current_level
        time.sleep(0.01)  # Check every 10ms for better accuracy
    
    # Calculate results
    wind_speed = (pulses / interval) * SPEED_CONV  # m/s
    
    logger.info(f"📊 Measurement complete: {pulses} pulses in {interval}s = {wind_speed:.2f} m/s")
    
    return wind_speed, pulses
