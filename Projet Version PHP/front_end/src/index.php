<?php

declare(strict_types=1);

require_once 'flight/Flight.php';

// --- CONNEXION À LA BASE DE DONNÉES (Native PostgreSQL) ---
$link = pg_connect("host='db' port=5432 dbname='mydb' user='postgres' password='postgres'");

// Petite vérification de sécurité au cas où la base plante
if (!$link) {
    die("Erreur de connexion à la base de données PostgreSQL.");
}

// On stocke la connexion dans Flight sous le nom 'bd'
Flight::set('bd', $link);

Flight::route('/', function() {
    Flight::render('accueil');
});

Flight::route('/accueil', function() {
    Flight::render('accueil');
});

Flight::route('/PPRI', function() {
    Flight::render('PPRI');
});

// --- ROUTE QUESTIONNAIRE : Interroge les 2 tables ---
Flight::route('/questionnaire', function() {
    $db = Flight::get('bd'); 
    
    // Table 1 : Zone Inondable
    $res1 = pg_query($db, "SELECT id, critere, question, array_to_json(reponses) AS reponses_json, array_to_json(scores_vulnerabilite) AS scores_json FROM public.zone_inondable ORDER BY id");
    $questions_zone = $res1 ? pg_fetch_all($res1) : [];
    
    // Table 2 : Questions Logement
    $res2 = pg_query($db, "SELECT id, critere, question, array_to_json(reponses) AS reponses_json, array_to_json(scores_vulnerabilite) AS scores_json FROM public.questions_logement ORDER BY id");
    $questions_logement = $res2 ? pg_fetch_all($res2) : [];
    
    // On passe les deux variables à la vue
    Flight::render('questionnaire', [
        'questions_zone' => $questions_zone,
        'questions_logement' => $questions_logement
    ]);
});

// --- ROUTE CALCUL : Interroge les 2 tables ---
Flight::route('/calcul', function() {
    $db = Flight::get('bd');
    
    // Table 1 : Zone Inondable
    $res1 = pg_query($db, "SELECT id, critere, question, array_to_json(reponses) AS reponses_json, array_to_json(scores_vulnerabilite) AS scores_json FROM public.zone_inondable ORDER BY id");
    $questions_zone_db = $res1 ? pg_fetch_all($res1) : [];
    
    // Table 2 : Questions Logement
    $res2 = pg_query($db, "SELECT id, critere, question, array_to_json(reponses) AS reponses_json, array_to_json(scores_vulnerabilite) AS scores_json FROM public.questions_logement ORDER BY id");
    $questions_logement_db = $res2 ? pg_fetch_all($res2) : [];
    
    Flight::render('calcul', [
        'questions_zone_db' => $questions_zone_db,
        'questions_logement_db' => $questions_logement_db
    ]);
});

Flight::start();

?>