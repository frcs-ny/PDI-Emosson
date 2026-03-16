import requests
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.geometry import shape
import geopandas as gpd
import pandas as pd

def adresse_vers_coordonnees(adresse):
    """
    Convertit une adresse en coordonnées GPS (lon, lat)
    via l'API adresse.data.gouv.fr (gratuite, pas de clé API)
    
    Paramètre :
        adresse : ex "9 Rue du Commandant Bourgoin, 37000 Tours"
    
    Retourne :
        dict {lon, lat, adresse_trouvee}
    """
    r = requests.get(
        "https://api-adresse.data.gouv.fr/search/",
        params={"q": adresse, "limit": 1}
    )
    
    data = r.json()
    
    feature = data["features"][0]
    lon = feature["geometry"]["coordinates"][0]
    lat = feature["geometry"]["coordinates"][1]
    adresse_trouvee = feature["properties"]["label"]
    
    return {
        "lon":            lon,
        "lat":            lat,
        "adresse_trouvee": adresse_trouvee
    }



def recuperer_info_toutes_les_station():
    
    url = "https://data.geopf.fr/wfs/ows"
    
    requetes_stations = requests.get(url, params={
        "SERVICE":      "WFS",
        "VERSION":      "2.0.0",
        "REQUEST":      "GetFeature",
        "TYPENAMES":    "VIGINOND-DIFFUSION:stationhydro",
        "OUTPUTFORMAT": "application/json",
        "COUNT":        5000
    })
    
    stations = []
    
    for f in requetes_stations.json()["features"]:
        station = {
            "code":        f["properties"]["cdstation"],
            "nom_station": f["properties"]["lbusuel"],
            "cours_d_eau": f["properties"]["lbentitehydrographique"],
            "lon":         f["geometry"]["coordinates"][0],
            "lat":         f["geometry"]["coordinates"][1]
        }
        stations.append(station)
    
    # pd.DataFrame(stations).to_csv("stations.csv", index=False, encoding="utf-8-sig")

    return stations

def recuperer_geom_zich(code_station):
    
    url = "https://data.geopf.fr/wfs/ows"
    r = requests.get(url, params={
        "SERVICE":      "WFS",
        "VERSION":      "2.0.0",
        "REQUEST":      "GetFeature",
        "TYPENAMES":    "VIGINOND-DIFFUSION:zich",
        "OUTPUTFORMAT": "application/json",
        "CQL_FILTER":   f"cdstationhydro='{code_station}'",
        "COUNT":        1000
    })
    
    features = r.json()["features"]
    
    hauteur_max = max(
        f["properties"]["hauteurstation"] 
        for f in features
    )
    
    geom = []
    for f in features:
        if f["properties"]["hauteurstation"] == hauteur_max:
            hmin = f["properties"]["hauteurmin"] / 1000
            hmax = f["properties"]["hauteurmax"] / 1000
            
            if hmax >= 9999:
                continue
            
            geom.append({
                "geometry":      f["geometry"],
                "hauteur_min_m": hmin,
                "hauteur_max_m": hmax
            })
    
    print("")
    print(f"Nombre de scénarios disponibles : {len(set(f['properties']['hauteurstation'] for f in features))}")
    print("")
    print(f"Liste scénarios en m : {sorted(set(f['properties']['hauteurstation'] / 1000 for f in features))}")
    
    print("")
    print(f"Scénario choisit : {hauteur_max / 1000}m")
    print("")
    print(f"Nb polygones : {len(geom)}")
    for g in geom:
        print(f"  submersion : {g['hauteur_min_m']}m – {g['hauteur_max_m']}m")
    
    # data = r.json()
    # print(data["crs"])


    return hauteur_max / 1000, geom



def trouver_station_plus_proche(stations,lon,lat):
    mini = ""
    distance_mini = float("inf") 
    nom_station_mini = ""
    for i in range(len(stations)):
        lon_station_i = stations[i]['lon']
        lat_station_i = stations[i]['lat']
    
        distance = ((lon_station_i - lon) ** 2 + (lat_station_i - lat) ** 2) ** 0.5
        
        if distance < distance_mini:
            distance_mini = distance
            mini = stations[i]["code"]
            nom_station_mini = stations[i]["nom_station"]
            # print(nom_station_mini)
            # print(mini)
            
    return mini, nom_station_mini




def afficher_geom_zich(hauteur, geom, lon , lat, nom_station):
    """
    Affiche les polygones de la ZICH pour le scénario max,
    une couleur différente par classe de submersion.
    
    Paramètres :
        hauteur : hauteur du scénario en mètres (ex: 6.5)
        geom    : liste de dictionnaires {geometry, hauteur_min_m, hauteur_max_m}
    """
    import matplotlib.cm as cm
    
    # Récupérer les classes uniques triées par hauteur_min
    classes_uniques = sorted(set(
        (g["hauteur_min_m"], g["hauteur_max_m"]) for g in geom
    ))
    
    # Attribuer une couleur différente à chaque classe
    blues = cm.Blues([0.3 + 0.4 * i / max(len(classes_uniques) - 1, 1) for i in range(len(classes_uniques))])
    classe_couleur = {
        classe: blues[i]
        for i, classe in enumerate(classes_uniques)
    }
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Dessiner chaque polygone
    for g in geom:
        classe  = (g["hauteur_min_m"], g["hauteur_max_m"])
        couleur = classe_couleur[classe]
        gdf_poly = gpd.GeoDataFrame(
            geometry=[shape(g["geometry"])], crs="EPSG:4326"
        )
        gdf_poly.plot(ax=ax, color=couleur, edgecolor="white", linewidth=0.3, alpha=0.85)
        
    ax.plot(lon, lat, 'ro', markersize=4, zorder=5, label="Mon point")
    
    
    ax.set_title(f"ZICH {nom_station} — Scénario max : {hauteur}m", fontsize=13, fontweight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    
    # Légende
    patches = [
        mpatches.Patch(
            color=classe_couleur[(hmin, hmax)],
            label=f"{hmin}m – {hmax}m"
        )
        for hmin, hmax in classes_uniques
    ]
    ax.legend(handles=patches, title="Hauteur de submersion", fontsize=9, loc="upper right")
    
    plt.tight_layout()
    plt.show()


def est_dans_une_zich(code_station, lon, lat, hauteur, geom):
    
   
    
    point = shape({"type": "Point", "coordinates": [lon, lat]})
    
    for g in geom:
        polygone = shape(g["geometry"])
        
        if polygone.contains(point):
            return True, g["hauteur_min_m"], g["hauteur_max_m"], geom
    
    return False, None, None, None




if __name__ == "__main__":
    
    stations = recuperer_info_toutes_les_station()
    
    result = adresse_vers_coordonnees("Paris")
    print("Information sur l'adrese :" , result)
    
    
    lon = result['lon']
    lat = result["lat"]
    # lon = 1.421
    # lat = 43.535
    
    code_station, nom_station = trouver_station_plus_proche(stations,lon,lat)
    print("Code station :",code_station)
    
    hauteur, geom = recuperer_geom_zich(code_station)
    
    
    
    dans_zich, hmin, hmax, geom = est_dans_une_zich(code_station, lon, lat, hauteur, geom )
    
    print(dans_zich, hmin, hmax, geom)

    
    afficher_geom_zich(hauteur, geom, lon, lat, nom_station)
    
    
    

    
    
    