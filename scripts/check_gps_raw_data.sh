#!/bin/bash
# Check raw GPS NMEA data to debug fix issues

echo "======================================"
echo "GPS Raw Data Analyzer"
echo "======================================"
echo ""

echo "Stopping GPSD temporarily to read raw data..."
sudo systemctl stop gpsd
sudo killall gpsd 2>/dev/null
sleep 2

echo ""
echo "Reading raw NMEA sentences from GPS (20 seconds)..."
echo "Look for satellite info and fix status..."
echo "--------------------------------------"
echo ""

timeout 20 cat /dev/ttyAMA0 | while IFS= read -r line; do
    # Highlight important NMEA sentences
    if [[ $line == \$GPGGA* ]] || [[ $line == \$GNGGA* ]]; then
        echo "GGA (Fix): $line"
    elif [[ $line == \$GPGSA* ]] || [[ $line == \$GNGSA* ]]; then
        echo "GSA (Satellites): $line"
    elif [[ $line == \$GPGSV* ]] || [[ $line == \$GNGSV* ]]; then
        echo "GSV (Satellites visible): $line"
    elif [[ $line == \$GPRMC* ]] || [[ $line == \$GNRMC* ]]; then
        echo "RMC (Position): $line"
    fi
done

echo ""
echo "--------------------------------------"
echo ""
echo "Restarting GPSD..."
sudo systemctl start gpsd
sleep 2

echo ""
echo "======================================"
echo "Analysis:"
echo "======================================"
echo ""
echo "NMEA Sentence Meanings:"
echo "• GGA - Fix data (quality indicator in field 6)"
echo "  - 0 = Invalid"
echo "  - 1 = GPS fix"
echo "  - 2 = DGPS fix"
echo ""
echo "• GSA - Satellite status and DOP values"
echo "  - Field 2: 1=no fix, 2=2D, 3=3D"
echo ""
echo "• GSV - Satellites in view"
echo "  - Shows signal strength (SNR) for each satellite"
echo ""
echo "• RMC - Recommended minimum"
echo "  - Field 2: A=valid, V=invalid"
echo ""
echo "Common Issues:"
echo "1. No satellites visible (GSV shows 0 or very low SNR)"
echo "   → Move GPS to location with clear sky view"
echo "   → Check antenna connection"
echo ""
echo "2. Satellites visible but no fix (GSA shows mode 1)"
echo "   → Wait longer (cold start: 2-5 minutes)"
echo "   → Need at least 4 satellites with good signal"
echo ""
echo "3. Only $GPRMC or $GPGGA appearing"
echo "   → GPS is working but needs time to acquire satellites"
echo ""
echo "4. No data at all"
echo "   → Check wiring and power"
echo ""
