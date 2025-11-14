# SQLite setup

## Key improvements with SQLite:

- ***Structured Data Storage:*** Separate tables for sensor readings, API data, and air quality
- ***Better Performance:*** Indexes for fast timestamp-based queries
- ***Data Integrity:*** Proper data types and constraints
- ***Backup Compatibility:*** Still saves to CSV as backup
- ***Query Capabilities:*** Easy to analyze historical data
- ***Expandable:*** Easy to add new sensors or data fields

## Prerequisites:
- Activate conda environment:
    ```bash
    conda activate python311
    ```

## Usage:
Run the weather station: python weather_station.py
Analyze data: python weather_analyzer.py --recent 24 --stats 24
Export data: python weather_analyzer.py --export 168 (export last week)
Database stats: python weather_analyzer.py --db-stats
The SQLite database will be created at ../weather_data.db and will store all your timestamped weather data for long-term analysis and historical tracking.

## Usefull commands:
-- Connect to your database
sqlite3 /home/rrocha/data/weather_data.db

-- Add the missing column
ALTER TABLE weather_readings ADD COLUMN sensor_wind_direction_name TEXT;

-- Verify the column was added
.schema weather_readings

-- Exit
.quit