#!/usr/bin/env python3
"""
Quick Anemometer Diagnostic Test
Tests GPIO17 connection and pulse detection
"""

import lgpio
import time

ANEMO_PIN = 17

def test_anemometer():
    print("🔧 Anemometer Quick Diagnostic Test")
    print("=" * 60)
    
    try:
        # Open GPIO
        gpio_handle = lgpio.gpiochip_open(0)
        print("✅ GPIO chip opened")
        
        # Claim pin
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN)
        print(f"✅ GPIO{ANEMO_PIN} claimed as input")
        
        # Read initial state
        initial_state = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
        print(f"\n📍 Current GPIO{ANEMO_PIN} state: {initial_state}")
        print(f"   0 = LOW (ground), 1 = HIGH (3.3V/pull-up)")
        
        if initial_state == 0:
            print("   ⚠️  Pin is LOW - this suggests:")
            print("      - Reed switch might be closed (magnet nearby), OR")
            print("      - Signal wire shorted to ground, OR")
            print("      - No pull-up resistance")
        else:
            print("   ✅ Pin is HIGH - normal resting state")
        
        print("\n" + "=" * 60)
        print("🔄 Monitoring for state changes...")
        print("   Spin the anemometer and watch for transitions")
        print("   Press Ctrl+C to stop")
        print("=" * 60)
        
        last_state = initial_state
        pulse_count = 0
        start_time = time.time()
        
        while True:
            current_state = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
            
            # Detect any state change
            if current_state != last_state:
                elapsed = time.time() - start_time
                if current_state == 1:
                    # Rising edge (LOW -> HIGH)
                    pulse_count += 1
                    print(f"⬆️  [{elapsed:.3f}s] RISING edge (0→1) - Pulse #{pulse_count}")
                else:
                    # Falling edge (HIGH -> LOW)
                    print(f"⬇️  [{elapsed:.3f}s] FALLING edge (1→0)")
                
                last_state = current_state
            
            time.sleep(0.001)  # Check every 1ms
            
    except KeyboardInterrupt:
        print("\n\n🛑 Test stopped by user")
        if pulse_count > 0:
            elapsed = time.time() - start_time
            rpm = (pulse_count / elapsed) * 60
            wind_speed_ms = (pulse_count / elapsed) * 0.6667
            print(f"\n📊 Results:")
            print(f"   Total pulses: {pulse_count}")
            print(f"   Test duration: {elapsed:.1f}s")
            print(f"   Pulse rate: {pulse_count/elapsed:.2f} pulses/sec")
            print(f"   Estimated RPM: {rpm:.1f}")
            print(f"   Wind speed: {wind_speed_ms:.2f} m/s ({wind_speed_ms*3.6:.1f} km/h)")
        else:
            print(f"\n❌ NO PULSES DETECTED!")
            print("\n🔍 Troubleshooting:")
            print("   1. Check Red DuPont wire from RJ45 Pin 4 to Pi GPIO 17 (Pin 11)")
            print("   2. Check Yellow DuPont wire from RJ45 Pin 5 to GND rail")
            print("   3. Verify anemometer RJ11 cable is connected")
            print("   4. Spin anemometer manually - you should hear/feel clicks")
            print("   5. Test with multimeter: measure resistance between Red & Yellow")
            print("      - Should alternate between ~0Ω (closed) and infinite (open)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        if 'gpio_handle' in locals():
            lgpio.gpiochip_close(gpio_handle)
            print("🔧 GPIO cleaned up")

if __name__ == "__main__":
    test_anemometer()

