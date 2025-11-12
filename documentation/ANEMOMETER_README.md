# SparkFun Weather Meter Kit Anemometer Setup

## 🧩 Kit Overview

![alt text](images/sparkfun_weather_kit.jpeg)


## ⚙️ Hardware and Wiring

***SparkFun Weather Meter Kit Anemometer Wiring***

As the wind vane setup is more complex, let's begin with anemometer.

## 🎯 **Anemometer-Only Setup (Minimal Start):**

### **What You Need:**

### Hardware:
- Anemometer and wind vane from your SparkFun kit
- RJ11 breakout (I use on from Leroy Merlin) to access the wires
- Long cable (your 10-20m run)


### **Simplified Wiring:**
- Anemometer RJ 11 ---> Wind Vane RJ11 female
- Wind Vane RJ 11 ---> RJ11 breakout
- Wind Vane RJ 11 Pin 2 (Red) ---> GPIO Pin 11 (GPIO17)
- Wind Vane RJ 11 Pin 3 (Yellow) ---> GNd (breadboard - column row 11)


#### Warning about wiring ####
Watch closely your breakout connector for RJ11.
The one I'm using (from Leroy Merlin) does not follow the color schema as the Sparkfun cable

And, to add more complexibility, I will use different DuPont cable collors. Look for collors next to the anemometer on my cables

PS: And the extension uses another color pattern :)

    | RJ11 Pin| Wire Color | Function                | Connection                     | Leroy conector | DuPont Wire soldered |
    |---------|------------|-------------------------| ------------------------------ | -------------- | -------------------- |
    | Pin 1	  | Black      | VCC (Power)             | Connect to 3.3V                | Yellow         | Yellow Female        |
    | Pin 2	  | Red        | Wind Speed (Anemometer) | Connect to Pi Pin 11 (GPIO 17) | Green          | Green Female         |
    | Pin 3	  | Yellow     | Ground                  | Connect to GND                 | Red            | Purple Male          |
    | Pin 4	  | Green	   | Wind Vane Signal        | Connect to DFR0553 A0          | Black          | Brown Male           |

So, using this RJ11 breakout:
- Yellow on connector, dupont Purple ---> GND (breadboard - column row 11)
- Red on connector, dupont Green -> GPIO Pin 11 (GPIO17)


#### For Long Cable Run - Minimal Protection ####

At Pi End:
- 100nF capacitor: GPIO17 to GND (debounce/filter)
- Ferrite choke on cable (reduces EMI)

At Sensor End:  
- Keep connections weatherproof
- Ensure good ground connection

#### 🛠️ **Practical Implementation on a Breadboard:**
- PI GPIIO 6 (pin 6) -> black wire -> GND Rail line 1 (alredy done for another module)
- GND Rail line 14: Capacitor leg 2 (filters to ground)
- Line 14 Row A: Capacitor leg 1 (filter input)
- Pi Pin 11 (GPIO17) -> DuPont Orange -> Line 14 Row B (signal input)  
- Wind Vane connertor Red -> RJ11 breakout Green wire -> Dupont Brown -> Line 14 Row C (signal source)
- Wind Vane connertor Yellow -> RJ11 breakout Red wire -> Dupont Purple -> GND Rail line 11

#### 🔍 What is "Bounce" in Switches? and why it's important for your anemometer setup ####
- If you are interested on details, check **ANEMOMETER_DETAILS.md**

## 📊 **Testing Process:**

### **Step 1: Bench Test (Short Cable)**
```bash
1. Connect Anemometer and Wind Vane, Wind Vane as describe in **Practical Implementation on a Breadboard:** step;
2. Run scripts/anemometer_signal_test.py and scripts/gpio17_diagnostic.py
3. Spin anemometer by hand and verify pulse counting
```

### **Step 2: Outdoor Installation**
```bash
1. Mount anemometer outdoors
2. Monitor data for 24-48 hours
3. Check for reasonable wind speed values
4. Look for electrical noise or interference
```

### **Step 3: Long Cable Test**
```bash
1. Install long cable run
2. Test pulse detection at various spin rates  
3. Monitor for false pulses or missed pulses
4. Add protection components if needed
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


## 💡 **Anemometer-Specific Tips:**

From **Weather Meter Hookup Guide**:
     "The wind moves the cups on the anemometer, which in turn, rotate a enclosed magnet. The magnet closes a reed switch on each rotation, which is reflected on the output. You can measure this on the two inner conductors of the RJ11 connector (pins 2 and 3), using a digital counter or interrupt pins on your microcontroller. To convert this into a functional wind speed, use the conversion of 1.492 mph = 1 switch closure/second. For those in metric land, this is 2.4 km/h."

So to convert 2.4 km/h use the following table: 
| Unit | Operation | Value |
| ---- | --------- | ----- |
| m/s | / | 0.6667 |
| km/h | TBD 0.27778 |
| mph | TBD | 1.49129 |
| knots | TBD| 1.2959 |

And to convert back multiply to:
| Unit  | Equivalent of 1 m/s |
| ----- | ------------------- |
| km/h  | 3.6 |
| mph   | 2.237 |
| knots | 1.944 |



## 📚 References

- [Weather Meter Kit product page](https://www.sparkfun.com/weather-meter-kit.html)
- [Weather Meter Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide)
- [Weather Sensor Assembly](https://cdn.sparkfun.com/assets/8/4/c/d/6/Weather_Sensor_Assembly_Updated.pdf)
- [Datasheet](https://cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf)
- [Arduino Library](https://github.com/sparkfun/SparkFun_Weather_Meter_Kit_Arduino_Library)

