import pandas as pd
import json
import requests
from geopy.distance import geodesic

# Load your local coordinates
sites = pd.read_csv("sites.csv")  # columns: name, latitude, longitude

# Load Pleiades GeoJSON data
with open("pleiades-places-latest.json", "r", encoding="utf-8") as f:
    pleiades_data = json.load(f)

# Extract minimal info
pleiades_places = []
for place in pleiades_data["features"]:
    props = place.get("properties", {})
    geom = place.get("geometry", {})
    coords = geom.get("coordinates", [])
    if geom.get("type") == "Point" and len(coords) == 2:
        pleiades_places.append({
            "pid": props.get("uid", ""),
            "title": props.get("title", ""),
            "latitude": coords[1],
            "longitude": coords[0]
        })

# Match nearest place
results = []
for _, row in sites.iterrows():
    name, lat, lon = row["name"], row["latitude"], row["longitude"]
    site_coord = (lat, lon)
    min_dist, closest = float("inf"), None

    for place in pleiades_places:
        p_coord = (place["latitude"], place["longitude"])
        dist = geodesic(site_coord, p_coord).kilometers
        if dist < min_dist:
            min_dist = dist
            closest = place

    # Optionally query the API for additional details
    api_url = f"https://pleiades.stoa.org/places/{closest['pid']}/json"
    try:
        response = requests.get(api_url)
        extra = response.json()
        description = extra.get("description", "")
    except:
        description = ""

    results.append({
        "local_site": name,
        "latitude": lat,
        "longitude": lon,
        "pleiades_title": closest["title"],
        "pleiades_uri": f"https://pleiades.stoa.org/places/{closest['pid']}",
        "distance_km": round(min_dist, 2),
        "description": description
    })

# Save output
df = pd.DataFrame(results)
df.to_csv("nearest_pleiades.csv", index=False)
print("Nearest Pleiades matches saved!")
