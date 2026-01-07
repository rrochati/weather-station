# Cable Continuity Testing Guide

## 🎯 Goal
Test each wire in the CAT6 cable between RJ45 breakout 1 (Pi end) and RJ45 breakout 3 (sensor end).

## 🔌 Test Circuit Setup

### **At the Pi/Breadboard:**

```
Pi 3.3V (Pin 1) → 10kΩ resistor → ADS1115 A2 → Test lead (alligator clip)
                                                        |
                                                        → Breakout 1 pin to test
                                                        
                                    Cable under test (long run)
                                                        
                                                        → Breakout 3 corresponding pin
                                                        |
Pi GND (Pin 6)  ←  Test lead (alligator clip)  ←←←←←←←←
```

### **Physical Connections at Pi:**

#### On Breadboard:
1. **3.3V supply**: Pi Pin 1 (3.3V) → Power rail
2. **10kΩ resistor**: Power rail → Row X Column A
3. **ADS1115 A2**: Row X Column C (same row as resistor)
4. **Test probe 1**: Row X Column E → Long alligator clip wire (RED)
5. **Test probe 2**: GND rail → Long alligator clip wire (BLACK)

#### Connection at RJ45 Breakout 1 (Pi end):
- **RED clip** → Touch to pin being tested (1, 2, 3, etc.)
- Keep breakout 1 connected or disconnected from breadboard (your choice)

#### Connection at RJ45 Breakout 3 (Sensor end):
- **BLACK clip** → Touch to corresponding pin on breakout 3

---

## 📋 Testing Procedure

### **Step 1: Setup the Circuit**
```bash
# On breadboard:
1. Connect Pi Pin 1 (3.3V) to power rail
2. Connect 10kΩ resistor from power rail to breadboard row (e.g., Row 25A)
3. Connect ADS1115 A2 to same row (e.g., Row 25C)
4. Connect RED alligator clip to same row (e.g., Row 25E)
5. Connect BLACK alligator clip to Pi Pin 6 (GND)
```

### **Step 2: Run the Multimeter Script**
```bash
cd /Users/ricardorocha/Documents/raspberry/weather-station
python3 scripts/pi_multimeter.py

# Choose option 4: Cable Continuity Test (A2)
# This uses A2 since A1 is connected to the wind vane
```

### **Step 3: Test Each Wire**

**You should test ALL 8 wires in your CAT6 cable:**

| Test # | Breakout 1 Pin | CAT6 Color   | Function          | Breakout 3 Pin | Expected Result |
|--------|----------------|--------------|-------------------|----------------|-----------------|
| 1      | Pin 1          | White/Orange | Power (BME280)    | Pin 1          | ✅ CONTINUITY   |
| 2      | Pin 2          | Orange       | GND (BME280)      | Pin 2          | ✅ CONTINUITY   |
| 3      | Pin 3          | White/Green  | I2C Clock         | Pin 3          | ✅ CONTINUITY   |
| 4      | Pin 4          | Blue         | I2C Data          | Pin 4          | ✅ CONTINUITY   |
| 5      | Pin 5          | White/Blue   | Vane Signal       | Pin 5          | ✅ CONTINUITY   |
| 6      | Pin 6          | Green        | Not in use        | Pin 6          | ✅ CONTINUITY   |
| 7      | Pin 7          | White/Brown  | Anemometer Signal | Pin 7          | ✅ CONTINUITY   |
| 8      | Pin 8          | Brown        | Rain Signal       | Pin 8          | ✅ CONTINUITY   |

### **Step 4: For Each Wire:**

1. **Touch RED clip** to the pin on breakout 1
2. **Touch BLACK clip** to the corresponding pin on breakout 3
3. **Watch the screen**:
   - ✅ **CONTINUITY!** means wire is good (typically < 5Ω)
   - ❌ **No continuity** means wire is broken or bad connection
4. **Note the resistance value** shown in parentheses
5. **Record results** in table above

---

## 🔍 Troubleshooting Results

### **Good Results:**
- Resistance: 0.1Ω to 5Ω → ✅ Wire is good
- Beep sound when connecting → ✅ Perfect continuity

### **Bad Results:**
- "OPEN (>10MΩ)" → ❌ Wire is broken or not connected
- Resistance > 100Ω → ⚠️ Poor connection, check connectors
- No beep → ❌ No continuity

### **Intermittent Results:**
- Reading changes when you wiggle cable → ⚠️ Loose connection
- Continuity comes and goes → ⚠️ Bad crimp or broken wire

---

## 🛠️ Common Issues & Fixes

### **Issue: All wires show OPEN**
**Causes:**
- Test leads not making contact
- 10kΩ resistor not connected properly
- ADS1115 not powered or not on I2C

**Fix:**
1. Test the setup: Touch RED and BLACK clips together → Should show ~0Ω
2. Check ADS1115: `i2cdetect -y 1` → Should see device at 0x48
3. Verify 10kΩ resistor is in circuit

### **Issue: Some wires good, some bad**
**Causes:**
- Bad crimps on RJ45 connector
- Damaged cable (cut, pinched, crushed)
- Loose pins in RJ45 keystone module

**Fix:**
1. Re-crimp RJ45 connectors
2. Check cable for visible damage
3. Test with a different cable to isolate problem

### **Issue: Intermittent readings**
**Causes:**
- Loose connection in RJ45 breakout
- Damaged wire strand (partial break)
- Bad punch-down on keystone

**Fix:**
1. Wiggle connections while testing to find loose spot
2. Re-seat all RJ45 connectors
3. Replace damaged section of cable

---

## 📊 Expected Resistance Values

For a good CAT6 cable:
- **Short runs (< 5m)**: 0.1Ω to 1Ω per wire
- **Medium runs (5-20m)**: 1Ω to 5Ω per wire  
- **Long runs (20-50m)**: 5Ω to 10Ω per wire

Your cable resistance will depend on length and wire gauge (CAT6 is typically 23 AWG).

---

## 🎓 Understanding the Test

### **How it works:**
1. 3.3V flows through 10kΩ resistor → creates voltage at A2
2. If wire has continuity → current flows to ground
3. Voltage divider formed: R_ref (10kΩ) and R_wire (small)
4. Low R_wire → low voltage at A2 → continuity detected
5. High R_wire → high voltage at A2 → no continuity

### **Math behind it:**
```
V_A2 = 3.3V × (R_wire / (10kΩ + R_wire))

Good wire (1Ω):   V_A2 ≈ 0.0003V → Continuity ✅
Broken wire (∞Ω): V_A2 ≈ 3.3V    → Open circuit ❌
```

---

## 💡 Pro Tips

1. **Test both directions**: Sometimes a wire works one way but not the other (rare, but possible with broken strands)

2. **Document everything**: Write down resistance values for each pin - helps track degradation over time

3. **Test under stress**: Wiggle the cable while testing to catch intermittent issues

4. **Compare readings**: All 8 wires should have similar resistance (within 1-2Ω)

5. **Test between pins**: Also test between adjacent pins with both clips at same end:
   - Should show OPEN (no continuity)
   - If continuity exists → wires are shorted together

---

## 📝 Test Results Template

```
Date: _______________
Cable: RJ45 Breakout 1 → RJ45 Breakout 3
Length: ~_____ meters

Pin | Color        | Resistance | Status | Notes
----|--------------|------------|--------|-------
1   | White/Orange | _____Ω     | ✅/❌  | 
2   | Orange       | _____Ω     | ✅/❌  | 
3   | White/Green  | _____Ω     | ✅/❌  | 
4   | Blue         | _____Ω     | ✅/❌  | 
5   | White/Blue   | _____Ω     | ✅/❌  | 
6   | Green        | _____Ω     | ✅/❌  | 
7   | White/Brown  | _____Ω     | ✅/❌  | 
8   | Brown        | _____Ω     | ✅/❌  | 

Short test (between pins at same end):
Pin 1-2: OPEN ✅/❌
Pin 2-3: OPEN ✅/❌
Pin 3-4: OPEN ✅/❌
(etc...)
```

---

## 🔗 Related Documentation

- [Pi Multimeter Guide](PI_MULTIMETER_README.md)
- [New Wiring Documentation](NEW_WIRING.md)
- [Troubleshooting Guide](Troubleshooting.md)
