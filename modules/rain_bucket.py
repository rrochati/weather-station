import logging
import time
import lgpio
import sys
import os
from datetime import datetime, timedelta

LOG_FILE = os.getenv('LOG_FILE', '/home/rrocha/logs/weather_station.log')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode='a')
    ]
)
logger = logging.getLogger(__name__)

class RainBucket:
    """
    Rain bucket sensor class for SparkFun Weather Meter Kit
    Uses GPIO pin to detect rain bucket tips and calculate rainfall
    """
    
    def __init__(self, pin=27):
        """
        Initialize rain bucket sensor
        
        Args:
            pin (int): GPIO pin number (BCM numbering) for rain sensor
        """
        self.pin = pin
        self.gpio_handle = None
        
        # SparkFun Weather Meter Kit specification
        self.mm_per_tip = 0.2794  # mm per tip (from documentation)
        
        # Counters
        self.interval_tips = 0
        self.daily_tips = 0
        self.total_tips = 0
        
        # Daily reset tracking
        self.last_reset_date = datetime.now().date()
        
        logger.info(f"🌧️ Rain bucket initialized on GPIO{self.pin} ({self.mm_per_tip}mm per tip)")
    
    def setup(self):
        """Initialize GPIO for rain bucket"""
        try:
            # Open GPIO chip
            self.gpio_handle = lgpio.gpiochip_open(0)
            logger.info("✅ Rain bucket GPIO chip opened successfully")
            
            # Claim pin as input with pull-up
            lgpio.gpio_claim_input(self.gpio_handle, self.pin, lgpio.SET_PULL_UP)
            lgpio.gpio_set_debounce_micros(self.gpio_handle, self.pin, 200000)  # 200ms debounce
            logger.info(f"✅ Rain bucket GPIO{self.pin} claimed as input with pull-up enabled")
            
            # Set up callback for falling edge detection
            self._setup_callback()
            
        except Exception as e:
            logger.error(f"❌ Error setting up rain bucket GPIO: {e}")
            raise
    
    def _setup_callback(self):
        """Set up interrupt callback for rain bucket tips"""
        try:
            # For lgpio, we'll use polling instead of callbacks for simplicity
            # Store the last state for edge detection
            self.last_state = lgpio.gpio_read(self.gpio_handle, self.pin)
            logger.info("✅ Rain bucket monitoring started")
        except Exception as e:
            logger.error(f"❌ Error setting up rain bucket callback: {e}")
    
    def _check_daily_reset(self):
        """Reset daily counter if it's a new day"""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            logger.info(f"🌅 New day detected, resetting daily rain counter (was {self.daily_tips} tips = {self.daily_tips * self.mm_per_tip:.3f}mm)")
            self.daily_tips = 0
            self.last_reset_date = current_date
    
    def _poll_for_tips(self):
        """Poll GPIO pin for rain bucket tips (fallback method)"""
        try:
            current_state = lgpio.gpio_read(self.gpio_handle, self.pin)
            
            # Detect falling edge (HIGH to LOW transition)
            if current_state == 0 and self.last_state == 1:
                self._tip_detected()
            
            self.last_state = current_state
            
        except Exception as e:
            logger.error(f"❌ Error polling rain bucket: {e}")
    
    def _tip_detected(self):
        """Handle rain bucket tip detection"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.interval_tips += 1
        self.daily_tips += 1
        self.total_tips += 1
        
        rain_mm = self.mm_per_tip
        logger.info(f"💧 [{timestamp}] Rain tip #{self.interval_tips}: +{rain_mm:.3f}mm (Daily: {self.daily_tips * self.mm_per_tip:.3f}mm)")
    
    def get_data(self, reset_counter=False):
        """
        Get current rain data
        
        Args:
            reset_counter (bool): If True, reset the interval counter
            
        Returns:
            dict: Rain data with interval and daily totals
        """
        # Check for new day
        self._check_daily_reset()
        
        # Poll for any recent tips (backup method)
        self._poll_for_tips()
        
        # Calculate totals
        interval_mm = self.interval_tips * self.mm_per_tip
        daily_mm = self.daily_tips * self.mm_per_tip
        total_mm = self.total_tips * self.mm_per_tip
        
        data = {
            'interval_tips': self.interval_tips,
            'interval_mm': interval_mm,
            'daily_tips': self.daily_tips,
            'daily_mm': daily_mm,
            'total_tips': self.total_tips,
            'total_mm': total_mm,
            'timestamp': datetime.now().isoformat()
        }
        
        # Reset interval counter if requested
        if reset_counter:
            logger.info(f"🔄 Rain interval reset: {self.interval_tips} tips ({interval_mm:.3f}mm)")
            self.interval_tips = 0
        
        return data
    
    def get_rain_rate(self, time_window_minutes=60):
        """
        Calculate current rain rate (for future enhancement)
        This is a placeholder for more sophisticated rain rate calculation
        
        Args:
            time_window_minutes (int): Time window for rate calculation
            
        Returns:
            float: Rain rate in mm/hour
        """
        # For now, use simple interval-based calculation
        data = self.get_data()
        
        # Assuming measurement interval is 1 minute, estimate hourly rate
        if data['interval_mm'] > 0:
            rate_mm_per_hour = data['interval_mm'] * 60  # Scale to hourly
        else:
            rate_mm_per_hour = 0.0
        
        return rate_mm_per_hour
    
    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            if self.gpio_handle is not None:
                lgpio.gpiochip_close(self.gpio_handle)
                logger.info("✅ Rain bucket GPIO cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during rain bucket cleanup: {e}")


# Test function
def test_rain_bucket():
    """Test rain bucket functionality"""
    print("🧪 Testing rain bucket...")
    
    rain_bucket = RainBucket(pin=27)
    rain_bucket.setup()
    
    try:
        print("📊 Monitoring for 30 seconds. Try triggering the rain bucket...")
        start_time = time.time()
        
        while (time.time() - start_time) < 30:
            data = rain_bucket.get_data()
            if data['interval_tips'] > 0:
                print(f"✅ Rain detected: {data['interval_mm']:.3f}mm ({data['interval_tips']} tips)")
            time.sleep(1)
        
        # Final data
        final_data = rain_bucket.get_data(reset_counter=True)
        print(f"\n📊 Test Results:")
        print(f"   Interval: {final_data['interval_mm']:.3f}mm ({final_data['interval_tips']} tips)")
        print(f"   Daily: {final_data['daily_mm']:.3f}mm ({final_data['daily_tips']} tips)")
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    finally:
        rain_bucket.cleanup()


if __name__ == "__main__":
    test_rain_bucket()