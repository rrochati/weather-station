# SparkFun Weather Meter Kit Wind Vane Setup

## 🧩 Kit Overview

![alt text](images/sparkfun_weather_kit.jpeg)


## ⚙️ Hardware and Wiring

***SparkFun Weather Meter Kit Wind Vane Wiring***
- The SparkFun Weather Meter Kit wind vane uses a resistor network that requires connection to your DFR0553 (ADS1115) analog input for reading wind direction.

- RJ11 Connector Pinout (Wind Vane)
The SparkFun Weather Meter Kit uses RJ11 connectors with the following a standard pinout.

But, due to our RJ breakout unusual color pattern we already discussed on Anemometer setup, check the following table for connection

    | RJ11 Pin| Wire Color | Function                | Connection                     | Leroy conector | DuPont Wire soldered |
    |---------|------------|-------------------------| ------------------------------ | -------------- | -------------------- |
    | Pin 1	  | Black      | VCC (Power)             | Connect to 3.3V                | Yellow         | Yellow Female        |
    | Pin 2	  | Red        | Wind Speed (Anemometer) | Connect to Pi Pin 11 (GPIO 17) | Green          | Green Female         |
    | Pin 3	  | Yellow     | Ground                  | Connect to GND                 | Red            | Purple Male          |
    | Pin 4	  | Green	   | Wind Vane Signal        | Connect to DFR0553 A0          | Black          | Brown Male           |

    **The Pins 1 and 4 function need to be confirmed.**

### Wiring diagram so far:

- Pi

    ![alt text](images/Pi_wiring.png)

- BreadBoard

    ![alt text](images/breadboard_wiring.png)

### Circuit Diagram
```bash
3.3V (Row 1+) ────[10kΩ]────┬────[100nF]────GND (Row 1-)
                              │
                              ├────► DFR0553 A0
                              │
                              └────► Wind Vane Signal (Brown)
                                     │
                              Wind Vane Internal Resistors
                                     │
                                    GND
```


## 📚 References

- [Weather Meter Kit product page](https://www.sparkfun.com/weather-meter-kit.html)
- [Weather Meter Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide)
- [Weather Sensor Assembly](https://cdn.sparkfun.com/assets/8/4/c/d/6/Weather_Sensor_Assembly_Updated.pdf)
- [Datasheet](https://cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf)
- [Arduino Library](https://github.com/sparkfun/SparkFun_Weather_Meter_Kit_Arduino_Library)