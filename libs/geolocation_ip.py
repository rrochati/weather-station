import requests

def get_geo_ip():
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5)
        data = r.json()
        lat, lon = map(float, data["loc"].split(","))
        return {
            "latitude": lat,
            "longitude": lon,
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "ip": data.get("ip")
        }
    except Exception as e:
        print("Geolocation error:", e)
        return None

geo = get_geo_ip()
latitude = geo["latitude"] if geo else None
longitude = geo["longitude"] if geo else None
city = geo["city"] if geo else "Unknown"
region = geo["region"] if geo else "Unknown"
country = geo["country"] if geo else "Unknown"
ip = geo["ip"] if geo else "Unknown"

print(f"Station location: City: {city}, Coordinates: ({latitude}, {longitude}), Region: {region}, Country: {country}, IP: {ip}")