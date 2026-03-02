<?php

declare(strict_types=1);

require_once 'flight/Flight.php';

// --- CONNEXION À LA BASE DE DONNÉES ---
// Remplacez par vos vrais identifiants PostgreSQL
Flight::register('db', 'PDO', array('pgsql:host=localhost;dbname=votre_base', 'votre_user', 'votre_mdp'));
// On force l'affichage des erreurs PDO pour le debug
Flight::db()->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

Flight::route('/', function() {
    Flight::render('accueil');
});

Flight::route('/accueil', function() {
    Flight::render('accueil');
});

Flight::route('/PPRI', function() {
    Flight::render('PPRI');
});

// --- ROUTE QUESTIONNAIRE : On charge les questions ---
Flight::route('/questionnaire', function() {
    $db = Flight::db();
    // On utilise array_to_json pour faciliter la lecture en PHP
    $stmt = $db->query("SELECT id, critere, question, array_to_json(reponses) AS reponses_json, array_to_json(scores_vulnerabilite) AS scores_json FROM public.zone_inondable ORDER BY id");
    $questions = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    // On passe la variable $questions à la vue
    Flight::render('questionnaire', ['questions' => $questions]);
});

// --- ROUTE CALCUL : On charge les règles pour le traitement ---
Flight::route('/calcul', function() {
    $db = Flight::db();
    $stmt = $db->query("SELECT id, critere, question, array_to_json(reponses) AS reponses_json, array_to_json(scores_vulnerabilite) AS scores_json FROM public.zone_inondable ORDER BY id");
    $questions_db = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    // On passe les données de la DB à la vue calcul
    Flight::render('calcul', ['questions_db' => $questions_db]);
});

Flight::start();

?>