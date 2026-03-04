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
            /*
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
            */


            
            $questionsByCritere = [];
            if (isset($questions)) {
                foreach ($questions as $q) {
                    if ($q['critere'] === "Hauteur d'eau potentielle") continue;
                    $questionsByCritere[$q['critere']][] = $q;
                }
            }
            $criteres = array_keys($questionsByCritere);
            ?>

            <link rel="stylesheet" href="/css/questionnaire.css">

            <!-- Barre de progression globale -->
            <div class="progress-bar-container">
                <div class="progress-bar" id="globalProgress"></div>
            </div>

            <?php foreach ($criteres as $i => $critere): ?>
                <div class="critere-block <?php echo $i > 0 ? 'locked' : ''; ?>"
                    data-critere-index="<?php echo $i; ?>"
                    id="critere-<?php echo $i; ?>">

                    <div class="critere-header"><?php echo htmlspecialchars($critere); ?></div>

                    <?php foreach ($questionsByCritere[$critere] as $q):
                        $reponses = json_decode($q['reponses_json'], true);
                    ?>
                        <div class="question-block">
                            <p><br>
                            <?php echo htmlspecialchars($q['question']); ?></p>

                            <?php if (count($reponses) === 1 && $reponses[0] === 'x'): ?>
                                <input type="number"
                                    name="rep_<?php echo $q['id']; ?>"
                                    step="0.01"
                                    placeholder="Ex: 0.50"
                                    required
                                    class="critere-input"
                                    data-critere="<?php echo $i; ?>">

                            <?php else: ?>
                                <select name="rep_<?php echo $q['id']; ?>"
                                        required
                                        class="critere-input"
                                        data-critere="<?php echo $i; ?>">
                                    <option value="" disabled selected>-- Choisir --</option>
                                    <?php foreach ($reponses as $index => $rep): ?>
                                        <option value="<?php echo $index; ?>"><?php echo htmlspecialchars($rep); ?></option>
                                    <?php endforeach; ?>
                                </select>
                            <?php endif; ?>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endforeach; ?>

            <script>
            (function () {
                const totalCriteres = <?php echo count($criteres); ?>;

                function getCritereInputs(index) {
                    return document.querySelectorAll(`.critere-input[data-critere="${index}"]`);
                }

                function isCritereComplete(index) {
                    const inputs = getCritereInputs(index);
                    return [...inputs].every(input => input.value !== '' && input.value !== null);
                }

                function unlockNext(index) {
                    const next = document.getElementById(`critere-${index + 1}`);
                    if (next && next.classList.contains('locked')) {
                        next.classList.remove('locked');
                        next.classList.add('unlocking');
                        next.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                    updateProgress();
                }

                function updateProgress() {
                    let completed = 0;
                    for (let i = 0; i < totalCriteres; i++) {
                        if (isCritereComplete(i)) completed++;
                    }
                    const pct = Math.round((completed / totalCriteres) * 100);
                    document.getElementById('globalProgress').style.height = pct + '%';
                }

                for (let i = 0; i < totalCriteres; i++) {
                    getCritereInputs(i).forEach(input => {
                        input.addEventListener('change', () => {
                            if (isCritereComplete(i)) unlockNext(i);
                            updateProgress();
                        });
                        input.addEventListener('input', () => {
                            if (isCritereComplete(i)) unlockNext(i);
                            updateProgress();
                        });
                    });
                }
            })();
            </script>

            

            <br>
            <input type="submit" value="Calculer mon score" class="btn">
        </form>
    </div>

    <footer>
        <p>&copy; <?php echo date('Y'); ?> Emosson. Tous droits réservés.</p>
    </footer>
</body>
</html>