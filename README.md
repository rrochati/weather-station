# DIY Raspberry Pi Weather Station Project

This project documents the creation of a home weather station using a Raspberry Pi, BME280, ADS1115, anemometer, wind vane, and rain gauge — with optional GPS or Wi-Fi-based geolocation.

---

## 🧩 Project Overview

- **Platform**: Raspberry Pi 5
- **Sensors**: DFRobot BME280 I²C (temp/pressure/humidity), ADS1115 (analog input), anemometer, wind vane, rain gauge
- **Power**: 5V (not suitable directly from 18650 without a boost converter)
- **Logging**: CSV (and optionally SQLite)
- **Geolocation**: IP-based via [ipinfo.io](https://ipinfo.io)

---

## ⚙️ Hardware and Wiring

## Raspberry Pi 5 GPIO pinout diagram:
<img width="2064" height="1185" alt="image" src="https://github.com/user-attachments/assets/1e071a9f-dda5-4bc4-bc79-a0a95151cba8" />

## ASCII / text wiring diagram

```bash
         Raspberry Pi 5
     +----------------------+
     | 3.3V -------------+    |
     |                   |    |
     | GND --------------+----+---+  (common ground)
     |                   |        |
     | SDA (GPIO 2) ------+--------+----> ADS1115 SDA
     | SCL (GPIO 3) ------+--------+----> ADS1115 SCL
     |                   |        |
     | GPIO17 (or other) -+-------------> Anemometer input (switch)
     +----------------------+         |
                                     +--- to 3.3V via pull-up
                                     |
                                     +--- other side of anemometer switch
````

And for the analog (vane) side, connected to ADS1115:

```bash
   3.3V
    |
    Rext (e.g. 10 kΩ fixed resistor)
    |
    +------> node (Vout) --------> ADS1115 A0
    |
    Vane resistor network (depending on wind direction)
    |
   GND
````

See generated wiring diagram (ADS1115 + wind sensors + BME280).

**Connections summary**:

| Component | Raspberry Pi 5 Pin |
|------------|--------------------|
| BME280 SDA | GPIO2 (SDA) |
| BME280 SCL | GPIO3 (SCL) |
| ADS1115 SDA | GPIO2 (SDA) |
| ADS1115 SCL | GPIO3 (SCL) |
| Anemometer | GPIO17 |
| Rain gauge | GPIO27 |
| 3.3V / GND | Shared Power |

---

## 📟 Weather Station Script (with Wi-Fi Geolocation)

```python
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
# Geolocation via IP
# -------------------------------------------------
def get_geo_ip():
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5)
        data = r.json()
        lat, lon = map(float, data["loc"].split(","))
        return {
            "latitude": lat,
            "longitude": lon,
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "ip": data.get("ip")
        }
    except Exception as e:
        print("Geolocation error:", e)
        return None

geo = get_geo_ip()
latitude = geo["latitude"] if geo else None
longitude = geo["longitude"] if geo else None
city = geo["city"] if geo else "Unknown"
region = geo["region"] if geo else "Unknown"
country = geo["country"] if geo else "Unknown"
ip = geo["ip"] if geo else "Unknown"
print(f"Station location: City: {city}, Coordinates: ({latitude}, {longitude}), Region: {region}, Country: {country}, IP: {ip}")

# -------------------------------------------------
# Configuration
# -------------------------------------------------

# GPIO pins (BCM numbering)
ANEMO_PIN = 17       # Anemometer reed switch
RAIN_PIN = 27        # Rain gauge reed switch

# Conversion constants
SPEED_CONV = 0.6667      # m/s per pulse/sec (SparkFun)
RAIN_MM_PER_TIP = 0.2794 # mm per tip

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# ADS1115 setup for wind vane
ads = ADS.ADS1115(i2c)
ads.gain = 1  # ±4.096V
vane_channel = AnalogIn(ads, ADS.P0)

# BME280 setup
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.sea_level_pressure = 1013.25

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
GPIO.setup(RAIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
GPIO.add_event_detect(RAIN_PIN, GPIO.FALLING, callback=rain_callback, bouncetime=200)


# -------------------------------------------------
# CSV setup
# -------------------------------------------------
CSV_FILE = "weather_log.csv"

with open(CSV_FILE, "a", newline="") as f:
    writer = csv.writer(f)
    if f.tell() == 0:
        writer.writerow([
            "timestamp", "temperature_C", "humidity_%", "pressure_hPa",
            "wind_speed_m_s", "wind_dir_deg", "wind_vane_voltage_V",
            "rain_interval_mm", "altitude_m", "latitude", "longitude", "city"
        ])


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
    print("Starting full weather station... Press Ctrl+C to stop.")
    while True:
        # Measure wind
        speed, cps = measure_wind_speed(5)
        v, direction = read_wind_direction()

        # Read rain (since last cycle)
        rain = measure_rain()

        # Read BME280
        temp = bme280.temperature
        humidity = bme280.humidity
        pressure = bme280.pressure
        altitude = bme280.altitude

        # Write to CSV
        timestamp = datetime.now().isoformat(timespec='seconds')
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, temp, humidity, pressure,
                speed, direction, v, rain, altitude,
                latitude, longitude, city
            ])

        # Print summary
        print(f"Timestamp: {timestamp}")
        print(f"Location: {city}, ({latitude}, {longitude})")
        print(f"Wind: {speed:.2f} m/s ({speed*3.6:.1f} km/h), Dir: {direction if direction is not None else 'Unknown'}° ({v:.2f} V)")
        print(f"Rain: +{rain:.2f} mm this interval")
        print(f"Temp: {temp:.1f} °C | Humidity: {humidity:.1f}% | Pressure: {pressure:.1f} hPa | Altitude: {altitude:.1f} m")
        print("-" * 30)

except KeyboardInterrupt:
    print("Stopping weather station...")
finally:
    GPIO.cleanup()

```
*(Script includes CSV logging, geolocation via ipinfo.io, BME280, ADS1115, wind speed/direction, and rainfall measurement.)*

---

## 🌍 Wi-Fi / IP Geolocation Function

```python
def get_geo_ip():
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5)
        data = r.json()
        lat, lon = map(float, data["loc"].split(","))
        return {
            "latitude": lat,
            "longitude": lon,
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "ip": data.get("ip")
        }
    except Exception as e:
        print("Geolocation error:", e)
        return None
```
Uses **ipinfo.io** to obtain approximate latitude, longitude, and city based on your public IP.

---

## 🧮 CSV Logging

Data saved to `weather_log.csv`:

```
timestamp,temperature_C,humidity_%,pressure_hPa,wind_speed_m_s,wind_dir_deg,wind_vane_voltage_V,rain_interval_mm,altitude_m,latitude,longitude,city
2025-10-08T16:04:03,21.7,48.2,1011.8,2.4,180.0,0.93,0.00,34.1,38.7167,-9.1333,Lisbon
```

---

## 🗄 SQLite Overview

SQLite can replace CSV for structured long-term storage. Example:

```python
import sqlite3

db = sqlite3.connect("weather.db")
cur = db.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS weather (
    timestamp TEXT,
    temperature REAL,
    humidity REAL,
    pressure REAL,
    wind_speed REAL,
    wind_dir REAL,
    wind_vane_voltage REAL,
    rain REAL,
    altitude REAL
)
""")
db.commit()
```

---

## 🛰 Optional GPS Integration

Replace IP geolocation with GPS (e.g., Neo-6M, u-blox M8N).  
Connect via UART and use `gps3` or `gpsd` to fetch live coordinates.

---

## ✅ Future Enhancements

- [ ] SQLite integration with daily summary queries  
- [ ] Local Flask dashboard  
- [ ] MQTT publishing for Home Assistant  

---

## 📚 References

- [SparkFun Weather Meter Datasheet (PDF)](https://cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf)
- [DFRobot Gravity ADS1115](https://www.dfrobot.com/product-1894.html)
- [Adafruit BME280 Guide](https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout)
