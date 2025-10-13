import json
import os

def update_pole_height():
    """Quick script to update pole height when sensor is moved"""
    
    if not os.path.exists("sensor_config.json"):
        print("❌ No sensor configuration found. Run the main script first.")
        return
    
    # Load existing configuration
    with open("sensor_config.json", 'r') as f:
        config = json.load(f)
    
    print("🔧 Update Sensor Pole Height")
    print("=" * 40)
    print(f"Current configuration:")
    print(f"   Floor: {config['floor_level']}")
    print(f"   Floor height: {config['floor_height']}m")
    print(f"   Current pole height: {config['pole_height']}m")
    print(f"   Current total height: {config['total_altitude_above_ground']:.1f}m")
    print()
    
    # Get new pole height
    new_pole_height = float(input("Enter new pole height in meters: "))
    
    # Update configuration
    config['pole_height'] = new_pole_height
    config['total_altitude_above_ground'] = (config['floor_level'] * config['floor_height']) + new_pole_height
    config['total_altitude_above_sea_level'] = config['building_ground_altitude'] + config['total_altitude_above_ground']
    config['last_updated'] = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Pole height updated"
    
    # Save updated configuration
    with open("sensor_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Updated pole height to {new_pole_height}m")
    print(f"📏 New total height above ground: {config['total_altitude_above_ground']:.1f}m")
    print("🔄 Configuration saved. Run the main script to see updated readings.")

if __name__ == "__main__":
    import time
    update_pole_height()
