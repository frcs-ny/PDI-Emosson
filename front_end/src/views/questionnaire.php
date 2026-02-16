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
                <p>Dans quelle zone d'aléas votre bien se situe-t-il ?</p>
                <select name="zone_aleas" required>
                    <option value="" disabled selected>-- Choisir une zone --</option>
                    <option value="ZDE">Zone de dissipation de l'énergie (ZDE)</option>
                    <option value="EP">Ecoulement préférentiel (EP)</option>
                    <option value="M">Modéré (M)</option>
                    <option value="F">Fort (F)</option>
                    <option value="TF">Très fort (TF)</option>
                </select>
            </div>

            <div class="question-block">
                <p>Avez-vous fait des travaux récemment au niveau du rez-de-chaussée ?</p>
                <select name="travaux_recents">
                    <option value="non">Non</option>
                    <option value="oui">Oui</option>
                </select>
            </div>

            <div class="question-block">
                <p>Quel est le niveau du premier plancher habitable de mon habitation (en mètres) ?</p>
                <input type="number" name="niveau_plancher" step="0.01" placeholder="Ex: 0.50" required>
            </div>

            <br>
            <input type="submit" value="Calculer mon score" class="btn">
        </form>
    </div>

    <footer>
        <p>&copy; <?php echo date('Y'); ?> Emosson. Tous droits réservés.</p>
    </footer>
</body>
</html>