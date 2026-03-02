<?php

declare(strict_types=1);

require_once 'flight/Flight.php';

// --- CONNEXION À LA BASE DE DONNÉES (Native PostgreSQL) ---
$link = pg_connect("host='db' port=5432 dbname='mydb' user='postgres' password='postgres'");

// Petite vérification de sécurité au cas où la base plante
if (!$link) {
    die("Erreur de connexion à la base de données PostgreSQL.");
}

// On stocke la connexion dans Flight sous le nom 'bd' (comme vous l'avez demandé)
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

// --- ROUTE QUESTIONNAIRE : Adaptée pour pg_query ---
Flight::route('/questionnaire', function() {
    // On récupère la connexion stockée
    $db = Flight::get('bd'); 
    
    // On exécute la requête avec la fonction native
    $result = pg_query($db, "SELECT id, critere, question, array_to_json(reponses) AS reponses_json, array_to_json(scores_vulnerabilite) AS scores_json FROM public.zone_inondable ORDER BY id");
    
    // On transforme le résultat en tableau associatif
    $questions = [];
    if ($result) {
        $questions = pg_fetch_all($result);
    }
    
    // On passe la variable à la vue
    Flight::render('questionnaire', ['questions' => $questions]);
});

// --- ROUTE CALCUL : Adaptée pour pg_query ---
Flight::route('/calcul', function() {
    $db = Flight::get('bd');
    
    $result = pg_query($db, "SELECT id, critere, question, array_to_json(reponses) AS reponses_json, array_to_json(scores_vulnerabilite) AS scores_json FROM public.zone_inondable ORDER BY id");
    
    $questions_db = [];
    if ($result) {
        $questions_db = pg_fetch_all($result);
    }
    
    Flight::render('calcul', ['questions_db' => $questions_db]);
});

Flight::start();

?>