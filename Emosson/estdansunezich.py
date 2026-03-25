import requests                
import matplotlib.pyplot as plt  
import matplotlib.patches as mpatches 
from shapely.geometry import shape 
import geopandas as gpd         
import pandas as pd              

#adresse to coordonnées lon lat
def adresse_vers_coordonnees(adresse):
    """
    Convertit une adresse en coordonnées lon, lat via l'API adresse.data.gouv.fr
    """
    r = requests.get(
        "https://api-adresse.data.gouv.fr/search/",
        params={"q": adresse, "limit": 1}  # requête AP on limite 1 résultat
    )
    
    data = r.json()  # JSON to dictionnaire
    feature = data["features"][0]
    
    lon = feature["geometry"]["coordinates"][0]  # longitude
    lat = feature["geometry"]["coordinates"][1]  # latitude
    adresse_trouvee = feature["properties"]["label"]  # label trouvé
    
    return {
        "lon": lon,
        "lat": lat,
        "adresse_trouvee": adresse_trouvee
    }

#Récupération de toutes les stations hydro
def recuperer_info_toutes_les_station():
    """
    Récupère toutes les stations hydrologiques depuis le WFS GeoPF et renvoie leurs infos
    """
    url = "https://data.geopf.fr/wfs/ows"
    
    requetes_stations = requests.get(url, params={
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "TYPENAMES": "VIGINOND-DIFFUSION:stationhydro",  # stations
        "OUTPUTFORMAT": "application/json",
        "COUNT": 5000
    })
    
    stations = []
    
    for f in requetes_stations.json()["features"]:
        station = {
            "code": f["properties"]["cdstation"],            # code station
            "nom_station": f["properties"]["lbusuel"],       # nom
            "cours_d_eau": f["properties"]["lbentitehydrographique"],  # cours d’eau
            "lon": f["geometry"]["coordinates"][0],          # longitude
            "lat": f["geometry"]["coordinates"][1]           # latitude
        }
        stations.append(station)
    
    # pd.DataFrame(stations).to_csv("stations.csv", index=False, encoding="utf-8-sig")  # option export CSV pour visualisé l'ensemble des staitons suir excel

    return stations

# Récupération polygones ZICH pour une station
def recuperer_geom_zich(code_station):
    """
    Récupère les polygones ZICH d'une station et leurs hauteurs de submersion max
    """

    
    url = "https://data.geopf.fr/wfs/ows"
    r = requests.get(url, params={
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "TYPENAMES": "VIGINOND-DIFFUSION:zich",  # ZICH
        "OUTPUTFORMAT": "application/json",
        "CQL_FILTER": f"cdstationhydro='{code_station}'",  # filtrage station
        "COUNT": 1000
    })
    
    features = r.json()["features"]
    
    # hauteur max parmi tous les scénarios
    hauteur_max = max(f["properties"]["hauteurstation"] for f in features)
    
    geom = []
    for f in features:
        if f["properties"]["hauteurstation"] == hauteur_max:
            hmin = f["properties"]["hauteurmin"] / 1000  # mm en m
            hmax = f["properties"]["hauteurmax"] / 1000
            if hmax >= 9999:  # on filtre les valeurs abérantes
                continue
            
            geom.append({
                "geometry": f["geometry"],  # polygone
                "hauteur_min_m": hmin,
                "hauteur_max_m": hmax
            })
    
    # infos scénarios
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
    
    return hauteur_max / 1000, geom

#Trouver la station la plus proche d’un point
def trouver_station_plus_proche(stations, lon, lat):
    """
    Trouve la station hydrologique la plus proche d'un point donné (lon, lat)
    """
    
    mini = ""                       # code station la plus proche
    distance_mini = float("inf")    # distance mini initiale
    nom_station_mini = ""            # nom station proche
    
    for i in range(len(stations)):
        lon_station_i = stations[i]['lon']
        lat_station_i = stations[i]['lat']
    
        distance = ((lon_station_i - lon) ** 2 + (lat_station_i - lat) ** 2) ** 0.5  # distance euclidienne
        
        if distance < distance_mini:
            distance_mini = distance
            mini = stations[i]["code"]
            nom_station_mini = stations[i]["nom_station"]
            
    return mini, nom_station_mini

#Affichage polygones ZICH avec submersion (ne sert que sur python pour visualiser le résultat en interne avant de la mettre sur le site)
def afficher_geom_zich(hauteur, geom, lon , lat, nom_station):
    """
    Affiche les polygones ZICH avec couleurs selon classes de submersion et point utilisateur
    """
    import matplotlib.cm as cm  # colormap
    
    classes_uniques = sorted(set((g["hauteur_min_m"], g["hauteur_max_m"]) for g in geom))  # classes submersion
    blues = cm.Blues([0.3 + 0.4 * i / max(len(classes_uniques) - 1, 1) for i in range(len(classes_uniques))])  # couleurs dégradées
    classe_couleur = {classe: blues[i] for i, classe in enumerate(classes_uniques)}
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for g in geom:
        classe  = (g["hauteur_min_m"], g["hauteur_max_m"])
        couleur = classe_couleur[classe]
        gdf_poly = gpd.GeoDataFrame(geometry=[shape(g["geometry"])], crs="EPSG:4326")  # GeoDataFrame
        gdf_poly.plot(ax=ax, color=couleur, edgecolor="white", linewidth=0.3, alpha=0.85)
        
    ax.plot(lon, lat, 'ro', markersize=4, zorder=5, label="Mon point")  # point utilisateur
    
    ax.set_title(f"ZICH {nom_station} — Scénario max : {hauteur}m", fontsize=13, fontweight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    
    # légende
    patches = [mpatches.Patch(color=classe_couleur[(hmin, hmax)], label=f"{hmin}m – {hmax}m") for hmin, hmax in classes_uniques]
    ax.legend(handles=patches, title="Hauteur de submersion", fontsize=9, loc="upper right")
    
    plt.tight_layout()
    plt.show()

#Vérifie si un point est dans une ZICH
def est_dans_une_zich(code_station, lon, lat, hauteur, geom):
    """
    Vérifie si un point (lon, lat) se trouve dans une ZICH et renvoie hauteur min/max
    """
    point = shape({"type": "Point", "coordinates": [lon, lat]})  # point utilisateur
    
    for g in geom:
        polygone = shape(g["geometry"])
        
        if polygone.contains(point):
            return True, g["hauteur_min_m"], g["hauteur_max_m"], geom
    
    return False, None, None, geom


## Ne sert a rien, le main sert justea essayer en local avec une adresse

if __name__ == "__main__":
    
    stations = recuperer_info_toutes_les_station()   # toutes stations
    
    result = adresse_vers_coordonnees("Paris")       # on récupère les coordonnées de l'adresse
    print("Information sur l'adrese :", result)
    
    lon = result['lon']
    lat = result["lat"]
    
    code_station, nom_station = trouver_station_plus_proche(stations, lon, lat)  # station proche
    print("Code station :", code_station)
    
    hauteur, geom = recuperer_geom_zich(code_station)  # polygones ZICH
    
    dans_zich, hmin, hmax, geom = est_dans_une_zich(code_station, lon, lat, hauteur, geom)  # point dans ZICH
    print(dans_zich, hmin, hmax)
    
    afficher_geom_zich(hauteur, geom, lon, lat, nom_station)  # plot