# DIY Raspberry Pi Weather Station Project

This project documents the creation of a home weather station using a Raspberry Pi, BME280, ADS1115, anemometer, wind vane, and rain gauge — with optional GPS or Wi-Fi-based geolocation.

---

## 🧩 Project Overview

- **Platform**: Raspberry Pi 5
- **Sensors**: DFRobot BME280 I²C (temp/pressure/humidity). ADS1115 (analog input), anemometer, wind vane, rain gauge (future)
- **Power**: 5V
- **Logging**: CSV (and optionally SQLite)
- **Geolocation**: TBD

---

## ⚙️ Hardware and Wiring

## Raspberry Pi 5 GPIO pinout diagram:
<img src="https://github.com/user-attachments/assets/1e071a9f-dda5-4bc4-bc79-a0a95151cba8" />


---

## 🧮 CSV Logging

Data saved to `weather_log.csv`:

```
timestamp, temperature, humidity, pressure, round(altitude, 1)]
2025-10-08T16:04:03,21.7,48.2,1011.8,2.4,34.1
```


## ⚡ Simple management script:

### Start sensor in background
./run_station_background.sh start

### Check if it's running
./run_station_background.sh status

### View logs
./run_station_background.sh logs

### Stop the sensor
./run_station_background.sh stop

***Explanation of Symbols***
- &: Runs command in background
- \>: Redirects stdout
- 2>&1: Redirects stderr to same place as stdout
- null: "Black hole" that discards all input
- nohup: Prevents process from stopping when terminal closes

## Geolocation
The apps use openweathermap api with hardcoded latitude and longitude for now.


## 🗄 SQLite Integration

SQLite replace CSV for structured long-term storage. Check ***documentation/SQLITE_README.MD*** for setup instructions


## 🛰 GPS Integration

Replace IP geolocation with GPS (e.g., Neo-6M, u-blox M8N).  
Connect via UART and use `gps3` or `gpsd` to fetch live coordinates.

---

## ✅ Future Enhancements
- [ ] SQLite integration with daily summary queries
- [ ] Segregate bme280 and ic2 as modules
- [ ] Improve geolocation
- [ ] Local Flask dashboard  
- [ ] MQTT publishing for Home Assistant  

---

## 📚 References

- [SparkFun Weather Meter Datasheet (PDF)](https://cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf)
- [DFRobot Gravity ADS1115](https://www.dfrobot.com/product-1894.html)
- [Adafruit BME280 Guide](https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout)
