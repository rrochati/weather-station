# Rain Bucket Sensor Setup

## 🌧️ Overview

The rain bucket is part of the SparkFun Weather Meter Kit and uses a tipping bucket mechanism to measure rainfall. Each tip of the bucket represents a specific amount of rainfall (0.2794mm).

## ⚙️ Hardware Specification

- **Type**: Tipping bucket rain gauge with reed switch
- **Resolution**: 0.2794mm per tip
- **Connection**: Reed switch between two wires
- **GPIO Pin**: GPIO27 (Pin 13)
- **Pull-up**: Internal pull-up resistor enabled

## 🔌 Wiring

Based on the SparkFun Weather Meter Kit documentation:

| RJ11 Pin | Wire Color | Function | Pi Connection |
|----------|------------|----------|---------------|
| Pin 1    | Black      | VCC (unused for rain) | Not connected |
| Pin 2    | Red        | Anemometer (unused) | Not connected |
| Pin 3    | Yellow     | Ground | Pi Pin 6 (GND) |
| Pin 4    | Green      | Rain Signal | Pi Pin 13 (GPIO27) |

### Your Specific Wiring (with Leroy Connector)

According to your color mapping:

| SparkFun Wire | Leroy Connector | DuPont Wire | Pi Connection |
|---------------|-----------------|-------------|---------------|
| Green (Rain Signal) | Black | TBD | GPIO27 (Pin 13) |
| Yellow (Ground) | Red | Purple | GND (Pin 6) |

## 🛠️ GPIO Configuration

```python
# GPIO27 configured as:
# - Input with internal pull-up resistor
# - Debounce time: 200ms (to prevent multiple triggers from single tip)
# - Edge detection: Falling edge (HIGH to LOW transition)
```

### Expected Behavior

- **Reed switch OPEN (no tip)**: GPIO reads HIGH (1)
- **Reed switch CLOSED (during tip)**: GPIO reads LOW (0)
- **Each tip**: Creates one HIGH→LOW→HIGH transition

## 📊 Measurement Logic

### Tip Detection
- Monitor GPIO27 for falling edge transitions (HIGH to LOW)
- Apply 200ms debounce to prevent bounce detection
- Increment tip counters on each valid transition

### Rain Calculation
```
Rainfall (mm) = Number of Tips × 0.2794mm
```

### Data Tracking
The rain bucket module tracks:
- **Interval tips**: Tips since last reset (usually 1 minute)
- **Daily tips**: Tips since midnight (auto-resets at 00:00)
- **Total tips**: Cumulative tips since startup

## 🧪 Testing

### 1. Wiring Test
```bash
python3 scripts/rain_bucket_test.py
# Choose option 1 for GPIO state monitoring
```

Expected results:
- GPIO27 reads HIGH (1) when bucket is idle
- GPIO27 reads LOW (0) when manually triggering bucket
- State changes detected when manually tipping bucket

### 2. Functional Test
```bash
python3 scripts/rain_bucket_test.py
# Choose option 2 for full rain bucket test
```

Expected results:
- Tips detected and logged
- Rainfall amounts calculated correctly
- Counters increment properly

## 🔧 Troubleshooting

### No Tips Detected
1. **Check wiring connections**
   - Verify GPIO27 connection to rain signal
   - Ensure ground connection is solid
   - Check for loose connections

2. **Test GPIO state**
   ```bash
   python3 scripts/rain_bucket_test.py
   # Run wiring test to see GPIO state changes
   ```

3. **Verify rain bucket mechanism**
   - Manually tip the bucket and listen for click
   - Check if bucket moves freely
   - Ensure reed switch is working

### False Tips (Too Many)
1. **Electrical noise**: Add capacitor filter (100nF ceramic)
2. **Bounce**: Increase debounce time in code
3. **Loose connections**: Secure all wiring

### Inconsistent Tips
1. **Power supply noise**: Check 3.3V stability
2. **Long cable runs**: Add pull-up resistor at sensor end
3. **Environmental**: Check for vibration or wind effects

## 📈 Calibration

The 0.2794mm per tip specification is from SparkFun and should be accurate for the official Weather Meter Kit. If you need to calibrate:

1. **Manual calibration**: Use known water volume
2. **Comparison method**: Compare with nearby weather station
3. **Long-term validation**: Check against meteorological data

## 🔄 Integration

The rain bucket integrates with the weather station as follows:

1. **Initialization**: Set up GPIO and counters during startup
2. **Monitoring**: Continuously monitor for tips in background
3. **Data collection**: Read interval data every minute
4. **Database storage**: Store rainfall amounts in SQLite database
5. **Daily reset**: Automatically reset daily counter at midnight

## 📚 References

- [SparkFun Weather Meter Kit](https://www.sparkfun.com/products/15901)
- [Weather Meter Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide)
- [Datasheet](https://cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf)