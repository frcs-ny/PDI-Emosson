<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accueil Emosson</title>
    <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
    <!-- Bandeau d'en-tête -->
    <header>
        <div class="header-container">
            <img src="../assets/img/castor_emosson.png" alt="logo">
            <h1>Emosson</h1>
            <a href="/accueil" class="btn">Retourner à l'accueil</a>
        </div>
    </header>

    <!-- Contenu principal -->
    <div class="container">
        <form action="page.php" method="get">

        <!-- question 1 -->

        <!-- question 2 -->
        <p>  Etage :
            <select name="Etage">
            <option value="0" selected>rez-de-chaussée</option>
            <option value="1">premier étage</option>
            <option value="2 ou plus">2eme étage ou plus</option>
            </select>
        </p>
        <!-- question 3 -->
         <p> Nombre de portes au rez-de-chaussée :
            <select name="nb_portes">
            <option value="1" selected>1</option>
            <option value="2">2</option>
            <option value="3">3 ou plus</option>
            </select>
        </p>
        <!-- question 4 -->
        <p> Disposez vous d'une ou plusieurs baies vitrées au rez-de-chaussée :
            <select name="nb_portes">
            <option value="True" selected> oui </option>
            <option value="False"> non </option>
            </select>
        </p>
        <!-- question 5 -->
        <p> Vos murs disposent-ils d'aérations situés à ... :
            <select name="h_aeration">
            <option value="<1" selected> moins d'un mètre de haut </option>
            <option value="<2.5"> moins de 2,5m de haut </option>
            <option value=">2.5"> plus de 2.5m de haut </option>
            <option value="False"> Non, pas d'aération au rez-de-chaussée </option>
            </select>
        </p> 
         <!-- question 6 -->
        <p> En quel matériau est fait votre plancher ? :
            <select name="h_aeration">
            <option value="Carrelage" selected> Carrelage </option>
            <option value="Pierre dure (granit, ardoise, pierre bleue ...)"> Pierre dure (granit, ardoise, pierre bleue ...) </option>
            <option value="Polystyrène"> Polystyrène </option>
            <option value="Béton"> Béton </option>
            <option value="Vinyle"> Vinyle </option>
            <option value="Stratifié spécial"> Stratifié spécial </option>
            <option value="Lino"> Lino </option>
            <option value="Bois"> Bois </option>
            <option value="Moquette"> Moquette </option>
            <option value="Liège"> Liège </option>
            </select>
        </p>
        </form>

       
    </div>

    <!-- Pied de page -->
    <footer>
        <p>&copy; <?php echo date('Y'); ?> Emosson. Tous droits réservés.</p>
    </footer>
</body>
</html>
