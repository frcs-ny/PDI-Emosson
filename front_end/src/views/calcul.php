<?php
// Inclure les fonctions de l'API Géorisques
require_once 'php_est_dans_une_zone_inondation.php';

$score_total = 0;
$details = [];
$niveau_plancher = 0;
$zone_choisie_texte = '';

// --- NOUVEAU : Récupération automatique de la zone via Géorisques ---
$adresse_complete = $_GET['adresse'] . ' ' . $_GET['code_postal'] . ' ' . $_GET['ville'];
$coords = récupérer_coordonnees($adresse_complete);

if ($coords) {
    $vulnerability = est_dans_une_zone_inondable($coords['lat'], $coords['lon']);
    
    if ($vulnerability['found']) {
        // On peut afficher une note d'information
        $details[] = "ℹ️ Analyse Géorisques : Zone à risque détectée (" . implode(', ', array_unique($vulnerability['risques'])) . ")";
        
        // Optionnel : Tu peux forcer la 'zone_choisie_texte' ici si tu veux 
        // que l'API remplace le choix manuel de l'utilisateur.
    } else {
        $details[] = "ℹ️ Analyse Géorisques : Aucun risque majeur (TRI) détecté à cette adresse.";
    }
}
// ------------------------------------------------------------------

// 1. Fusionner les données de la base
$all_questions_db = [];

if (isset($questions_zone_db) && is_array($questions_zone_db)) {
    foreach ($questions_zone_db as $q) {
        $q['prefix'] = 'zone';
        $all_questions_db[] = $q;
    }
}

if (isset($questions_logement_db) && is_array($questions_logement_db)) {
    foreach ($questions_logement_db as $q) {
        $q['prefix'] = 'logement';
        $all_questions_db[] = $q;
    }
}

// 2. Boucler sur toutes les questions combinées
foreach ($all_questions_db as $q) {
    $id = $q['id'];
    $prefix = $q['prefix'];
    $critere = $q['critere'];
    
    $reponses = json_decode($q['reponses_json'], true);
    $scores = json_decode($q['scores_json'], true);

    // On reconstitue le nom de la variable reçue du formulaire
    $input_name = "rep_" . $prefix . "_" . $id;

    // Si l'utilisateur a répondu à cette question précise
    if (isset($_GET[$input_name])) {
        $user_answer = $_GET[$input_name];

        // Cas A : C'est le niveau du plancher ("x")
        if (count($reponses) === 1 && $reponses[0] === 'x') {
            $niveau_plancher = (float) $user_answer;
            $details[] = "$critere : $niveau_plancher m";
        } 
        // Cas B : C'est une liste déroulante (Zone inondable, Travaux, Murs, etc.)
        else {
            $index = (int) $user_answer;
            $texte_reponse = $reponses[$index];
            $score_obtenu = (float) $scores[$index];
            
            $score_total += $score_obtenu;
            $details[] = "$critere ($texte_reponse) : $score_obtenu points";

            // On sauvegarde le nom de la zone pour le calcul H
            if ($critere === 'Zone inondable') {
                $zone_choisie_texte = $texte_reponse;
            }
        }
    }
    
    // 3. Traitement automatique du "Calcul H"
    if ($critere === "Hauteur d'eau potentielle" && $zone_choisie_texte !== '') {
        
        // Dictionnaire des hauteurs de référence
        $hauteurs_reference = [
            "Zone de dissipation de l'énergie (ZDE)" => 1.5,
            "Ecoulement préférentiel (EP)"           => 1.2,
            "Modéré (M)"                             => 0.5,
            "Fort (F)"                               => 1.0,
            "Très fort (TF)"                         => 2.0
        ];

        $niveau_inondation = $hauteurs_reference[$zone_choisie_texte] ?? 0;
        $H = $niveau_inondation - $niveau_plancher;

        // On cherche la règle correspondante dans la base de données
        if ($H >= 0.2) {
            $idx_regle = array_search('h >= 0.2', $reponses);
        } else {
            $idx_regle = array_search('h <= 0.2', $reponses);
        }

        // Si on trouve la règle dans la base, on applique son score
        if ($idx_regle !== false) {
            $score_calc = (float) $scores[$idx_regle];
            $score_total += $score_calc;
            $details[] = "Hauteur d'eau H ($H m) : $score_calc points";
        }
    }
}
?>

<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Résultat - Emosson</title>
    <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
    <div class="container">
        <h1>Résultat de votre évaluation</h1>
        
        <div class="resultat-box">
            <p>Votre score de vulnérabilité est de :</p>
            <h2 style="font-size: 3em; color: #d9534f;"><?php echo $score_total; ?></h2>
        </div>

        <div style="text-align: left; background: #f9f9f9; padding: 15px; margin-top: 20px; border-radius: 5px;">
            <h3>Détails du calcul :</h3>
            <ul>
                <?php foreach($details as $msg): ?>
                    <li><?php echo htmlspecialchars($msg); ?></li>
                <?php endforeach; ?>
            </ul>
        </div>

        <br>
        <a href="questionnaire" class="btn">Recommencer</a>
    </div>
</body>
</html>