#!/bin/bash
# GPS NEO-M8N Diagnostic Script for Raspberry Pi 5

echo "======================================"
echo "NEO-M8N GPS Diagnostic Tool"
echo "======================================"
echo ""

# Check UART devices
echo "1. Checking UART devices..."
echo "----------------------------"
ls -l /dev/ttyAMA* /dev/serial* 2>/dev/null
if [ ! -e /dev/ttyAMA0 ]; then
    echo "⚠️  WARNING: /dev/ttyAMA0 not found!"
    echo "   UART may not be enabled. Check /boot/firmware/config.txt"
else
    echo "✓ /dev/ttyAMA0 exists"
fi
echo ""

# Check UART configuration in config.txt
echo "2. Checking UART configuration..."
echo "----------------------------"
if grep -q "enable_uart=1" /boot/firmware/config.txt 2>/dev/null; then
    echo "✓ enable_uart=1 found in config.txt"
else
    echo "⚠️  enable_uart=1 NOT found in config.txt"
fi

if grep -q "dtoverlay=disable-bt" /boot/firmware/config.txt 2>/dev/null; then
    echo "✓ Bluetooth disabled (frees up UART0)"
else
    echo "⚠️  Bluetooth NOT disabled - may conflict with UART0"
fi
echo ""

# Check for serial console
echo "3. Checking serial console..."
echo "----------------------------"
if systemctl is-active --quiet serial-getty@ttyAMA0.service; then
    echo "⚠️  Serial console is ACTIVE - this will block GPS!"
    echo "   Disable with: sudo systemctl disable serial-getty@ttyAMA0.service"
else
    echo "✓ Serial console is disabled"
fi
echo ""

# Test raw serial data
echo "4. Testing raw serial data (5 seconds)..."
echo "----------------------------"
echo "Reading from /dev/ttyAMA0..."
timeout 5 cat /dev/ttyAMA0 2>/dev/null | head -n 10
if [ $? -eq 0 ]; then
    echo "✓ Data received from GPS!"
else
    echo "⚠️  NO DATA from /dev/ttyAMA0"
    echo "   Check physical connections (especially TX/RX swap)"
fi
echo ""

# Check GPSD status
echo "5. Checking GPSD status..."
echo "----------------------------"
if systemctl is-active --quiet gpsd; then
    echo "✓ GPSD is running"
else
    echo "⚠️  GPSD is NOT running"
fi

systemctl status gpsd --no-pager -l | grep -A 5 "Active:"
echo ""

# Check GPSD configuration
echo "6. Checking GPSD configuration..."
echo "----------------------------"
if [ -f /etc/default/gpsd ]; then
    cat /etc/default/gpsd
else
    echo "⚠️  /etc/default/gpsd not found"
fi
echo ""

# Check GPSD processes
echo "7. Checking GPSD processes..."
echo "----------------------------"
ps aux | grep gpsd | grep -v grep
echo ""

# Check port permissions
echo "8. Checking port permissions..."
echo "----------------------------"
ls -l /dev/ttyAMA0
groups | grep -q dialout && echo "✓ User is in dialout group" || echo "⚠️  User NOT in dialout group"
echo ""

# Test with gpspipe
echo "9. Testing GPSD connection (5 seconds)..."
echo "----------------------------"
timeout 5 gpspipe -r 2>/dev/null | head -n 5
if [ $? -eq 0 ]; then
    echo "✓ GPSD is receiving data"
else
    echo "⚠️  GPSD not receiving data"
fi
echo ""

# Summary and recommendations
echo "======================================"
echo "DIAGNOSTIC SUMMARY"
echo "======================================"
echo ""
echo "Common Issues & Solutions:"
echo ""
echo "1. NO DATA from /dev/ttyAMA0:"
echo "   → Check TX/RX wiring (GPS TX → Pi RX pin 10)"
echo "   → Verify power connections"
echo "   → Ensure UART enabled in config.txt"
echo ""
echo "2. GPSD not receiving data:"
echo "   → Stop GPSD: sudo systemctl stop gpsd"
echo "   → Kill processes: sudo killall gpsd"
echo "   → Restart: sudo systemctl start gpsd"
echo ""
echo "3. Serial console blocking GPS:"
echo "   → sudo systemctl disable serial-getty@ttyAMA0.service"
echo "   → sudo reboot"
echo ""
echo "4. Multiple GPSD instances:"
echo "   → sudo killall gpsd"
echo "   → sudo systemctl restart gpsd"
echo ""
