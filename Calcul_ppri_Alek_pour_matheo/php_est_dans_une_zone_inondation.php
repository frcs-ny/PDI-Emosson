<?php

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
        "rayon"     => 1000,
        "latlon"    => "$lon,$lat",
        "page"      => $page,
        "page_size" => $page_size,
    ];

    // Initialisation des résultats pour chaque référentiel
    // found   : true si un risque d'inondation est détecté
    // risques : liste des libellés des risques trouvés
    $results = [
        'TRI'  => ['found' => false, 'risques' => []],
        'AZI'  => ['found' => false, 'risques' => []],
        'PAPI' => ['found' => false, 'risques' => []],
    ];

    // On boucle sur chaque URL (TRI, AZI, PAPI)
    foreach ($urls as $type => $base_url) {

        // Construction de l'URL complète avec les paramètres
        // ex: https://georisques.gouv.fr/api/v1/gaspar/tri?rayon=1000&latlon=0.657551,47.388068&...
        $url = $base_url . '?' . http_build_query($params);

        // Appel à l'API et récupération de la réponse JSON brute
        $response = file_get_contents($url);
        if ($response === false) {
            die("Erreur lors de l'appel à l'API : $type");
        }

        // Conversion du JSON en tableau PHP associatif
        $data = json_decode($response, true);

        // On parcourt chaque élément retourné par l'API
        foreach ($data['data'] as $elt_data) {

            // Chaque élément contient une liste de risques associés
            foreach ($elt_data['liste_libelle_risque'] as $risque) {

                $num = (string) $risque['num_risque'];

                // Les codes risque commençant par '11' = inondation
                // Les codes risque commençant par '23' = rupture de barrage
                if (str_starts_with($num, '11') || str_starts_with($num, '23')) {
                    $results[$type]['found'] = true;
                    $results[$type]['risques'][] = $risque['libelle_risque_long'];
                }
            }
        }
    }

    return [$results['TRI'], $results['AZI'], $results['PAPI']];
}

// Coordonnées GPS du point à analyser (ici : Tours, Indre-et-Loire)
$lat = 47.388068;
$lon = 0.657551;

// Appel de la fonction, résultats récupérés dans 3 variables distinctes
[$res_TRI, $res_AZI, $res_PAPI] = est_dans_une_zone_inondable($lat, $lon);

// Affichage des résultats pour chaque référentiel
foreach (['TRI' => $res_TRI, 'AZI' => $res_AZI, 'PAPI' => $res_PAPI] as $nom => $res) {
    if ($res['found']) {
        // array_unique évite les doublons, implode les sépare par des virgules
        echo "$nom : " . implode(', ', array_unique($res['risques'])) . "<br>";
    } else {
        echo "$nom : aucun risque<br>";
    }
}