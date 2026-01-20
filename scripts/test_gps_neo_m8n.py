#!/usr/bin/env python3
"""
Quick test script for NEO-M8N GPS module
Run this to verify GPS is working properly
"""

import sys
import time
import os

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from modules.gps_neo_m8n import NEOM8N
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_gps_continuous():
    """Test GPS with continuous updates"""
    print("\n" + "="*60)
    print("NEO-M8N GPS Continuous Test")
    print("="*60)
    print("\nPress Ctrl+C to stop\n")
    
    # Try GPSD first
    gps = NEOM8N(use_gpsd=True)
    
    if not gps.connect():
        print("GPSD connection failed, trying serial...")
        gps = NEOM8N(use_gpsd=False)
        if not gps.connect():
            print("ERROR: Could not connect to GPS!")
            print("\nTroubleshooting steps:")
            print("1. Check physical connections")
            print("2. Verify UART is enabled: ls -l /dev/ttyAMA0")
            print("3. Check GPSD: sudo systemctl status gpsd")
            print("4. Test raw data: cat /dev/ttyAMA0")
            return
    
    print("Connected to GPS. Waiting for fix...\n")
    
    fix_acquired = False
    update_count = 0
    
    try:
        while True:
            position = gps.get_position(timeout=5)
            
            if position:
                if not fix_acquired:
                    print("\n✓ GPS FIX ACQUIRED!\n")
                    fix_acquired = True
                
                update_count += 1
                
                print(f"Update #{update_count} - {time.strftime('%H:%M:%S')}")
                print(f"  Position: {position['latitude']:.6f}°, {position['longitude']:.6f}°")
                
                if position['altitude']:
                    print(f"  Altitude: {position['altitude']:.1f} m")
                
                if position['satellites']:
                    print(f"  Satellites: {position['satellites']}")
                
                if position['speed']:
                    print(f"  Speed: {position['speed']:.1f} m/s ({position['speed']*3.6:.1f} km/h)")
                
                if position['hdop']:
                    print(f"  HDOP: {position['hdop']:.2f}")
                
                print()
            else:
                if fix_acquired:
                    print(f"⚠ Lost GPS fix - {time.strftime('%H:%M:%S')}")
                else:
                    print(f"⏳ Waiting for GPS fix... {time.strftime('%H:%M:%S')}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    finally:
        gps.close()
        print(f"Total updates received: {update_count}")


def test_gps_single():
    """Single GPS reading test"""
    print("\n" + "="*60)
    print("NEO-M8N GPS Single Reading Test")
    print("="*60 + "\n")
    
    gps = NEOM8N(use_gpsd=True)
    
    if not gps.connect():
        print("GPSD failed, trying serial...")
        gps = NEOM8N(use_gpsd=False)
        if not gps.connect():
            print("ERROR: Could not connect to GPS!")
            return
    
    print("Waiting for GPS fix (timeout: 60 seconds)...")
    print("Ensure GPS antenna has clear sky view!\n")
    
    start = time.time()
    position = gps.get_position(timeout=60)
    elapsed = time.time() - start
    
    if position:
        print(f"\n✓ GPS fix acquired in {elapsed:.1f} seconds\n")
        print("GPS Data:")
        print("-" * 40)
        print(f"  Latitude:     {position['latitude']:.6f}°")
        print(f"  Longitude:    {position['longitude']:.6f}°")
        
        if position['altitude']:
            print(f"  Altitude:     {position['altitude']:.1f} m")
        
        if position['satellites']:
            print(f"  Satellites:   {position['satellites']}")
        
        if position['fix_quality']:
            quality = ['Invalid', 'GPS', 'DGPS', 'PPS', 'RTK', 'Float RTK', 'Estimated', 'Manual', 'Simulation']
            q_idx = min(position['fix_quality'], len(quality)-1)
            print(f"  Fix Quality:  {quality[q_idx]} ({position['fix_quality']})")
        
        if position['time']:
            print(f"  Time:         {position['time']}")
        
        if position['hdop']:
            print(f"  HDOP:         {position['hdop']:.2f}")
        
        # Show Google Maps link
        print(f"\n  Google Maps:  https://www.google.com/maps?q={position['latitude']},{position['longitude']}")
        
    else:
        print(f"\n✗ No GPS fix acquired after {elapsed:.1f} seconds")
        print("\nTroubleshooting:")
        print("  • Ensure antenna has unobstructed sky view")
        print("  • Cold start can take 2-5 minutes")
        print("  • Check connections (TX/RX must be crossed)")
        print("  • Verify power LED is on")
        print("  • Check raw data: cat /dev/ttyAMA0")
    
    gps.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test NEO-M8N GPS module')
    parser.add_argument('--continuous', '-c', action='store_true',
                       help='Continuous updates (default: single reading)')
    
    args = parser.parse_args()
    
    if args.continuous:
        test_gps_continuous()
    else:
        test_gps_single()
