# NEO-M8N-0-10 GPS Module Setup Guide for Raspberry Pi 5

## Overview
The NEO-M8N is a GPS module that uses the u-blox M8 chip. It provides accurate positioning data via UART/serial communication.

## Hardware Connections

### Pin Connections (Raspberry Pi 5 to NEO-M8N)

| NEO-M8N Pin | Raspberry Pi 5 Pin | Description |
|-------------|-------------------|-------------|
| VCC         | Pin 1 (3.3V)      | Power supply |
| GND         | Pin 6 (GND)       | Ground |
| TXD         | Pin 10 (GPIO15/RXD0) | GPS transmit to Pi receive |
| RXD         | Pin 8 (GPIO14/TXD0) | GPS receive from Pi transmit |

**Important Notes:**
- The NEO-M8N typically works with 3.3V-5V, but check your specific module
- Use the hardware UART (UART0) on the Raspberry Pi 5
- TXD on GPS connects to RXD on Pi (cross-over connection)

## Software Setup

### 1. Enable UART on Raspberry Pi 5

Edit the config file:
```bash
sudo nano /boot/firmware/config.txt
```

Add or modify these lines:
```
# Disable Bluetooth to free up UART0
dtoverlay=disable-bt

# Enable UART
enable_uart=1
```

Disable the serial console:
```bash
sudo systemctl stop serial-getty@ttyAMA0.service
sudo systemctl disable serial-getty@ttyAMA0.service
```

Edit cmdline.txt to remove console settings:
```bash
sudo nano /boot/firmware/cmdline.txt
```

Remove any text containing `console=serial0,115200` or `console=ttyAMA0,115200`

Reboot:
```bash
sudo reboot
```

### 2. Install Required Software

```bash
# Install GPS daemon
sudo apt-get update
sudo apt-get install -y gpsd gpsd-clients python3-gps

# Install Python libraries
pip3 install pyserial pynmea2
```

### 3. Configure GPSD

Edit GPSD configuration:
```bash
sudo nano /etc/default/gpsd
```

Set:
```
START_GPSD="true"
GPSD_OPTIONS="-n"
DEVICES="/dev/ttyAMA0"
USBAUTO="true"
```

Restart GPSD:
```bash
sudo systemctl restart gpsd
sudo systemctl enable gpsd
```

## Testing the GPS Module

### Basic Test with GPSD
```bash
# Check if GPS is receiving data
cgps -s

# Or use gpsmon
gpsmon
```

### Test Serial Connection
```bash
# Read raw NMEA data
cat /dev/ttyAMA0
```

You should see NMEA sentences like:
```
$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
```

## Getting GPS Fix

**Important:** The GPS needs a clear view of the sky to get a fix. This can take:
- Cold start (no data): 26-30 seconds
- Warm start (some data): ~30 seconds
- Hot start (recent data): ~1 second

The module needs to see at least 4 satellites to get a 3D fix (latitude, longitude, altitude).

## Troubleshooting

### No Data from GPS
1. Check connections (especially TX/RX crossover)
2. Verify power (LED should blink when searching for satellites)
3. Ensure antenna has clear sky view
4. Check UART is enabled: `ls -l /dev/ttyAMA0`

### GPSD Not Working
```bash
# Stop GPSD
sudo systemctl stop gpsd

# Kill any gpsd processes
sudo killall gpsd

# Restart
sudo systemctl start gpsd
```

### Check UART Configuration
```bash
# List serial devices
ls -l /dev/serial*

# Check if UART is enabled
dmesg | grep uart
```

## LED Indicators
- **No blink**: No power or module fault
- **Blinking (1Hz)**: Searching for satellites
- **Solid/Fast blink**: GPS fix acquired

## Next Steps
Once the hardware is connected and tested, use the Python module provided to integrate GPS data into your weather station!
