#!/usr/bin/env python3
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_bme280
import RPi.GPIO as GPIO
import csv
from datetime import datetime

# -------------------------------------------------
# Configuration
# -------------------------------------------------

# GPIO pins (BCM numbering)
ANEMO_PIN = 17       # Anemometer reed switch
#RAIN_PIN = 27        # Rain gauge reed switch

# Conversion constants
SPEED_CONV = 0.6667      # m/s per pulse/sec (SparkFun)
#RAIN_MM_PER_TIP = 0.2794 # mm per tip

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# ADS1115 setup for wind vane
#ads = ADS.ADS1115(i2c)
#ads.gain = 1  # ±4.096V
#vane_channel = AnalogIn(ads, ADS.P0)

# BME280 setup
#bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
#bme280.sea_level_pressure = 1013.25

# -------------------------------------------------
# Wind vane voltage→direction lookup (3.3V, 10k divider)
# -------------------------------------------------
VOLTAGE_TO_DIR = {
    0.270: 67.5,
    0.300: 90.0,
    0.212: 112.5,
    0.595: 135.0,
    0.408: 157.5,
    0.926: 180.0,
    0.789: 202.5,
    2.031: 225.0,
    1.932: 247.5,
    3.046: 270.0,
    2.667: 292.5,
    2.859: 315.0,
    2.265: 337.5,
    2.533: 0.0,
    1.308: 22.5,
    1.487: 45.0,
}
TOLERANCE = 0.05

# -------------------------------------------------
# GPIO setup
# -------------------------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(ANEMO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(RAIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# -------------------------------------------------
# Global counters
# -------------------------------------------------
anemo_pulses = 0
rain_tips = 0

def anemo_callback(channel):
    global anemo_pulses
    anemo_pulses += 1

def rain_callback(channel):
    global rain_tips
    rain_tips += 1

GPIO.add_event_detect(ANEMO_PIN, GPIO.FALLING, callback=anemo_callback, bouncetime=10)
#GPIO.add_event_detect(RAIN_PIN, GPIO.FALLING, callback=rain_callback, bouncetime=200)



# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def read_wind_direction():
    v = vane_channel.voltage
    nearest_v = min(VOLTAGE_TO_DIR.keys(), key=lambda x: abs(x - v))
    if abs(nearest_v - v) <= TOLERANCE:
        direction = VOLTAGE_TO_DIR[nearest_v]
    else:
        direction = None
    return v, direction

def measure_wind_speed(interval=5.0):
    global anemo_pulses
    anemo_pulses = 0
    time.sleep(interval)
    cps = anemo_pulses / interval
    speed = cps * SPEED_CONV  # m/s
    return speed, cps

def measure_rain():
    global rain_tips
    total = rain_tips * RAIN_MM_PER_TIP
    rain_tips = 0
    return total

# -------------------------------------------------
# Main loop
# -------------------------------------------------
try:
    print("Starting full weather kit... Press Ctrl+C to stop.")
    while True:
        # Measure wind
        speed, cps = measure_wind_speed(5)
        #v, direction = read_wind_direction()

        # Read rain (since last cycle)
        #rain = measure_rain()

        # Print summary
        print(f"Timestamp: {timestamp}")
        print(f"Wind: {speed:.2f} m/s ({speed*3.6:.1f} km/h), Dir: {direction if direction is not None else 'Unknown'}° ({v:.2f} V)")
        print("-" * 30)

except KeyboardInterrupt:
    print("Stopping weather kit...")
finally:
    GPIO.cleanup()

```
*(Script includes CSV logging, geolocation via ipinfo.io, BME280, ADS1115, wind speed/direction, and rainfall measurement.)*