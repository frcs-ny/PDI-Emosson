import requests

def recuperer_coordonnees(adresse: str) -> dict | None:
    """Récupère les coordonnées GPS à partir d'une adresse via l'API BAN."""
    url = "https://api-adresse.data.gouv.fr/search/"
    params = {'q': adresse, 'limit': 1}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('features'):
            return None
            
        # Les coordonnées sont au format [longitude, latitude]
        coords = data['features'][0]['geometry']['coordinates']
        return {
            'lat': coords[1],
            'lon': coords[0]
        }
    except requests.RequestException as e:
        print(f"Erreur API BAN: {e}")
        return None

def est_dans_une_zone_inondable(lat: float, lon: float, page: int = 1, page_size: int = 10) -> dict:
    """
    Vérifie si des coordonnées GPS se trouvent dans un TRI 
    (Territoire à Risque Important d'inondation) via Géorisques.
    """
    url_tri = 'https://georisques.gouv.fr/api/v1/gaspar/tri'
    
    params = {
        "rayon": 100,
        "latlon": f"{lon},{lat}",
        "page": page,
        "page_size": page_size,
    }
    
    result = {'found': False, 'risques': []}
    
    try:
        response = requests.get(url_tri, params=params)
        response.raise_for_status()
        data = response.json()
        
        for elt_data in data.get('data', []):
            for risque in elt_data.get('liste_libelle_risque', []):
                num = str(risque.get('num_risque', ''))
                
                if num.startswith('11') or num.startswith('23'):
                    result['found'] = True
                    result['risques'].append(risque.get('libelle_risque_long', ''))
        
        # Supprimer les doublons de la liste des risques
        result['risques'] = list(set(result['risques']))
        
    except requests.RequestException as e:
        print(f"Erreur API Géorisques: {e}")
        
    return result