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
