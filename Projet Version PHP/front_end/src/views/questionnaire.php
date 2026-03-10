<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Questionnaire Emosson</title>
    <link rel="stylesheet" href="../assets/css/style.css">
    <style>
        /* Ajustements mineurs pour la navigation qui complètent ton style.css */
        .navigation-buttons {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 30px;
            gap: 15px;
        }
        
        /* On retire la largeur 100% de ton bouton submit pour qu'il s'intègre au flexbox */
        form button[type="submit"]#btn-submit {
            width: auto;
            margin-top: 0;
            padding: 12px 30px;
        }

        /* Style pour les boutons désactivés */
        .btn:disabled, form button[type="submit"]:disabled {
            background: #cccccc;
            color: #666;
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
            border: none;
        }
    </style>
</head>
<body>
    <header>
        <div class="header-container">
            <img src="../assets/img/castor_emosson.png" alt="logo">
            <h1>Emosson - Diagnostic</h1>
            <a href="/accueil" class="btn">Retourner à l'accueil</a>
        </div>
    </header>

    <div class="progress-bar-container">
        <div class="progress-bar" id="globalProgress"></div>
    </div>

    <div class="container">
        <form action="calcul" method="get" id="diagnostic-form">

            <?php 
            // 1. Préparation de toutes les questions (manuelles + BDD)
            $etapes = [];

            // Questions d'introduction
            $etapes[] = [
                'critere' => 'Informations générales',
                'question' => 'Numéro et libellé de la voie :',
                'html' => '<input type="text" name="adresse" placeholder="Ex: 10 Rue de la République" required class="step-input">'
            ];
            $etapes[] = [
                'critere' => 'Informations générales',
                'question' => 'Code postal :',
                'html' => '<input type="text" name="code_postal" pattern="[0-9]{5}" placeholder="Ex: 37000" title="Veuillez saisir un code postal à 5 chiffres" required class="step-input">'
            ];
            $etapes[] = [
                'critere' => 'Informations générales',
                'question' => 'Ville :',
                'html' => '<input type="text" name="ville" placeholder="Ex: Tours" required class="step-input">'
            ];

            // Fusion des tables de la BDD
            $all_questions = [];
            if (isset($questions_zone) && is_array($questions_zone)) {
                foreach ($questions_zone as $q) { $q['prefix'] = 'zone'; $all_questions[] = $q; }
            }
            if (isset($questions_logement) && is_array($questions_logement)) {
                foreach ($questions_logement as $q) { $q['prefix'] = 'logement'; $all_questions[] = $q; }
            }

            // Génération des inputs BDD
            foreach ($all_questions as $q) {
                if ($q['critere'] === "Hauteur d'eau potentielle") continue;

                $reponses = json_decode($q['reponses_json'], true);
                $input_name = "rep_" . $q['prefix'] . "_" . $q['id'];
                
                if (count($reponses) === 1 && $reponses[0] === 'x') {
                    $html = '<input type="number" name="'.$input_name.'" step="0.01" placeholder="Ex: 0.50" required class="step-input">';
                } else {
                    $html = '<select name="'.$input_name.'" required class="step-input">';
                    $html .= '<option value="" disabled selected>-- Choisir --</option>';
                    foreach ($reponses as $index => $rep) {
                        $html .= '<option value="'.$index.'">'.htmlspecialchars($rep).'</option>';
                    }
                    $html .= '</select>';
                }

                $etapes[] = [
                    'critere' => $q['critere'],
                    'question' => $q['question'],
                    'html' => $html
                ];
            }
            ?>

            <div id="form-steps">
                <?php foreach($etapes as $index => $etape): ?>
                    <div class="critere-block <?php echo $index === 0 ? 'unlocking' : 'locked'; ?>" data-step="<?php echo $index; ?>">
                        <div class="critere-header">
                            <?php echo htmlspecialchars($etape['critere']); ?>
                        </div>
                        <p>
                            <?php echo htmlspecialchars($etape['question']); ?>
                            <?php echo $etape['html']; ?>
                        </p>
                    </div>
                <?php endforeach; ?>
            </div>

            <div class="navigation-buttons">
                <button type="button" id="btn-prev" class="btn" style="display: none;">Précédent</button>
                <div style="flex-grow: 1;"></div> 
                <button type="button" id="btn-next" class="btn" disabled>Suivant</button>
                <button type="submit" id="btn-submit" style="display: none;">Calculer mon score</button>
            </div>

        </form>
    </div>

    <footer>
        <p>&copy; <?php echo date('Y'); ?> Emosson. Tous droits réservés.</p>
    </footer>

    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const steps = document.querySelectorAll('.critere-block');
        const btnPrev = document.getElementById('btn-prev');
        const btnNext = document.getElementById('btn-next');
        const btnSubmit = document.getElementById('btn-submit');
        const progressBar = document.getElementById('globalProgress');
        const form = document.getElementById('diagnostic-form');
        
        let currentStep = 0;
        const totalSteps = steps.length;

        function updateUI() {
            // Gestion de l'affichage avec tes classes CSS "locked" et "unlocking"
            steps.forEach((step, index) => {
                if (index === currentStep) {
                    step.classList.remove('locked');
                    step.classList.add('unlocking');
                } else {
                    step.classList.remove('unlocking');
                    step.classList.add('locked');
                }
            });

            // Mise à jour de TA jauge verticale (on modifie le height et non le width)
            const progressPct = (currentStep / (totalSteps - 1)) * 100;
            progressBar.style.height = progressPct + '%';

            // Boutons Précédent / Suivant
            btnPrev.style.display = (currentStep === 0) ? 'none' : 'inline-block';

            if (currentStep === totalSteps - 1) {
                btnNext.style.display = 'none';
                btnSubmit.style.display = 'inline-block';
            } else {
                btnNext.style.display = 'inline-block';
                btnSubmit.style.display = 'none';
            }

            checkValidity();
        }

        function checkValidity() {
            const currentInput = steps[currentStep].querySelector('.step-input');
            const isValid = currentInput.checkValidity() && currentInput.value.trim() !== '';
            
            btnNext.disabled = !isValid;
            if (currentStep === totalSteps - 1) {
                btnSubmit.disabled = !isValid;
            }
        }

        steps.forEach((step, index) => {
            const input = step.querySelector('.step-input');
            
            input.addEventListener('input', checkValidity);
            
            input.addEventListener('change', function() {
                checkValidity();
                
                // Auto-avance pour les menus déroulants
                if (input.tagName.toLowerCase() === 'select' && input.checkValidity()) {
                    setTimeout(() => {
                        if (currentStep < totalSteps - 1) {
                            currentStep++;
                            updateUI();
                        }
                    }, 300);
                }
            });

            // Touche "Entrée" pour avancer
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    if (!btnNext.disabled && currentStep < totalSteps - 1) {
                        currentStep++;
                        updateUI();
                    } else if (currentStep === totalSteps - 1 && !btnSubmit.disabled) {
                        form.submit();
                    }
                }
            });
        });

        btnNext.addEventListener('click', () => {
            if (currentStep < totalSteps - 1) {
                currentStep++;
                updateUI();
            }
        });

        btnPrev.addEventListener('click', () => {
            if (currentStep > 0) {
                currentStep--;
                updateUI();
            }
        });

        updateUI();
    });
    </script>
</body>
</html>