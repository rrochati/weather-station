"""
NEO-M8N GPS Module Interface
Provides methods to read GPS data from the NEO-M8N module
Supports both GPSD and direct serial NMEA parsing
"""

import serial
import time
import logging
from typing import Optional, Dict, Tuple

try:
    import pynmea2
    PYNMEA2_AVAILABLE = True
except ImportError:
    PYNMEA2_AVAILABLE = False
    logging.warning("pynmea2 not installed. Install with: pip3 install pynmea2")

try:
    import gps
    GPS3_AVAILABLE = False
    GPSD_AVAILABLE = True
except ImportError:
    try:
        from gps3 import gps3
        GPS3_AVAILABLE = True
        GPSD_AVAILABLE = False
    except ImportError:
        GPS3_AVAILABLE = False
        GPSD_AVAILABLE = False
        logging.warning("GPS library not available. Install with: sudo apt-get install python3-gps")


class NEOM8N:
    """Interface for NEO-M8N GPS module"""
    
    def __init__(self, serial_port='/dev/ttyAMA0', baudrate=9600, use_gpsd=True):
        """
        Initialize GPS module
        
        Args:
            serial_port: Serial port device path (default: /dev/ttyAMA0)
            baudrate: Serial communication speed (default: 9600)
            use_gpsd: Use GPSD daemon if True, otherwise direct serial
        """
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.use_gpsd = use_gpsd
        self.serial_conn = None
        self.gpsd_session = None
        
        logging.info(f"Initializing NEO-M8N GPS on {serial_port}")
        
    def connect(self) -> bool:
        """
        Connect to GPS module
        
        Returns:
            bool: True if connection successful
        """
        try:
            if self.use_gpsd:
                return self._connect_gpsd()
            else:
                return self._connect_serial()
        except Exception as e:
            logging.error(f"Failed to connect to GPS: {e}")
            return False
    
    def _connect_gpsd(self) -> bool:
        """Connect using GPSD daemon"""
        try:
            if GPSD_AVAILABLE:
                self.gpsd_session = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
                logging.info("Connected to GPSD")
                return True
            elif GPS3_AVAILABLE:
                self.gpsd_socket = gps3.GPSDSocket()
                self.gpsd_stream = gps3.DataStream()
                self.gpsd_socket.connect()
                self.gpsd_socket.watch()
                logging.info("Connected to GPSD (gps3)")
                return True
            else:
                logging.error("GPSD library not available. Install: sudo apt-get install python3-gps")
                return False
        except Exception as e:
            logging.error(f"GPSD connection failed: {e}")
            return False
    
    def _connect_serial(self) -> bool:
        """Connect using direct serial connection"""
        try:
            if not PYNMEA2_AVAILABLE:
                logging.error("pynmea2 required for serial mode")
                return False
                
            self.serial_conn = serial.Serial(
                self.serial_port,
                baudrate=self.baudrate,
                timeout=1
            )
            logging.info(f"Connected to GPS via serial: {self.serial_port}")
            return True
        except Exception as e:
            logging.error(f"Serial connection failed: {e}")
            return False
    
    def get_position(self, timeout=10) -> Optional[Dict]:
        """
        Get current GPS position
        
        Args:
            timeout: Maximum time to wait for valid GPS fix (seconds)
        
        Returns:
            Dict with GPS data or None if no fix:
            {
                'latitude': float,
                'longitude': float,
                'altitude': float,
                'speed': float,
                'track': float,
                'time': str,
                'satellites': int,
                'fix_quality': int,
                'hdop': float
            }
        """
        if self.use_gpsd:
            return self._get_position_gpsd(timeout)
        else:
            return self._get_position_serial(timeout)
    
    def _get_position_gpsd(self, timeout) -> Optional[Dict]:
        """Get position using GPSD"""
        if not self.gpsd_session:
            logging.error("GPSD not connected")
            return None
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                if GPSD_AVAILABLE:
                    report = self.gpsd_session.next()
                    
                    if report['class'] == 'TPV':
                        # Check for valid lat/lon in the dictionary
                        lat = report.get('lat', None)
                        lon = report.get('lon', None)
                        
                        if lat is not None and lon is not None and lat != 'n/a' and lon != 'n/a':
                            return {
                                'latitude': float(lat),
                                'longitude': float(lon),
                                'altitude': report.get('alt', None),
                                'speed': report.get('speed', None),
                                'track': report.get('track', None),
                                'time': report.get('time', None),
                                'satellites': None,
                                'fix_quality': report.get('mode', 0),
                                'hdop': None
                            }
                elif GPS3_AVAILABLE:
                    for new_data in self.gpsd_socket:
                        if new_data:
                            self.gpsd_stream.unpack(new_data)
                            
                            if self.gpsd_stream.TPV['lat'] != 'n/a':
                                return {
                                    'latitude': float(self.gpsd_stream.TPV['lat']),
                                    'longitude': float(self.gpsd_stream.TPV['lon']),
                                    'altitude': float(self.gpsd_stream.TPV['alt']) if self.gpsd_stream.TPV['alt'] != 'n/a' else None,
                                    'speed': float(self.gpsd_stream.TPV['speed']) if self.gpsd_stream.TPV['speed'] != 'n/a' else None,
                                    'track': float(self.gpsd_stream.TPV['track']) if self.gpsd_stream.TPV['track'] != 'n/a' else None,
                                    'time': self.gpsd_stream.TPV['time'],
                                    'satellites': None,
                                    'fix_quality': int(self.gpsd_stream.TPV['mode']) if self.gpsd_stream.TPV['mode'] != 'n/a' else 0,
                                    'hdop': None
                                }
                
                time.sleep(0.1)
                
            logging.warning("GPS timeout: No fix acquired")
            return None
            
        except Exception as e:
            logging.error(f"Error reading GPSD data: {e}")
            return None
    
    def _get_position_serial(self, timeout) -> Optional[Dict]:
        """Get position using direct serial NMEA parsing"""
        if not self.serial_conn:
            logging.error("Serial not connected")
            return None
        
        start_time = time.time()
        gps_data = {}
        
        try:
            while time.time() - start_time < timeout:
                line = self.serial_conn.readline().decode('ascii', errors='replace')
                
                if line.startswith('$'):
                    try:
                        msg = pynmea2.parse(line)
                        
                        # GGA - Fix data
                        if isinstance(msg, pynmea2.GGA):
                            if msg.latitude and msg.longitude:
                                gps_data['latitude'] = msg.latitude
                                gps_data['longitude'] = msg.longitude
                                gps_data['altitude'] = msg.altitude
                                gps_data['satellites'] = msg.num_sats
                                gps_data['fix_quality'] = msg.gps_qual
                                gps_data['hdop'] = msg.horizontal_dil
                                gps_data['time'] = str(msg.timestamp) if msg.timestamp else None
                        
                        # RMC - Recommended minimum
                        elif isinstance(msg, pynmea2.RMC):
                            if msg.latitude and msg.longitude:
                                gps_data['latitude'] = msg.latitude
                                gps_data['longitude'] = msg.longitude
                                gps_data['speed'] = msg.spd_over_grnd
                                gps_data['track'] = msg.true_course
                                gps_data['time'] = str(msg.timestamp) if msg.timestamp else None
                        
                        # If we have valid position data, return it
                        if 'latitude' in gps_data and 'longitude' in gps_data:
                            # Fill in any missing fields
                            return {
                                'latitude': gps_data.get('latitude'),
                                'longitude': gps_data.get('longitude'),
                                'altitude': gps_data.get('altitude'),
                                'speed': gps_data.get('speed'),
                                'track': gps_data.get('track'),
                                'time': gps_data.get('time'),
                                'satellites': gps_data.get('satellites'),
                                'fix_quality': gps_data.get('fix_quality', 0),
                                'hdop': gps_data.get('hdop')
                            }
                            
                    except pynmea2.ParseError:
                        continue
            
            logging.warning("GPS timeout: No valid NMEA data received")
            return None
            
        except Exception as e:
            logging.error(f"Error reading serial GPS data: {e}")
            return None
    
    def get_lat_lon(self, timeout=10) -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude only
        
        Args:
            timeout: Maximum time to wait for GPS fix
        
        Returns:
            Tuple of (latitude, longitude) or None
        """
        position = self.get_position(timeout)
        if position:
            return (position['latitude'], position['longitude'])
        return None
    
    def has_fix(self) -> bool:
        """
        Check if GPS has a valid fix
        
        Returns:
            bool: True if GPS has fix
        """
        position = self.get_position(timeout=2)
        return position is not None
    
    def close(self):
        """Close GPS connection"""
        try:
            if self.serial_conn:
                self.serial_conn.close()
                logging.info("GPS serial connection closed")
            if self.gpsd_session:
                self.gpsd_session = None
                logging.info("GPSD session closed")
        except Exception as e:
            logging.error(f"Error closing GPS connection: {e}")


def main():
    """Test the GPS module"""
    logging.basicConfig(level=logging.INFO)
    
    print("NEO-M8N GPS Module Test")
    print("=" * 50)
    
    # Try GPSD first, then fall back to serial
    gps_module = NEOM8N(use_gpsd=True)
    
    if not gps_module.connect():
        print("\nGPSD failed, trying direct serial...")
        gps_module = NEOM8N(use_gpsd=False)
        if not gps_module.connect():
            print("Failed to connect to GPS module!")
            return
    
    print("\nWaiting for GPS fix (this may take 30-60 seconds)...")
    print("Make sure the GPS antenna has a clear view of the sky!")
    
    position = gps_module.get_position(timeout=60)
    
    if position:
        print("\n✓ GPS Fix Acquired!")
        print("-" * 50)
        print(f"Latitude:     {position['latitude']:.6f}°")
        print(f"Longitude:    {position['longitude']:.6f}°")
        print(f"Altitude:     {position['altitude']:.1f} m" if position['altitude'] else "Altitude:     N/A")
        print(f"Satellites:   {position['satellites']}" if position['satellites'] else "Satellites:   N/A")
        print(f"Fix Quality:  {position['fix_quality']}")
        print(f"Time:         {position['time']}" if position['time'] else "Time:         N/A")
        print(f"Speed:        {position['speed']:.1f} m/s" if position['speed'] else "Speed:        N/A")
        print(f"HDOP:         {position['hdop']}" if position['hdop'] else "HDOP:         N/A")
    else:
        print("\n✗ No GPS fix acquired")
        print("Troubleshooting:")
        print("1. Check antenna has clear sky view")
        print("2. Verify wiring connections")
        print("3. Wait longer (cold start can take 2-5 minutes)")
        print("4. Check GPSD status: sudo systemctl status gpsd")
    
    gps_module.close()


if __name__ == "__main__":
    main()
