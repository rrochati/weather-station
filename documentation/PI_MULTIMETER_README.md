# Raspberry Pi Multimeter Guide

## 🔌 Hardware Setup

### What You Have
- Raspberry Pi 5
- ADS1115 ADC (already connected via I2C)
- 10kΩ resistor (from your wind vane circuit)
- Breadboard

## 📊 Measurement Modes

### 1. Voltmeter (DC Voltage)

**Wiring:**
```
Signal wire → ADS1115 A1
Ground wire → ADS1115 GND
```

**Range:** 0V to ±4.096V (default gain)

**Use cases:**
- Test battery voltage
- Measure sensor outputs
- Debug circuit voltages

### 2. Ohmmeter (Resistance)

**Wiring:**
```
Pi 3.3V → 10kΩ resistor → ADS1115 A1 → Unknown resistor → ADS1115 GND
```

**Circuit diagram:**
```
3.3V ──[10kΩ]──┬──[R?]── GND
                │
               A1
```

**Range:** 0Ω to ~10MΩ

**How it works:**
- Uses voltage divider principle
- Measures voltage at junction
- Calculates resistance from voltage ratio

### 3. Continuity Tester

**Same wiring as ohmmeter**

**Function:**
- Beeps when resistance < 100Ω
- Perfect for testing cables and connections

### 4. Multi-Channel Monitor

Monitor 4 voltages simultaneously on A0, A1, A2, A3

## 🚀 Usage

```bash
cd /Users/ricardorocha/Documents/raspberry/weather-station
python3 scripts/pi_multimeter.py
```

## 📝 Examples

### Measure Battery Voltage
```
1. Select mode 1 (Voltmeter)
2. Connect battery + to A1
3. Connect battery - to GND
4. Read voltage on screen
```

### Measure Resistor Value
```
1. Build circuit: 3.3V → 10kΩ → A1 → Unknown R → GND
2. Select mode 2 (Ohmmeter)
3. Read resistance value
```

### Test Cable Continuity
```
1. Build circuit: 3.3V → 10kΩ → A1 → Test leads → GND
2. Select mode 3 (Continuity)
3. Touch test leads together → should beep
4. Touch to cable ends to test continuity
```

## ⚙️ Accuracy Notes

### Voltage Measurement
- Accuracy: ±0.5%
- Resolution: ~125µV (with gain 1)
- Good for most hobby projects

### Resistance Measurement
- Best range: 1kΩ to 100kΩ
- Less accurate for very low (<100Ω) or very high (>1MΩ) resistances
- To measure different ranges, change R_REF value:
  - Low resistance (0-100Ω): Use 1kΩ reference
  - High resistance (100kΩ-1MΩ): Use 100kΩ reference

## 🎯 Calibration (Optional)

To improve accuracy, measure your 10kΩ resistor with a real multimeter and update the value in the script:

```python
self.R_REF = 9850  # Your actual measured value
```

Also measure your Pi's 3.3V output:
```python
self.V_SUPPLY = 3.28  # Your actual measured value
```

## 🔧 Troubleshooting

### No readings
- Check I2C connection: `i2cdetect -y 1`
- Should see device at address 0x48 or 0x49

### Voltage readings wrong
- Check gain setting (mode 7)
- Verify ground connections

### Resistance readings wrong
- Verify reference resistor value
- Check circuit wiring
- Measure V_SUPPLY and update in code

### Continuity test doesn't beep
- Your terminal may not support beep
- Watch for ✅/❌ indicators instead

## 💡 Tips

1. **For best accuracy:** Average multiple readings (already done in code)
2. **For high voltages:** Use voltage divider to scale down (e.g., 12V → 3V)
3. **For AC voltage:** This only measures DC - need additional circuitry for AC
4. **Current measurement:** Not directly supported - measure voltage across known resistor and use Ohm's law

## 🎓 Understanding the Math

### Voltage Divider Formula
```
V_out = V_in × (R2 / (R1 + R2))

Rearranged to solve for R2:
R2 = R1 × (V_out / (V_in - V_out))
```

Where:
- V_in = 3.3V (supply)
- V_out = measured voltage at A0
- R1 = 10kΩ (reference resistor)
- R2 = unknown resistor

## 🚨 Safety

⚠️ **IMPORTANT:**
- **Maximum voltage:** 4.096V on ADS1115 input (with gain 1)
- **Never exceed:** ADS1115 is rated for ±6.144V max (gain 2/3)
- **No mains voltage:** This is only for low-voltage DC circuits
- **Always double-check:** polarity before connecting

## 📚 Advanced Usage

### Measure High Voltages (with voltage divider)

To measure 12V battery:
```
12V ──[10kΩ]──┬──[3.3kΩ]── GND
               │
              A1

V_measured × (R1 + R2) / R2 = Actual voltage
```

### Data Logging

Modify the script to log to CSV:
```python
import csv
from datetime import datetime

with open('voltages.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow([datetime.now(), voltage])
```

## 🔗 Resources

- [ADS1115 Datasheet](https://www.ti.com/lit/ds/symlink/ads1115.pdf)
- [Voltage Divider Calculator](https://www.calculator.net/voltage-divider-calculator.html)
- [Ohm's Law](https://en.wikipedia.org/wiki/Ohm%27s_law)
