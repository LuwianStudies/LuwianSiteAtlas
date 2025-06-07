import pandas as pd
import requests
from time import sleep

sites = pd.read_csv("site_coordinates.csv")  # Requires: name, latitude, longitude

GEONAMES_USERNAME = "your_username"  # ← Replace with your GeoNames username. You can register via: https://www.geonames.org/login
API_URL = "http://api.geonames.org/findNearbyPlaceNameJSON"

enriched = []

for _, row in sites.iterrows():
    name, lat, lon = row["name"], row["latitude"], row["longitude"]
    
    try:
        res = requests.get(API_URL, params={
            "lat": lat,
            "lng": lon,
            "username": GEONAMES_USERNAME
        })
        data = res.json()
        item = data["geonames"][0] if "geonames" in data and data["geonames"] else {}

        enriched.append({
            "site": name,
            "latitude": lat,
            "longitude": lon,
            "town": item.get("name"),
            "district": item.get("adminName2"),
            "province": item.get("adminName1"),
            "country": item.get("countryName")
        })
    except Exception as e:
        enriched.append({
            "site": name,
            "latitude": lat,
            "longitude": lon,
            "town": None,
            "district": None,
            "province": None,
            "country": None
        })
        print(f"Error for {name}: {e}")
    
    sleep(1)  # Respect API rate limits

df = pd.DataFrame(enriched)
df.to_csv("sites_with_geonames_admin.csv", index=False)
print("GeoNames admin data saved!")
