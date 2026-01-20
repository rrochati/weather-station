#!/usr/bin/env python3
"""
Direct serial GPS test - bypasses GPSD to test GPS module directly
"""

import serial
import time
import sys

def analyze_nmea_sentence(sentence):
    """Parse and display NMEA sentence info"""
    if sentence.startswith('$GPGGA') or sentence.startswith('$GNGGA'):
        parts = sentence.split(',')
        if len(parts) > 6:
            fix_quality = parts[6] if len(parts) > 6 else '0'
            num_sats = parts[7] if len(parts) > 7 else '0'
            lat = parts[2] if len(parts) > 2 else ''
            lon = parts[4] if len(parts) > 4 else ''
            
            fix_types = {
                '0': 'No fix',
                '1': 'GPS fix',
                '2': 'DGPS fix',
                '3': 'PPS fix',
                '4': 'RTK',
                '5': 'Float RTK',
                '6': 'Estimated',
                '8': 'Simulation',
                '9': 'WAAS'
            }
            
            fix_desc = fix_types.get(fix_quality, 'Unknown')
            
            print(f"  GGA: Fix={fix_desc} ({fix_quality}), Satellites={num_sats}", end='')
            if lat and lon:
                print(f", Position: {lat},{lon}")
            else:
                print(" - No position yet")
            return True
    
    elif sentence.startswith('$GPGSA') or sentence.startswith('$GNGSA'):
        parts = sentence.split(',')
        if len(parts) > 2:
            mode = parts[2] if len(parts) > 2 else '1'
            mode_types = {'1': 'No fix', '2': '2D fix', '3': '3D fix'}
            print(f"  GSA: {mode_types.get(mode, 'Unknown')} (mode {mode})")
            return True
    
    elif sentence.startswith('$GPGSV') or sentence.startswith('$GNGSV'):
        parts = sentence.split(',')
        if len(parts) > 3:
            total_sats = parts[3] if len(parts) > 3 else '0'
            print(f"  GSV: {total_sats} satellites in view")
            return True
    
    elif sentence.startswith('$GPRMC') or sentence.startswith('$GNRMC'):
        parts = sentence.split(',')
        if len(parts) > 2:
            status = parts[2] if len(parts) > 2 else 'V'
            status_desc = 'Valid' if status == 'A' else 'Invalid'
            lat = parts[3] if len(parts) > 3 else ''
            lon = parts[5] if len(parts) > 5 else ''
            print(f"  RMC: {status_desc} ({status})", end='')
            if lat and lon:
                print(f", Position: {lat},{lon}")
            else:
                print(" - No position")
            return True
    
    return False

def main():
    print("\n" + "="*60)
    print("Direct Serial GPS Test (NEO-M8N)")
    print("="*60)
    print("\nThis test reads directly from /dev/ttyAMA0")
    print("Bypasses GPSD to verify GPS module is working")
    print("\nPress Ctrl+C to stop")
    print("-"*60 + "\n")
    
    try:
        # Open serial port
        ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)
        print("✓ Connected to /dev/ttyAMA0 at 9600 baud\n")
        
        sentence_count = 0
        important_count = 0
        start_time = time.time()
        last_summary = time.time()
        
        while True:
            try:
                line = ser.readline().decode('ascii', errors='replace').strip()
                
                if line.startswith('$'):
                    sentence_count += 1
                    
                    # Show timestamp every 10 seconds
                    if time.time() - last_summary >= 10:
                        elapsed = int(time.time() - start_time)
                        print(f"\n[{elapsed}s elapsed - {sentence_count} sentences received]")
                        last_summary = time.time()
                    
                    # Parse and display important sentences
                    if analyze_nmea_sentence(line):
                        important_count += 1
                    
            except UnicodeDecodeError:
                continue
            except KeyboardInterrupt:
                raise
                
    except serial.SerialException as e:
        print(f"\n✗ Error opening serial port: {e}")
        print("\nPossible causes:")
        print("  • GPSD is still running (blocks the port)")
        print("  • Insufficient permissions")
        print("\nTry:")
        print("  sudo systemctl stop gpsd")
        print("  sudo killall gpsd")
        print("  sudo python3 check_gps_serial.py")
        return 1
    
    except KeyboardInterrupt:
        print("\n\n" + "-"*60)
        print(f"Test stopped by user")
        print(f"Total NMEA sentences received: {sentence_count}")
        print(f"Important sentences shown: {important_count}")
        
        if sentence_count == 0:
            print("\n⚠️  NO DATA RECEIVED!")
            print("  • Check wiring (TX/RX connections)")
            print("  • Verify power to GPS module")
            print("  • Check baud rate (should be 9600)")
        elif important_count == 0:
            print("\n⚠️  Data received but no GPS info")
            print("  • GPS may still be initializing")
            print("  • Wait longer for satellite acquisition")
        else:
            print("\n✓ GPS module is communicating!")
            print("\nIf no fix acquired:")
            print("  • Ensure clear view of sky")
            print("  • Wait 2-5 minutes for cold start")
            print("  • Need 4+ satellites for 3D fix")
    
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("\nSerial port closed")

if __name__ == "__main__":
    sys.exit(main() or 0)
