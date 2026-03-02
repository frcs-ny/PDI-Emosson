<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Questionnaire Emosson</title>
    <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
    <header>
        <div class="header-container">
            <img src="../assets/img/castor_emosson.png" alt="logo">
            <h1>Emosson - Diagnostic</h1>
            <a href="/accueil" class="btn">Retourner à l'accueil</a>
        </div>
    </header>

    <div class="container">
        <form action="calcul" method="get">

            <div class="question-block">
                <p>Numéro et libellé de la voie :</p>
                <input type="text" name="adresse" placeholder="Ex: 10 Rue de la République" required>
            </div>
            <div class="question-block">
                <p>Code postal :</p>
                <input type="text" name="code_postal" pattern="[0-9]{5}" placeholder="Ex: 37000" title="Veuillez saisir un code postal à 5 chiffres" required>
            </div>
            <div class="question-block">
                <p>Ville :</p>
                <input type="text" name="ville" placeholder="Ex: Tours" required>
            </div>

            <?php 
            // On s'assure que $questions existe (transmis par FlightPHP)
            if (isset($questions)): 
                foreach ($questions as $q): 
                    $reponses = json_decode($q['reponses_json'], true);
                    
                    // On masque la question de calcul automatique (Hauteur d'eau)
                    if ($q['critere'] === "Hauteur d'eau potentielle") {
                        continue; 
                    }
            ?>
                <div class="question-block">
                    <p><strong><?php echo htmlspecialchars($q['critere']); ?> :</strong><br>
                    <?php echo htmlspecialchars($q['question']); ?></p>

                    <?php 
                    // Si la réponse attendue est "x" (champ libre pour le plancher)
                    if (count($reponses) === 1 && $reponses[0] === 'x'): 
                    ?>
                        <input type="number" name="rep_<?php echo $q['id']; ?>" step="0.01" placeholder="Ex: 0.50" required>
                    
                    <?php 
                    // Sinon, c'est une liste déroulante
                    else: 
                    ?>
                        <select name="rep_<?php echo $q['id']; ?>" required>
                            <option value="" disabled selected>-- Choisir --</option>
                            <?php foreach ($reponses as $index => $rep): ?>
                                <option value="<?php echo $index; ?>"><?php echo htmlspecialchars($rep); ?></option>
                            <?php endforeach; ?>
                        </select>
                    <?php endif; ?>
                </div>

            <?php 
                endforeach; 
            endif; 
            ?>

            <br>
            <input type="submit" value="Calculer mon score" class="btn">
        </form>
    </div>

    <footer>
        <p>&copy; <?php echo date('Y'); ?> Emosson. Tous droits réservés.</p>
    </footer>
</body>
</html>