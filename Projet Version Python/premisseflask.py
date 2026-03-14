from flask import Flask, render_template, request, jsonify
from estdansunezich import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adresse')
def chercher_adresse():
    adresse = request.args.get('adresse')  
    
    stations = recuperer_info_toutes_les_station()
    
    result = adresse_vers_coordonnees(adresse)
    print("Information sur l'adrese :" , result)
    
    
    lon = result['lon']
    lat = result["lat"]
    # lon = 1.421
    # lat = 43.535
    
    code_station, nom_station = trouver_station_plus_proche(stations,lon,lat)
    print("Code station :",code_station)
    
    hauteur, geom = recuperer_geom_zich(code_station)
    
    
    
    dans_zich, hmin, hmax = est_dans_une_zich(code_station, lon, lat, hauteur, geom )
    
    print(dans_zich, hmin, hmax)
    
    if dans_zich:
        message = f"Votre adresse se trouve dans une zone d'inondation. Lors d'un potentiel cru, l'endroit où vous vous trouvez sera inondé entre {hmin}m et {hmax}m."
    else:
        message = "Votre adresse ne se trouve pas dans une zone d'inondation."

    return jsonify({"message": message})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)