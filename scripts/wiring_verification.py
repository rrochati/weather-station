#!/usr/bin/env python3
"""
Step-by-Step Anemometer Wiring Verification
Guides through systematic troubleshooting of the connection chain
"""

import lgpio
import time
import signal
import sys

ANEMO_PIN = 17
gpio_handle = None

def signal_handler(sig, frame):
    print("\n🛑 Test stopped by user")
    cleanup_and_exit()

def cleanup_and_exit():
    global gpio_handle
    if gpio_handle is not None:
        lgpio.gpiochip_close(gpio_handle)
    sys.exit(0)

def test_continuity_step(step_name, instruction):
    """Test a specific connection step"""
    print(f"\n🔧 {step_name}")
    print("="*50)
    print(instruction)
    print("\nPress Enter when ready to test...")
    input()
    
    # Monitor for 20 seconds
    print("🎯 Monitoring for 20 seconds...")
    changes = 0
    last_level = -1
    
    for i in range(200):  # 20 seconds, 10 readings per second
        current_level = lgpio.gpio_read(gpio_handle, ANEMO_PIN)
        
        if current_level != last_level and last_level != -1:
            changes += 1
            timestamp = time.strftime("%H:%M:%S")
            print(f"   [{timestamp}] Signal change: {last_level} → {current_level}")
        
        last_level = current_level
        time.sleep(0.1)
    
    print(f"\n📊 Result: {changes} signal changes detected")
    
    if changes > 0:
        print("✅ This connection is working!")
        return True
    else:
        print("❌ No signal detected at this step")
        return False

def main():
    global gpio_handle
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔍 STEP-BY-STEP ANEMOMETER WIRING VERIFICATION")
    print("="*60)
    print("This will test each connection point systematically")
    print("to find exactly where the signal is lost.")
    print()
    
    try:
        # Setup GPIO
        gpio_handle = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(gpio_handle, ANEMO_PIN)
        
        print("✅ GPIO setup complete")
        
        # Step 1: Direct Pi connection test
        step1_ok = test_continuity_step(
            "STEP 1: Direct Pi Connection Test",
            """
📌 Test: Verify Pi GPIO is working
🔧 Action: 
   1. Take a jumper wire
   2. Touch one end to Pi Pin 11 (GPIO17)
   3. Touch other end to Pi Pin 6 (GND)
   4. Repeatedly connect/disconnect while test runs
   
Expected: Should see signal changes when touching GND
            """
        )
        
        if not step1_ok:
            print("❌ STOP: Basic GPIO connection failed!")
            print("   Check if you're using the correct pins")
            return
        
        # Step 2: Test your extension cable
        step2_ok = test_continuity_step(
            "STEP 2: Extension Cable Test", 
            """
📌 Test: Verify your long extension cable
🔧 Action:
   1. Disconnect anemometer from RJ11 connector
   2. At the Pi end, connect your signal wire (currently to GPIO17)
   3. At the Pi end, connect your ground wire (currently to GND) 
   4. At the OTHER end, manually connect/disconnect the two wires
   
Expected: Signal changes when connecting wires at far end
            """
        )
        
        if not step2_ok:
            print("❌ Extension cable has a break or wrong wiring!")
            print("   Check continuity of your long cable")
            return
            
        # Step 3: RJ11 Connector test
        step3_ok = test_continuity_step(
            "STEP 3: RJ11 Connector Test",
            """
📌 Test: Verify RJ11 breakout connector wiring
🔧 Action:
   1. Connect anemometer to RJ11 connector 
   2. At RJ11 connector, identify the two wires going to Pi:
      - Signal wire (should go to GPIO17)
      - Ground wire (should go to GND)
   3. Manually short these two wires together repeatedly
   
Expected: Signal changes when shorting the wires
            """
        )
        
        if not step3_ok:
            print("❌ RJ11 connector wiring issue!")
            print("   Check your color mapping table in documentation")
            return
        
        # Step 4: Anemometer mechanical test
        step4_ok = test_continuity_step(
            "STEP 4: Anemometer Mechanical Test",
            """
📌 Test: Verify anemometer reed switch operation
🔧 Action:
   1. Everything connected as normal
   2. Hold anemometer in your hand
   3. SLOWLY spin it by hand (1 revolution per 2-3 seconds)
   4. Try different spinning speeds
   5. Try spinning both directions
   
Expected: Signal changes during spinning
            """
        )
        
        if not step4_ok:
            print("❌ Anemometer mechanical issue!")
            print("   Possible problems:")
            print("   - Reed switch is broken")
            print("   - Magnet is missing or weak") 
            print("   - Mechanical obstruction")
            print("   - Wrong wire connections in RJ11")
        else:
            print("✅ SUCCESS: Anemometer is working!")
            print("   The original test scripts should work now")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cleanup_and_exit()

if __name__ == "__main__":
    main()