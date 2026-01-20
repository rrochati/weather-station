#!/bin/bash
# Enable UART on Raspberry Pi 5 for NEO-M8N GPS

echo "======================================"
echo "Raspberry Pi 5 UART Setup for GPS"
echo "======================================"
echo ""

# Check current serial devices
echo "1. Checking current serial devices..."
echo "----------------------------"
ls -l /dev/tty* 2>/dev/null | grep -E "(ttyAMA|ttyS|serial)"
echo ""

# Backup config.txt
echo "2. Backing up config.txt..."
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%Y%m%d_%H%M%S)
echo "✓ Backup created"
echo ""

# Configure UART
echo "3. Configuring UART in config.txt..."
echo "----------------------------"

# Remove any existing UART settings
sudo sed -i '/^enable_uart/d' /boot/firmware/config.txt
sudo sed -i '/^dtoverlay=disable-bt/d' /boot/firmware/config.txt
sudo sed -i '/^dtoverlay=uart0/d' /boot/firmware/config.txt

# Add UART configuration at the end of [all] section
if grep -q "^\[all\]" /boot/firmware/config.txt; then
    # [all] section exists, add after it
    sudo sed -i '/^\[all\]/a # GPS UART Configuration\nenable_uart=1\ndtoverlay=disable-bt' /boot/firmware/config.txt
else
    # No [all] section, add at the end
    echo "" | sudo tee -a /boot/firmware/config.txt
    echo "# GPS UART Configuration" | sudo tee -a /boot/firmware/config.txt
    echo "enable_uart=1" | sudo tee -a /boot/firmware/config.txt
    echo "dtoverlay=disable-bt" | sudo tee -a /boot/firmware/config.txt
fi

echo "✓ Added to config.txt:"
echo "  enable_uart=1"
echo "  dtoverlay=disable-bt"
echo ""

# Disable serial console
echo "4. Disabling serial console..."
echo "----------------------------"

# Check cmdline.txt
if [ -f /boot/firmware/cmdline.txt ]; then
    sudo cp /boot/firmware/cmdline.txt /boot/firmware/cmdline.txt.backup.$(date +%Y%m%d_%H%M%S)
    
    # Remove console=serial0 and console=ttyAMA0
    sudo sed -i 's/console=serial0,[0-9]\+\s*//g' /boot/firmware/cmdline.txt
    sudo sed -i 's/console=ttyAMA0,[0-9]\+\s*//g' /boot/firmware/cmdline.txt
    
    echo "✓ Removed serial console from cmdline.txt"
else
    echo "⚠️  cmdline.txt not found (this is OK for some setups)"
fi

# Disable serial-getty service
if systemctl is-enabled serial-getty@ttyAMA0.service 2>/dev/null; then
    sudo systemctl disable serial-getty@ttyAMA0.service
    echo "✓ Disabled serial-getty@ttyAMA0.service"
else
    echo "✓ serial-getty service not active"
fi
echo ""

# Show what was added to config.txt
echo "5. Current UART configuration in config.txt:"
echo "----------------------------"
grep -A 2 "GPS UART Configuration" /boot/firmware/config.txt || grep -E "(enable_uart|disable-bt)" /boot/firmware/config.txt
echo ""

echo "======================================"
echo "UART Configuration Complete!"
echo "======================================"
echo ""
echo "⚠️  IMPORTANT: You MUST reboot for changes to take effect!"
echo ""
echo "After reboot:"
echo "1. Check device exists: ls -l /dev/ttyAMA0"
echo "2. Check for data: cat /dev/ttyAMA0 (Ctrl+C to stop)"
echo "3. Configure GPSD: sudo bash fix_gps_gpsd.sh"
echo ""
read -p "Reboot now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Rebooting in 5 seconds..."
    sleep 5
    sudo reboot
else
    echo "Remember to reboot before testing GPS!"
fi
