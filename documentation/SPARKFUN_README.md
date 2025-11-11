# Weather Meter Kit setup

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

| Front wiev | Pin 1 | Pin 2 | Pin 3 | Pin 4 |
| -----------|------------------| ------------------| -----------------| ------------------|
| Anemometer | Black | Red  | Yellow | Green |
| Leroy conector | Yellow | Green | Red | Black |
| DuPont Wire soldered | Yellow Female | Green Female  | Purple Male | Brown Male |

So, using this RJ11 breakout:
- Yellow on connector, dupont Purple ---> GNd (breadboard - column row 11)
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

#### **Component Specs:**
```bash
Capacitor: 100nF (0.1μF) ceramic capacitor
- Voltage: 50V (overkill, but safe)
- Type: Ceramic (X7R or C0G)
- Package: Through-hole or 0805 SMD
- Cost: €0.05-0.10
```
## 📊 **Testing Process:**

### **Step 1: Bench Test (Short Cable)**
```bash
1. Connect Anemometer and Wind Vane, Wind Vane as describe in **Practical Implementation on a Breadboard:** step;
2. Run scripts/anemometer_signal_test.py and scripts/gpio17_diagnostic.py
3. Spin anemometer by hand and verify pulse counting
```



## 📚 References

- [Weather Meter Kit product page](https://www.sparkfun.com/weather-meter-kit.html)
- [Weather Meter Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide)
- [Weather Sensor Assembly](https://cdn.sparkfun.com/assets/8/4/c/d/6/Weather_Sensor_Assembly_Updated.pdf)
- [Datasheet](https://cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf)
- [Arduino Library](https://github.com/sparkfun/SparkFun_Weather_Meter_Kit_Arduino_Library)

