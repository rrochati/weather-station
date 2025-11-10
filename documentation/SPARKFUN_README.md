# Weather Meter Kit setup

## 🧩 Kit Overview

![alt text](images/sparkfun_weather_kit.jpeg)


## ⚙️ Hardware and Wiring

***SparkFun Weather Meter Kit Anemometer Wiring***

As the wind vane setup is more complex, let's begin with anemometer.

## 🎯 **Anemometer-Only Setup (Minimal Start):**

### **What You Need:**
```bash
Hardware:
- Just the anemometer from your SparkFun kit
- Access to the green + black wires from RJ11
- Long cable (your 10-20m run)

Software:
- Your existing weather_station.py already handles this!
```

### **Simplified Wiring:**
```bash
Anemometer Only:
Green wire (signal) ----[long cable]----> Pi Pin 11 (GPIO17)
Black wire (ground) ----[long cable]----> Pi Pin 6 (GND)
```

#### Warning about wiring ####
Watch closely your breakout connector for RJ11.
The one I'm using (from Leroy Merlin) does not follow the color schema as the Sparckfun cable

So, to get the Green wire from Anemometer I will use black wire on connector
To get the Black wire from Anemometer I will use the yellow wire on connector

And, to add more complexibility, I will use different DuPont cable collors. Look for collors next to the anemometer on my cables

PS: And the extension uses another color pattern :)

| Front wiev | First connection | Second connection | Thrid connection | Fourth connection |
| -----------|------------------| ------------------| -----------------| ------------------|
| Anemometer | Black | Red  | Yellow | Green |
| Leroy conector | Yellow | Green | Red | Black |
| DuPont Wire soldered | Yellow Female | Green Female  | Purple Male | Brown Male |

#### For Long Cable Run - Minimal Protection ####

At Pi End:
- 100nF capacitor: GPIO17 to GND (debounce/filter)
- Ferrite choke on cable (reduces EMI)

At Sensor End:  
- Keep connections weatherproof
- Ensure good ground connection

#### 🔍 What is "Bounce" in Switches? and why it's important for your anemometer setup ####

When mechanical switches (like your anemometer's reed switch) open or close, they don't make a clean electrical connection. Instead, they "bounce" - making and breaking contact multiple times very quickly.

#### **Visual Example:**
```bash
What you expect from 1 anemometer pulse:
     3.3V ____          ____
              |        |
     0V       |________|

What actually happens (bounce):
     3.3V ____    _ _   ____
              |  | | | |
     0V       |__| |_|_|

Result: Pi sees 4-5 pulses instead of 1!
```

#### 🌪️ **Why This Matters for Your Anemometer:**

```bash
Real scenario:
- Anemometer spins once = should be 1 pulse
- Reed switch bounces = Pi counts 3-5 pulses  
- Wind speed calculation becomes 3-5x too high!

Example:
- Actual wind: 10 km/h
- With bounce: reads as 30-50 km/h
```

#### **Solution - Hardware Debouncing:**
The **100nF capacitor** acts as a **low-pass filter** that smooths out the rapid bounces:

```bash
Without Capacitor (bouncy):
GPIO17: _____|‾|_|‾|_|‾‾‾‾‾

With 100nF Capacitor (smooth):
GPIO17: _____|‾‾‾‾‾‾‾‾‾‾‾‾‾
               ^
         Clean single pulse!
```

#### ⚡ **How the 100nF Capacitor Works:**

##### **Circuit:**
```bash
                 Anemometer Reed Switch
3.3V ----[pullup]----+---------> GPIO17
                      |
                   [100nF]
                      |
                     GND

When switch closes:
- Capacitor charges slowly through pullup resistor
- Prevents rapid voltage changes
- Creates smooth transition
```

#### **Technical Details:**
```bash
RC Time Constant:
- R = 10kΩ (pullup resistor)  
- C = 100nF (debounce capacitor)
- τ = R × C = 10kΩ × 100nF = 1ms

This means:
- Bounces faster than ~1ms are filtered out
- Real pulses (longer than 1ms) pass through
- Perfect for mechanical switches!
```

#### 🛠️ **Practical Implementation on a Breadboard:**
- PI GPIIO 6 (pin xx) -> black wire -> GND Rail line 1 (alredy done for another module)
- GND Rail line 14: Capacitor leg 2 (filters to ground)
- Line 14 Row A: Capacitor leg 1 (filter input)
- Pi Pin 11 (GPIO17) -> green cable -> Line 14 Row B (signal input)  
- Anemometer green wire -> green wire -> Line 14 Row C (signal source)


#### **Component Specs:**
```bash
Capacitor: 100nF (0.1μF) ceramic capacitor
- Voltage: 50V (overkill, but safe)
- Type: Ceramic (X7R or C0G)
- Package: Through-hole or 0805 SMD
- Cost: €0.05-0.10
```

#### 📊 **Before vs After Results:**

#### **Without Debounce Capacitor:**
```bash
Anemometer Test Results:
- 1 manual spin → 3-7 pulses counted
- Wind speed: Erratic, too high
- Data: Noisy, unreliable
```

#### **With 100nF Debounce Capacitor:**
```bash
Anemometer Test Results:
- 1 manual spin → 1 pulse counted  
- Wind speed: Accurate, stable
- Data: Clean, reliable
```

#### 🔧 **Your Existing Software Also Helps:**

Your code already has **software debouncing**:
```python
# This line in your weather_station.py:
GPIO.add_event_detect(ANEMO_PIN, GPIO.FALLING, callback=anemo_callback, bouncetime=10)
                                                                              ↑
                                                            10ms software debounce
```

#### **Hardware + Software = Best Results:**
```bash
Hardware debounce (100nF): Smooths electrical bounce
Software debounce (10ms):  Ignores rapid callbacks

Combined: Nearly perfect pulse counting!
```

#### 🌬️ **Real-World Impact:**

**Without proper debouncing:**
- Calm day (5 km/h wind) might read as 20 km/h
- Gusty conditions become unreadable
- False storm warnings

**With proper debouncing:**
- Accurate wind measurements
- Reliable weather data
- Proper storm detection


## Pi Setup:
```python
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Internal pullup
GPIO.add_event_detect(17, GPIO.FALLING, callback=anemo_callback, bouncetime=10)
```

## 📊 **Testing Process:**

### **Step 1: Bench Test (Short Cable)**
```bash
1. Connect anemometer with short wires first
2. Run your weather_station.py
3. Spin anemometer by hand and verify pulse counting
4. Check wind speed calculations (1 pulse/sec = 2.4 km/h)
```

### **Step 2: Long Cable Test**
```bash
1. Install long cable run
2. Test pulse detection at various spin rates  
3. Monitor for false pulses or missed pulses
4. Add protection components if needed
```

### **Step 3: Outdoor Installation**
```bash
1. Mount anemometer outdoors
2. Monitor data for 24-48 hours
3. Check for reasonable wind speed values
4. Look for electrical noise or interference
```

## 🔧 **Progressive Addition Strategy:**

### **Week 1: Anemometer Only**
- Test basic wind speed measurement
- Validate long cable run
- Identify any interference issues

### **Week 2: Add Wind Vane**  
- Connect wind direction sensor
- Add the 10kΩ voltage divider
- Test direction accuracy

### **Week 3: Add Rain Gauge**
- Complete the weather station
- Full system testing

## 💡 **Anemometer-Specific Tips:**

### **Calibration Check:**
```python
# Add this to your existing code for validation:
def calibrate_anemometer():
    """Simple calibration test"""
    print("Spin anemometer steadily for 10 seconds...")
    anemo_pulses = 0
    time.sleep(10)
    
    pps = anemo_pulses / 10.0  # pulses per second
    wind_speed_kmh = pps * 2.4
    wind_speed_ms = wind_speed_kmh / 3.6
    
    print(f"Pulses: {anemo_pulses}")
    print(f"Speed: {wind_speed_kmh:.1f} km/h ({wind_speed_ms:.1f} m/s)")
```

### **Long Cable Troubleshooting:**
```bash
If you see issues:

False pulses (too many counts):
- Add 100nF capacitor for debouncing
- Increase bouncetime in software (try 20-50ms)
- Check for loose connections

Missed pulses (too few counts):
- Verify good ground connection
- Check cable continuity
- Ensure pullup is working (measure voltage)

No pulses at all:
- Test continuity with multimeter
- Check GPIO pin assignment
- Verify internal pullup is enabled
```

Starting with just the anemometer lets you:
- ✅ Test your long cable run
- ✅ Validate basic pulse detection
- ✅ Identify any interference issues  
- ✅ Get immediate wind speed data
- ✅ Build confidence before adding complexity

**Ready to start with just the anemometer?**


***SparkFun Weather Meter Kit Wind Vane Wiring***
- The SparkFun Weather Meter Kit wind vane uses a resistor network that requires connection to your DFR0553 (ADS1115) analog input for reading wind direction.

- RJ11 Connector Pinout (Wind Vane)
The SparkFun Weather Meter Kit uses RJ11 connectors with the following standard pinout:

    | RJ11 Pin| Wire Color | Function | Connection |
    |---------|------------|----------| ---------- |
    | Pin 1	| Black | Ground | Connect to GND |
    | Pin 2	| Red | VCC (Power) | Connect to 3.3V |
    | Pin 3	| Yellow | Wind Vane Signal	| Connect to DFR0553 A0 |
    | Pin 4	| Green	| Wind Speed (Anemometer)	| Connect to Pi GPIO |

- Wind Vane Connection Diagram:
    ```bash
    SparkFun Weather Kit      Voltage Divider         DFR0553 (ADS1115)
        (RJ11)                                    
    +-------------+           3.3V                 +---------------+
    | Pin 1 (BLK) |----------> |                  | A0 (Analog)   |<---+
    | Pin 2 (RED) |----------> +                  | A1            |    |
    | Pin 3 (YEL) |----------> +---> 10kΩ ------> +---------------+    |
    | Pin 4 (GRN) |            |                                       |
    +-------------+            |                                       |
                              Vane Resistor Network                    |
                              (Variable resistance)                    |
                               |                                       |
                              GND <-----------------------------------+
    ```

- Complete Wiring Setup:
    ```bash
        Raspberry Pi 5 GPIO
    +------------------------+
    | Pin 1  (3.3V) ---------|----+---> BME280 VCC -----> DFR0553 + (Red)
    | Pin 3  (SDA)  ---------|----|-+-> BME280 SDA -----> DFR0553 D (Green)
    | Pin 5  (SCL)  ---------|----|-|-> BME280 SCL -----> DFR0553 C (Blue)
    | Pin 6  (GND)  ---------|----|-|--> BME280 GND -----> DFR0553 - (Black)
    | Pin 11 (GPIO17) -------|----|-|--> Anemometer (Green wire from RJ11)
    | Pin 13 (GPIO27) -------|    | |    (for rain gauge later)
    +------------------------+    | |
                                | |
    Wind Vane Voltage Divider:    | |
    3.3V (from Pi Pin 1) ---------|+
        |                         |
        10kΩ Resistor             |
        |                         |
        +-> Wind Vane Signal -----+--> DFR0553 A0
        |   (Yellow wire RJ11)
        |
        Vane Resistor Network
        |
        GND (to Pi Pin 6)
    ```

- Physical Connections:
1. RJ11 to Wire Breakout: You'll need an RJ11 breakout or cut the cable to access individual wires
2. Voltage Divider: Add a 10kΩ resistor between 3.3V and the wind vane signal
3. Analog Input: Connect the voltage divider output to DFR0553 pin A0

- Components You Need:
1. RJ11 Breakout Board (search: "RJ11 to screw terminal" or "RJ11 breakout")
2. 10kΩ Resistor (1/4W)
3. Breadboard or protoboard for connections
4. Jumper wires

***Anemometer and Rain bucket wiring***

For the Anemometer and Rain bucket wiring you'll need much simpler connections compared to the wind vane since they are **digital pulse sensors** (switches), not analog sensors.

## Anemometer (Wind Speed) - Digital Pulse Sensor

The anemometer is a **reed switch** that closes once per rotation. It needs:

### Required Components:
1. **Pull-up resistor: 10kΩ** (recommended external, though Pi has internal pull-ups)
2. **Debounce capacitor: 100nF (0.1μF)** (optional but recommended)

### Wiring:
```bash
Anemometer (Green wire from RJ11)
    |
    +----> Pi GPIO17 (Pin 11)
    |
    10kΩ Pull-up resistor
    |
    3.3V (Pi Pin 1)

Optional debounce:
GPIO17 ----[100nF capacitor]---- GND
```

## Rain Gauge (Rain Bucket) - Digital Pulse Sensor

The rain gauge is a **tipping bucket** with reed switch that closes on each tip (0.2794mm of rain). It needs:

### Required Components:
1. **Pull-up resistor: 10kΩ** 
2. **Debounce capacitor: 100nF (0.1μF)** (more important for rain gauge due to mechanical bouncing)

### Wiring:
```bash
Rain Gauge (separate cable, usually has 2 wires)
    |
    +----> Pi GPIO27 (Pin 13)
    |
    10kΩ Pull-up resistor
    |
    3.3V (Pi Pin 1)

Recommended debounce:
GPIO27 ----[100nF capacitor]---- GND
```

## Complete Component Shopping List:

### Essential Components:
- **2x 10kΩ resistors (1/4W)** - Pull-ups for anemometer + rain gauge
- **1x 10kΩ resistor (1/4W)** - Voltage divider for wind vane  
- **Total: 3x 10kΩ resistors**

### Recommended (for better reliability):
- **2x 100nF (0.1μF) ceramic capacitors** - Debouncing for digital inputs
- **RJ11 breakout board** - To access the weather kit wires

### Optional (for professional setup):
- **2x 1kΩ resistors** - Current limiting (extra protection)
- **Small breadboard or perfboard** - Organize all connections
- Ferrite chokes - clip on type (4x)
- TVS diode protection IC (1x)


## Updated Complete Wiring Diagram:

```bash
Raspberry Pi 5 GPIO
+------------------------+
| Pin 1  (3.3V) ---------|----+---> BME280 VCC -----> DFR0553 + (Red)
| Pin 3  (SDA)  ---------|----|-+-> BME280 SDA -----> DFR0553 D (Green)
| Pin 5  (SCL)  ---------|----|-|-> BME280 SCL -----> DFR0553 C (Blue)
| Pin 6  (GND)  ---------|----|-|--> BME280 GND -----> DFR0553 - (Black)
| Pin 11 (GPIO17) -------|----|-|--> Anemometer + 10kΩ pullup to 3.3V
| Pin 13 (GPIO27) -------|----|-|    Rain Gauge + 10kΩ pullup to 3.3V
+------------------------+    | |
                              | |
Wind Vane Circuit:            | |
3.3V -------------------------+|
    |                          |
    10kΩ (voltage divider)     |
    |                          |
    +-> Wind Vane Signal ------+--> DFR0553 A0
    |   (Yellow from RJ11)
    |
    Wind Vane Resistors
    |
    GND

Anemometer Circuit:
3.3V ----[10kΩ]---+----> GPIO17
                  |
          Anemometer Switch
                  |
                 GND

Rain Gauge Circuit:
3.3V ----[10kΩ]---+----> GPIO27
                  |
           Rain Switch
                  |
                 GND
```

## Software Configuration (Already in Your Code):

Your `weather_station.py` already has the correct GPIO setup:

```python
# GPIO setup (already correct in your code)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ANEMO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Internal pullup
GPIO.setup(RAIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)     # Internal pullup

# Interrupt handlers (already in your code)
GPIO.add_event_detect(ANEMO_PIN, GPIO.FALLING, callback=anemo_callback, bouncetime=10)
GPIO.add_event_detect(RAIN_PIN, GPIO.FALLING, callback=rain_callback, bouncetime=200)
```

## Minimum vs Recommended Setup:

### **Minimum (Pi internal pull-ups only):**
- Just connect the switch wires directly to GPIO pins
- Use Pi's internal pull-ups (`GPIO.PUD_UP`)
- **Cost: ~€0** (if you can access the wires)

### **Recommended (external components):**
- External 10kΩ pull-up resistors (more reliable)
- 100nF debounce capacitors (cleaner signals)
- **Cost: ~€2-3** for resistors + capacitors



## 📚 References

- [Weather Meter Kit product page](https://www.sparkfun.com/weather-meter-kit.html)
- [Weather Meter Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide)
- [Weather Sensor Assembly](https://cdn.sparkfun.com/assets/8/4/c/d/6/Weather_Sensor_Assembly_Updated.pdf)
- [Datasheet](https://cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf)
- [Arduino Library](https://github.com/sparkfun/SparkFun_Weather_Meter_Kit_Arduino_Library)

