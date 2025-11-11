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




## 📚 References

- [Weather Meter Kit product page](https://www.sparkfun.com/weather-meter-kit.html)
- [Weather Meter Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide)
- [Weather Sensor Assembly](https://cdn.sparkfun.com/assets/8/4/c/d/6/Weather_Sensor_Assembly_Updated.pdf)
- [Datasheet](https://cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf)
- [Arduino Library](https://github.com/sparkfun/SparkFun_Weather_Meter_Kit_Arduino_Library)

