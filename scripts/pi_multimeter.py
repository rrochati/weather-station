#!/usr/bin/env python3
"""
Simple Raspberry Pi Multimeter
Uses ADS1115 for voltage measurements

Hardware Setup:
- ADS1115 connected via I2C
- For voltage measurement: Connect signal to A1, ground to GND
- For resistance: Use 10kΩ reference resistor in series (3.3V → 10kΩ → A1 → Unknown R → GND)
- For continuity: Check if resistance < 100Ω

Voltage Ranges (ADS1115 Gain settings):
- Gain 2/3: ±6.144V (for 5V circuits)
- Gain 1:   ±4.096V (default, good for 3.3V circuits)
- Gain 2:   ±2.048V
- Gain 4:   ±1.024V
- Gain 8:   ±0.512V
- Gain 16:  ±0.256V
"""

import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import sys

class PiMultimeter:
    def __init__(self):
        """Initialize the multimeter"""
        print("🔧 Initializing Pi Multimeter...")
        
        # I2C setup
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # ADS1115 setup
        self.ads = ADS1115(i2c)
        self.ads.gain = 1  # ±4.096V range (default)
        
        # Reference resistor value for resistance measurements (Ohms)
        self.R_REF = 10000  # 10kΩ
        self.V_SUPPLY = 3.3  # Supply voltage
        
        print("✅ ADS1115 initialized")
        print(f"✅ Reference resistor: {self.R_REF}Ω")
        print(f"✅ Supply voltage: {self.V_SUPPLY}V\n")
    
    def measure_voltage(self, channel=0, samples=10):
        """
        Measure DC voltage on specified channel
        
        Args:
            channel: ADC channel (0-3) corresponding to A0-A3
            samples: Number of samples to average
            
        Returns:
            Average voltage in volts
        """
        chan = AnalogIn(self.ads, channel)
        
        voltages = []
        for _ in range(samples):
            voltages.append(chan.voltage)
            time.sleep(0.01)
        
        return sum(voltages) / len(voltages)
    
    def measure_resistance(self, channel=0, samples=10):
        """
        Measure resistance using voltage divider method
        
        Circuit: 3.3V → R_REF (10kΩ) → [Measure here at A1] → R_UNKNOWN → GND
        
        Formula: R_unknown = R_ref * (V_measured / (V_supply - V_measured))
        
        Args:
            channel: ADC channel where voltage is measured
            samples: Number of samples to average
            
        Returns:
            Resistance in ohms, or None if open circuit
        """
        v_measured = self.measure_voltage(channel, samples)
        
        # Check for open circuit
        if v_measured > (self.V_SUPPLY - 0.1):
            return None  # Open circuit (infinite resistance)
        
        if v_measured < 0.01:
            return 0  # Short circuit
        
        # Calculate unknown resistance using voltage divider formula
        r_unknown = self.R_REF * (v_measured / (self.V_SUPPLY - v_measured))
        
        return r_unknown
    
    def continuity_test(self, channel=0, threshold=100):
        """
        Test for continuity (low resistance)
        
        Args:
            channel: ADC channel
            threshold: Resistance threshold in ohms
            
        Returns:
            True if continuity exists (R < threshold)
        """
        resistance = self.measure_resistance(channel)
        
        if resistance is None:
            return False
        
        return resistance < threshold
    
    def format_resistance(self, r):
        """Format resistance value with appropriate units"""
        if r is None:
            return "OPEN (>10MΩ)"
        elif r < 1000:
            return f"{r:.1f}Ω"
        elif r < 1000000:
            return f"{r/1000:.2f}kΩ"
        else:
            return f"{r/1000000:.2f}MΩ"
    
    def voltmeter_mode(self):
        """Continuous voltage monitoring mode"""
        print("\n" + "="*60)
        print("⚡ VOLTMETER MODE")
        print("="*60)
        print("Connect signal to A1, ground to ADS1115 GND")
        print("Current gain setting: ±4.096V range")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                voltage = self.measure_voltage(channel=1, samples=5)
                print(f"📊 Voltage: {voltage:+7.4f}V", end='\r')
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("\n")
    
    def ohmmeter_mode(self):
        """Continuous resistance monitoring mode"""
        print("\n" + "="*60)
        print("📏 OHMMETER MODE")
        print("="*60)
        print(f"Circuit: 3.3V → {self.R_REF}Ω → A1 → Unknown R → GND")
        print("1. Connect 10kΩ resistor from 3.3V to A1")
        print("2. Connect unknown resistor from A1 to GND")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                resistance = self.measure_resistance(channel=1, samples=5)
                r_str = self.format_resistance(resistance)
                print(f"📊 Resistance: {r_str:>15}", end='\r')
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("\n")
    
    def continuity_mode(self):
        """Continuity testing mode with audio feedback"""
        print("\n" + "="*60)
        print("🔌 CONTINUITY TEST MODE")
        print("="*60)
        print(f"Circuit: 3.3V → {self.R_REF}Ω → A1 → Test leads → GND")
        print("Setup same as ohmmeter mode")
        print("Beep indicates continuity (R < 100Ω)")
        print("Press Ctrl+C to stop\n")
        
        try:
            last_state = False
            while True:
                has_continuity = self.continuity_test(channel=1)
                resistance = self.measure_resistance(channel=1, samples=3)
                
                if has_continuity:
                    r_str = self.format_resistance(resistance)
                    print(f"✅ CONTINUITY! ({r_str})  ", end='\r')
                    
                    # Beep on transition to continuity
                    if not last_state:
                        print("\a", end='')  # Terminal beep
                        sys.stdout.flush()
                else:
                    r_str = self.format_resistance(resistance)
                    print(f"❌ No continuity ({r_str})  ", end='\r')
                
                last_state = has_continuity
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n")
    
    def multi_channel_voltage(self):
        """Monitor all 4 channels simultaneously"""
        print("\n" + "="*60)
        print("📺 4-CHANNEL VOLTAGE MONITOR")
        print("="*60)
        print("Monitoring A0, A1, A2, A3")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                v0 = self.measure_voltage(0, samples=3)
                v1 = self.measure_voltage(1, samples=3)
                v2 = self.measure_voltage(2, samples=3)
                v3 = self.measure_voltage(3, samples=3)
                
                print(f"A0: {v0:+6.3f}V | A1: {v1:+6.3f}V | A2: {v2:+6.3f}V | A3: {v3:+6.3f}V", end='\r')
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("\n")
    
    def run(self):
        """Main menu"""
        while True:
            print("\n" + "="*60)
            print("🔬 RASPBERRY PI MULTIMETER")
            print("="*60)
            print("Choose a mode:")
            print("  1. Voltmeter (DC Voltage)")
            print("  2. Ohmmeter (Resistance)")
            print("  3. Continuity Test")
            print("  4. 4-Channel Voltage Monitor")
            print("  5. Single Voltage Reading")
            print("  6. Single Resistance Reading")
            print("  7. Change Gain (Voltage Range)")
            print("  0. Exit")
            print("="*60)
            
            try:
                choice = input("\nEnter choice: ").strip()
                
                if choice == '1':
                    self.voltmeter_mode()
                elif choice == '2':
                    self.ohmmeter_mode()
                elif choice == '3':
                    self.continuity_mode()
                elif choice == '4':
                    self.multi_channel_voltage()
                elif choice == '5':
                    v = self.measure_voltage(1)
                    print(f"\n📊 Voltage on A1: {v:+.4f}V")
                elif choice == '6':
                    r = self.measure_resistance(1)
                    print(f"\n📊 Resistance: {self.format_resistance(r)}")
                elif choice == '7':
                    self.change_gain()
                elif choice == '0':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def change_gain(self):
        """Change ADS1115 gain setting"""
        print("\n" + "="*60)
        print("⚙️  GAIN SETTINGS")
        print("="*60)
        print("  1. Gain 2/3 → ±6.144V (for 5V circuits)")
        print("  2. Gain 1   → ±4.096V (default, 3.3V circuits)")
        print("  3. Gain 2   → ±2.048V (higher precision)")
        print("  4. Gain 4   → ±1.024V")
        print("  5. Gain 8   → ±0.512V")
        print("  6. Gain 16  → ±0.256V (max precision)")
        print("="*60)
        
        choice = input("\nEnter choice: ").strip()
        
        gain_map = {
            '1': (2/3, "±6.144V"),
            '2': (1, "±4.096V"),
            '3': (2, "±2.048V"),
            '4': (4, "±1.024V"),
            '5': (8, "±0.512V"),
            '6': (16, "±0.256V"),
        }
        
        if choice in gain_map:
            self.ads.gain = gain_map[choice][0]
            print(f"✅ Gain set to {gain_map[choice][1]}")
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║         🔬 RASPBERRY PI MULTIMETER 🔬                    ║
║                                                          ║
║  A simple multimeter using ADS1115 ADC                  ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        multimeter = PiMultimeter()
        multimeter.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("\nTroubleshooting:")
        print("1. Check ADS1115 I2C connection")
        print("2. Run 'i2cdetect -y 1' to verify ADS1115 is detected")
        print("3. Check wiring and power supply")
