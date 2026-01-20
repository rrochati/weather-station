#!/bin/bash
# Fix common GPSD issues with NEO-M8N GPS module

echo "======================================"
echo "GPS GPSD Fix Script"
echo "======================================"
echo ""

# Stop GPSD and kill all instances
echo "1. Stopping GPSD and killing all instances..."
sudo systemctl stop gpsd
sudo systemctl stop gpsd.socket
sleep 2
sudo killall gpsd 2>/dev/null
sleep 1
echo "✓ GPSD stopped"
echo ""

# Configure GPSD
echo "2. Configuring GPSD..."
sudo tee /etc/default/gpsd > /dev/null <<EOF
# GPSD Configuration for NEO-M8N
START_GPSD="true"
GPSD_OPTIONS="-n -b"
DEVICES="/dev/ttyAMA0"
USBAUTO="true"
GPSD_SOCKET="/var/run/gpsd.sock"
EOF
echo "✓ GPSD configured for /dev/ttyAMA0"
echo ""

# Disable serial console if active
echo "3. Checking serial console..."
if systemctl is-active --quiet serial-getty@ttyAMA0.service; then
    echo "Disabling serial console..."
    sudo systemctl stop serial-getty@ttyAMA0.service
    sudo systemctl disable serial-getty@ttyAMA0.service
    echo "✓ Serial console disabled"
else
    echo "✓ Serial console already disabled"
fi
echo ""

# Add user to dialout group
echo "4. Adding user to dialout group..."
sudo usermod -a -G dialout $USER
echo "✓ User added to dialout group"
echo ""

# Set permissions
echo "5. Setting permissions..."
sudo chmod 666 /dev/ttyAMA0 2>/dev/null
echo "✓ Permissions set"
echo ""

# Start GPSD
echo "6. Starting GPSD..."
sudo systemctl start gpsd.socket
sudo systemctl start gpsd
sleep 2
echo "✓ GPSD started"
echo ""

# Check status
echo "7. Checking GPSD status..."
systemctl status gpsd --no-pager | head -n 10
echo ""

echo "======================================"
echo "GPSD has been reset and configured!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Wait 30-60 seconds for GPS fix"
echo "2. Run: cgps -s"
echo "3. Or run: gpsmon"
echo "4. Test with: timeout 10 gpspipe -r"
echo ""
echo "If still no data:"
echo "• Check raw serial: cat /dev/ttyAMA0"
echo "• Run diagnostic: bash diagnose_gps.sh"
echo "• Verify wiring (GPS TX → Pi pin 10)"
echo ""
