<?php

declare(strict_types=1);

require_once 'flight/Flight.php';




Flight::route('/', function() {
    Flight::render('accueil');
});

Flight::route('/accueil', function() {
    Flight::render('accueil');
});

Flight::route('/questionnaire', function() {
    Flight::render('questionnaire');
});

Flight::route('/calcul', function() {
    Flight::render('calcul');
});


Flight::start();

?>