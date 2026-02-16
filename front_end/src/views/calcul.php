<?php
// Initialisation
$score_total = 0;
$details = [];

// On vérifie si le formulaire a été soumis
if (isset($_GET['zone_aleas'])) {

    // --- 1. CRITÈRE : ZONE INONDABLE ---
    $zone = $_GET['zone_aleas'];
    
    // Tableau des scores selon l'image (colonne "Score de vulnérabilité")
    $scores_zone = [
        "ZDE" => 140,
        "EP"  => 140,
        "M"   => 80,
        "F"   => 110,
        "TF"  => 140
    ];

    // On ajoute le score de la zone
    if (array_key_exists($zone, $scores_zone)) {
        $score_zone = $scores_zone[$zone];
        $score_total += $score_zone;
        $details[] = "Zone $zone : +$score_zone points";
    }

    // --- 2. CRITÈRE : TRAVAUX ---
    // L'image indique 0 point pour Oui ou Non, donc on ne change pas le score
    // Mais on récupère l'info si besoin pour plus tard.
    $travaux = $_GET['travaux_recents'];


    // --- 3. CRITÈRE : HAUTEUR D'EAU POTENTIELLE (Calcul H) ---
    // Formule : H = niveau d'inondation (zone) - niveau du premier plancher
    
    $niveau_plancher = (float) $_GET['niveau_plancher']; // La réponse de l'utilisateur

    // IMPORTANT : L'image dit "niveau d'inondation donné dans la zone".
    // Comme ces chiffres ne sont pas visibles sur l'image, j'ai mis 0.0 par défaut.
    // VOUS DEVEZ REMPLACER CES 0.0 PAR LES VRAIES HAUTEURS D'EAU DE VOS ZONES.
    $hauteurs_reference_zone = [
        "ZDE" => 1.5,  // Exemple : 1.50m
        "EP"  => 1.2,
        "M"   => 0.5,
        "F"   => 1.0,
        "TF"  => 2.0
    ];

    // On récupère la hauteur d'eau de référence pour la zone choisie
    $niveau_inondation = $hauteurs_reference_zone[$zone] ?? 0;

    // Calcul de H
    $H = $niveau_inondation - $niveau_plancher;

    // Application de la règle du tableau
    // Si H >= 0,2 m -> -20 points (bonus de sécurité car plancher bas ?) 
    // Note: Le tableau dit -20, ce qui réduit la vulnérabilité
    if ($H >= 0.2) {
        $score_total -= 20;
        $details[] = "Hauteur différentielle ($H m) >= 0.2m : -20 points";
    } else {
        // Sinon 0
        $details[] = "Hauteur différentielle ($H m) < 0.2m : 0 point";
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
                    <li><?php echo $msg; ?></li>
                <?php endforeach; ?>
            </ul>
        </div>

        <br>
        <a href="questionnaire" class="btn">Recommencer</a>
    </div>
</body>
</html>