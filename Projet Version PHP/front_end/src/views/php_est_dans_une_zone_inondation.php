<?php

// Récupération coordonnée a partir de l'adresse

function récupérer_coordonnees(string $adresse): ?array {

    // Encodage de l'adresse pour l'intégrer dans une URL
    $params = http_build_query(['q' => $adresse, 'limit' => 1]);
    $url = "https://api-adresse.data.gouv.fr/search/?$params";

    $response = file_get_contents($url);
    if ($response === false) {
        die("Erreur lors de l'appel à l'API BAN");
    }

    $data = json_decode($response, true);

    // Vérifie qu'on a bien au moins un résultat
    if (empty($data['features'])) {
        return null;
    }

    // Les coordonnées sont au format [longitude, latitude]
    $coords = $data['features'][0]['geometry']['coordinates'];

    return [
        'lat' => $coords[1],
        'lon' => $coords[0],
    ];
}



/**
 * Vérifie si des coordonnées GPS se trouvent dans une zone inondable
 * en interrogeant l'API Géorisques sur 3 référentiels :
 * - TRI  : Territoire à Risque Important d'inondation
 * - AZI  : Atlas des Zones Inondables
 * - PAPI : Programme d'Actions de Prévention des Inondations
 *
 * @param float $lat       Latitude du point à analyser
 * @param float $lon       Longitude du point à analyser
 * @param int   $page      Numéro de page des résultats (défaut : 1)
 * @param int   $page_size Nombre de résultats par page (défaut : 10)
 * @return array Tableau avec les résultats TRI, AZI et PAPI
 */
function est_dans_une_zone_inondable(float $lat, float $lon, int $page = 1, int $page_size = 10) {

    // Les 3 endpoints de l'API Géorisques à interroger
    $urls = [
        'TRI'  => 'https://georisques.gouv.fr/api/v1/gaspar/tri',
        'AZI'  => 'https://georisques.gouv.fr/api/v1/gaspar/azi',
        'PAPI' => 'https://georisques.gouv.fr/api/v1/gaspar/papi',
    ];

    // Paramètres communs envoyés à chaque appel API :
    // - rayon  : zone de recherche autour du point (en mètres)
    // - latlon : coordonnées GPS au format "longitude,latitude"
    $params = [
        "rayon"     => 100,
        "latlon"    => "$lon,$lat",
        "page"      => $page,
        "page_size" => $page_size,
    ];

    // Initialisation des résultats pour chaque référentiel
    // found   : true si un risque d'inondation est détecté
    // risques : liste des libellés des risques trouvés
    $result = ['found' => false, 'risques' => []];

    $url = $urls['TRI'] . '?' . http_build_query($params);

    $response = file_get_contents($url);
    if ($response === false) {
        die("Erreur lors de l'appel à l'API : TRI");
    }

    $data = json_decode($response, true);

    foreach ($data['data'] as $elt_data) {
        foreach ($elt_data['liste_libelle_risque'] as $risque) {

            $num = (string) $risque['num_risque'];

            if (str_starts_with($num, '11') || str_starts_with($num, '23')) {
                $result['found'] = true;
                $result['risques'][] = $risque['libelle_risque_long'];
            }
        }
    }

    return $result;
}

// Comment l'utiliser

$adresse = "10 Rue de la République, 37000 Tours";

$coords = récupérer_coordonnees($adresse);

if (!$coords) {
    die("Adresse introuvable");
}

$lat = $coords['lat'];
$lon = $coords['lon'];

$res_TRI = est_dans_une_zone_inondable($lat, $lon);

if ($res_TRI['found']) {
    echo "TRI : " . implode(', ', array_unique($res_TRI['risques'])) . "<br>";
} else {
    echo "TRI : aucun risque<br>";
}



