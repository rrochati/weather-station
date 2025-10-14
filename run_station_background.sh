#!/bin/bash

SCRIPT_DIR="/home/rrocha/weather-station"
SCRIPT_NAME="weather-station.py"
LOG_FILE="/home/rrocha/bme280_sensor.log"
PID_FILE="/home/rrocha/bme280_sensor.pid"

cd $SCRIPT_DIR

case "$1" in
    start)
        echo "Starting weather station in background..."
        # Activate conda environment and run script
        source ~/miniconda3/bin/activate python311
        nohup python -u $SCRIPT_NAME > $LOG_FILE 2>&1 &
        echo $! > $PID_FILE
        echo "Sensor started with PID $(cat $PID_FILE)"
        ;;
    stop)
        if [ -f $PID_FILE ]; then
            PID=$(cat $PID_FILE)
            echo "Stopping weather station (PID: $PID)..."
            kill $PID
            rm $PID_FILE
            echo "Weather station stopped."
        else
            echo "No PID file found. Weather station may not be running."
        fi
        ;;
    status)
        if [ -f $PID_FILE ]; then
            PID=$(cat $PID_FILE)
            if ps -p $PID > /dev/null; then
                echo "Weather station is running (PID: $PID)"
            else
                echo "PID file exists but process not running"
                rm $PID_FILE
            fi
        else
            echo "Weather station is not running"
        fi
        ;;
    logs)
        if [ -f $LOG_FILE ]; then
            tail -f $LOG_FILE
        else
            echo "No log file found"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status|logs}"
        exit 1
        ;;
esac
