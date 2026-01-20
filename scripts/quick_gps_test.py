#!/usr/bin/env python3
"""
Quick GPS position test using GPSD
Works with system python3-gps package
"""

import gps
import time

def get_gps_position(timeout=10):
    """Get current GPS position from GPSD"""
    try:
        session = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        
        print("Connecting to GPSD...")
        start = time.time()
        
        while time.time() - start < timeout:
            report = session.next()
            
            if report['class'] == 'TPV':
                lat = report.get('lat', None)
                lon = report.get('lon', None)
                
                if lat and lon and lat != 'n/a' and lon != 'n/a':
                    return {
                        'latitude': lat,
                        'longitude': lon,
                        'altitude': report.get('alt', None),
                        'speed': report.get('speed', None),
                        'time': report.get('time', None),
                        'mode': report.get('mode', 0)
                    }
        
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Quick GPS Test")
    print("="*60 + "\n")
    
    position = get_gps_position(timeout=15)
    
    if position:
        print("✓ GPS FIX ACQUIRED!\n")
        print(f"  Latitude:  {position['latitude']:.6f}°")
        print(f"  Longitude: {position['longitude']:.6f}°")
        
        if position['altitude']:
            print(f"  Altitude:  {position['altitude']:.1f} m")
        
        mode_text = {0: 'No fix', 1: 'No fix', 2: '2D fix', 3: '3D fix'}
        print(f"  Fix mode:  {mode_text.get(position['mode'], 'Unknown')}")
        
        if position['time']:
            print(f"  Time:      {position['time']}")
        
        print(f"\n  Google Maps: https://www.google.com/maps?q={position['latitude']},{position['longitude']}")
        print("\n✓ Your GPS is working perfectly! 🎉\n")
    else:
        print("✗ No GPS fix acquired\n")
        print("Troubleshooting:")
        print("  • Check GPSD is running: sudo systemctl status gpsd")
        print("  • Try: cgps -s")
        print("  • Ensure clear sky view\n")
