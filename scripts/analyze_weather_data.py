#!/usr/bin/env python3
"""
Weather Data Analyzer - Query and analyze weather station data from SQLite database
"""

import argparse
import sqlite3
from datetime import datetime, timedelta
import statistics
from modules.database import WeatherDatabase

def print_recent_readings(db: WeatherDatabase, hours: int = 24):
    """Print recent weather readings."""
    readings = db.get_recent_readings(hours)
    
    if not readings:
        print(f"No readings found in the last {hours} hours")
        return
    
    print(f"\n=== Recent Weather Readings (Last {hours} hours) ===")
    print(f"{'Timestamp':<20} {'Temp(°C)':<8} {'Humidity(%)':<12} {'Pressure(hPa)':<14} {'Altitude(m)':<12}")
    print("-" * 80)
    
    for reading in readings[:20]:  # Show last 20 readings
        print(f"{reading['timestamp']:<20} {reading['temperature_c']:<8.1f} "
              f"{reading['humidity_percent']:<12.1f} {reading['pressure_hpa']:<14.1f} "
              f"{reading['altitude_m']:<12.1f}")

def print_statistics(db: WeatherDatabase, hours: int = 24):
    """Print weather statistics."""
    readings = db.get_recent_readings(hours)
    
    if not readings:
        print(f"No readings found in the last {hours} hours")
        return
    
    temps = [r['temperature_c'] for r in readings if r['temperature_c'] is not None]
    humidity = [r['humidity_percent'] for r in readings if r['humidity_percent'] is not None]
    pressure = [r['pressure_hpa'] for r in readings if r['pressure_hpa'] is not None]
    
    print(f"\n=== Weather Statistics (Last {hours} hours) ===")
    print(f"Total readings: {len(readings)}")
    
    if temps:
        print(f"\nTemperature (°C):")
        print(f"  Min: {min(temps):.1f}, Max: {max(temps):.1f}, Avg: {statistics.mean(temps):.1f}")
        
    if humidity:
        print(f"\nHumidity (%):")
        print(f"  Min: {min(humidity):.1f}, Max: {max(humidity):.1f}, Avg: {statistics.mean(humidity):.1f}")
        
    if pressure:
        print(f"\nPressure (hPa):")
        print(f"  Min: {min(pressure):.1f}, Max: {max(pressure):.1f}, Avg: {statistics.mean(pressure):.1f}")

def export_to_csv(db: WeatherDatabase, hours: int = 24, filename: str = None):
    """Export recent readings to CSV."""
    import csv
    
    readings = db.get_recent_readings(hours)
    
    if not readings:
        print(f"No readings found in the last {hours} hours")
        return
    
    if filename is None:
        filename = f"weather_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'temperature_c', 'humidity_percent', 'pressure_hpa', 'altitude_m']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for reading in readings:
            writer.writerow({k: reading[k] for k in fieldnames})
    
    print(f"Exported {len(readings)} readings to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Weather Station Data Analyzer')
    parser.add_argument('--recent', type=int, default=24, 
                       help='Show recent readings from last N hours (default: 24)')
    parser.add_argument('--stats', type=int, 
                       help='Show statistics for last N hours')
    parser.add_argument('--export', type=int, 
                       help='Export data from last N hours to CSV')
    parser.add_argument('--db-stats', action='store_true',
                       help='Show database statistics')
    
    args = parser.parse_args()
    
    # Initialize database
    db = WeatherDatabase()
    
    if args.db_stats:
        stats = db.get_database_stats()
        print("\n=== Database Statistics ===")
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    if args.recent:
        print_recent_readings(db, args.recent)
    
    if args.stats:
        print_statistics(db, args.stats)
    
    if args.export:
        export_to_csv(db, args.export)

if __name__ == "__main__":
    main()