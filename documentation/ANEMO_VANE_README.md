# SparkFun Weather Meter Kit Anemometer and Wind Vane Setup

## 🧩 Kit Overview

![alt text](images/sparkfun_weather_kit.jpeg)

## ⚙️ Hardware and Wiring

## Pre requisites
- Digital multimeter
- 1 RJ45 breakout
- DuPont Cables
- 1 breadboard

### SparkFun Weather Meter Kit Anemometer Wind Vane Wiring

- RJ11 Connector Pinout
The SparkFun Weather Meter Kit uses RJ11 connectors that does not follow the standard pinout.


### Identify connections
This RJ11 to RJ45 is tricky. My suggestion, bring the whole kit mounted inside (including the stand), next to you work bench and test with the multimeter.
Connect the RJ11 connector from vane/anemometer to test RJ45 breakout for testing.

**Anemometer Wire Identification:**

The anemometer uses only 2 wires - they act as a simple switch:

One connects to Ground
One is the Signal (needs pull-up resistor)

1. Find which wires are for anemometer:
    - Set multimeter to continuity/diode mode (beep mode)
    - Spin the anemometer cups slowly
    - Test all wire pairs
    - The pair that beeps intermittently as you spin = Anemometer wires

2. Once you find the anemometer pair:

    Either wire can be ground or signal (it's just a switch).
    In my case, it was the pins 4 and 5 from the RJ45 breakout, so RJ45 breakout pin 4 is RJ11 Red (anemometer signal) and RJ45 breakout pin 5 is RJ11 Yellow (Ground), as demonstrated below. 
    So, I connected a Purple DuPont to RJ45 breakout Pin 4 (RJ11 Red, anemometer signal) and a Black DuPont to RJ45 breakout Pin 5 (RJ11 Yellow, GND)

That leaves 2 pins for the wind vane. But the vane needs 3 wires (Power, Ground, Signal), and you only have 2 remaining...
***The Answer: Shared Ground!***


**Wind Vane Wire Identification:**
We already know 2 wires, RJ11 Red (RJ45 breakout Pin 4, Purple DuPont) and RJ11 Yellow (RJ45 breakout Pin 5, Black DuPont).
Do as combinations tests as you want. what worked for me was:

1. Power-Up Test:
    - RJ45 breakout pin 3 (RJ11 Pin 2, Black wire) → Red DuPont → Breadboard Power rail
    - RJ45 breakout pin 5 (RJ11 Pin 4, Yellow wire) → Black DuPont → Breadboard GND rail
    - RJ45 breakout pin 6 (RJ11 Pin 5, Green wire) → Orange DuPont → Multimeter Red probe
    - Breadboard GND (Ground) → Multimeter Black probe
    - Set multimeter to DC Voltage (V˜ range) position 20m
    - Rotate vane slowly
    ***You should see voltage varying between ~0.4V to 2.8V as you rotate through the 16 positions!***

**Connection summary:**
    | RJ11 Pin| Wire Color | Function          | Connection          | RJ45 Breakout pin | DuPont |
    |---------|------------|-------------------| ------------------- | ----------------- | ------ |
    | Pin 2	  | Black      | VCC (Power)       | To 3.3V             | 3                 | Red    |
    | Pin 3	  | Red        | Anemometer signal | Pi Pin 11 (GPIO 17) | 4                 | Purple |
    | Pin 4	  | Yellow     | Ground            | To GND              | 5                 | Black  |
    | Pin 5	  | Green	   | Wind Vane Signal  | To DFR0553 A0       | 6                 | Orange |


**Bench test:**

Once you have the wire identified on a test breakout test the vane and anemometer on Pi
1. Connect wires:
    - RJ45 breakout Pin 3 → Red DuPont → Breadboard Power rail
    - RJ45 breakout Pin 4 → Purple DuPont → Breadboard 15C
    - RJ45 breakout Pin 5 → Black DuPont → Breadboard GND rail
    - RJ45 breakout Pin 6 → Orange DuPont → Breadboard 20A

2. Test the anemometer:
    - Connect to Pi via ssh
    - Activate pyenv (conda activate python311)
    - Go to folder weather-station/scripts/anemo
    - Run the scripts on there and follow the instructions

3. Test the vane:
    - Switch to folder weather-station/scripts/windvane
    - Cry on your bed
    - The vane is only working on the multimeter, so let's disable it on code and return for this later.

#### For Long Cable Run - Minimal Protection ####

At Pi End:
- 100nF capacitor: GPIO17 to GND (debounce/filter)
- Ferrite choke on cable (reduces EMI)

At Sensor End:  
- Keep connections weatherproof
- Ensure good ground connection

### Wiring diagram so far:

- Pi

    <img src="images/Pi_wiring.png" alt="Raspberry Pi GPIO pinout diagram showing connections for wind vane circuit with pins labeled for 3.3V power, ground, and GPIO 17 for anemometer signal" width="500"> 

- BreadBoard

    <img src="images/breadboard_wiring.png" alt="BreadBoard pinout diagram showing connections for BME280, DFR0553, Anemometer and Wind vane" width="800"> 


#### 🔍 What is "Bounce" in Switches? and why it's important for your anemometer setup ####
- If you are interested on details, check **ANEMOMETER_DETAILS.md**



- The SparkFun Weather Meter Kit wind vane uses a resistor network that requires connection to your DFR0553 (ADS1115) analog input for reading wind direction.

### Circuit Diagram
```bash
Power Rail → 17A → 10kΩ leg 1 → 10kΩ leg 1 17B → Junction (Row 20B) → 100nF leg 1 20C → ADS1115 A0 (20D) → Wind Vane Signal (20A - Orange)
                                                    ↓
                                                100nF leg 1 → 21C  
                                                    ↓
                                                100nF leg 2 → GND Rail
```

## install python prereqs:
```bash
pip install adafruit-circuitpython-ads1x15
```

## Calibrate your readings

The vane have marks for North, South, East and West, so make sure to align the North mark with compass North.

It is also help if you mark the other directions on the vane fixed part for calibration and use a elastic band to hold the movel part in the desired direction.

Use script scripts/3-full_vane_test.py

The one that worked better for me is different from spec. Maybe the spec refer to another emisphere readings?

# Voltage tolerance for direction matching (volts)
TOLERANCE = 0.05

# Wind direction mapping based on your actual hardware calibration
# Custom calibrated values from your SparkFun Weather Kit + 10kΩ voltage divider
# Note: Some adjacent directions have identical voltages - hardware limitation
VOLTAGE_TO_DIR = {
    0.252: 202.5,  # SSW
    0.254: 180.0,  # S
    0.441: 225.0,  # SW
    0.602: 247.5,  # WSW (Note: very close voltage voltage to SW)
    0.763: 270.0,  # W
    1.043: 292.5,  # WNW (Note: very close voltage voltage to W)
    1.260: 135.0,  # SE
    1.261: 157.5,  # SSE
    1.802: 315.0,  # NW
    1.974: 337.5,  # NNW
    2.255: 67.5,   # ENE
    2.356: 90.0,   # E
    2.437: 112.5,  # ESE (Note: very close voltage to E)
    2.681: 45.0,   # NE
    2.858: 22.5,   # NNE
    2.973: 0.0,    # N
}


## 📚 References

- [Weather Meter Kit product page](https://www.sparkfun.com/weather-meter-kit.html)
- [Weather Meter Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide)
- [Weather Sensor Assembly](https://cdn.sparkfun.com/assets/8/4/c/d/6/Weather_Sensor_Assembly_Updated.pdf)
- [Datasheet](https://cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf)
- [Arduino Library](https://github.com/sparkfun/SparkFun_Weather_Meter_Kit_Arduino_Library)