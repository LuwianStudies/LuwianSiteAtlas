import pandas as pd
import requests
from rdflib import Graph
from rdflib.namespace import Namespace
from io import StringIO
from time import sleep

# Load site data
sites = pd.read_csv("coordinates.csv")  # Must include: name, latitude, longitude

endpoint = "https://query.wikidata.org/sparql"
search_radius = 5  # km ----- adjust according to your need ---------
results = []

def make_query(lat, lon, radius_km):
    return f"""
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT ?place ?placeLabel ?coord ?distance WHERE {{
      SERVICE wikibase:around {{
        ?place wdt:P625 ?coord .
        bd:serviceParam wikibase:center "Point({lon} {lat})"^^geo:wktLiteral .
        bd:serviceParam wikibase:radius "{radius_km}" .
        bd:serviceParam wikibase:distance ?distance .
      }}
      ?place wdt:P31/wdt:P279* wd:Q839954 .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    ORDER BY ?distance
    LIMIT 1
    """

for _, row in sites.iterrows():
    lat, lon, name = row['latitude'], row['longitude'], row['name']
    query = make_query(lat, lon, search_radius)

    response = requests.get(endpoint, params={"query": query}, headers={"Accept": "application/sparql-results+json"})

    if response.status_code == 200:
        bindings = response.json().get('results', {}).get('bindings', [])
        if bindings:
            item = bindings[0]
            results.append({
                "local_site": name,
                "latitude": lat,
                "longitude": lon,
                "wikidata_uri": item["place"]["value"],
                "label": item["placeLabel"]["value"],
                "distance_km": float(item["distance"]["value"])
            })
        else:
            results.append({
                "local_site": name,
                "latitude": lat,
                "longitude": lon,
                "wikidata_uri": None,
                "label": None,
                "distance_km": None
            })
    else:
        print(f"Query failed for {name}: {response.status_code}")
    
    sleep(1)

df = pd.DataFrame(results)
df.to_csv("nearest_wikidata_sites.csv", index=False)
print("Nearest places saved to nearest_wikidata_sites.csv!")
