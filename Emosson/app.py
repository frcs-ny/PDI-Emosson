from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import psycopg2
import psycopg2.extras
import os
import json

from estdansunezich import adresse_vers_coordonnees, recuperer_info_toutes_les_station, trouver_station_plus_proche, recuperer_geom_zich, est_dans_une_zich

app = Flask(
    __name__,
    template_folder='front_end/templates',
    static_folder='front_end/static'
)

# connexion à la BDD
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
conn.autocommit = True

# Requetes SQL pour récupérer les questions
def recuperer_questions():
    curseur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    curseur.execute("SELECT id, critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations, inclure_stats FROM public.zone_inondable ORDER BY id")
    questions_zone = [dict(ligne) for ligne in curseur.fetchall()]
    for question in questions_zone:
        question['prefix'] = 'zone'

    curseur.execute("SELECT id, critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations, inclure_stats FROM public.questions_logement ORDER BY id")
    questions_logement = [dict(ligne) for ligne in curseur.fetchall()]
    for question in questions_logement:
        question['prefix'] = 'logement'

    curseur.execute("SELECT id, critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations, inclure_stats FROM public.protection_personnes ORDER BY id")
    questions_protection = [dict(ligne) for ligne in curseur.fetchall()]
    for question in questions_protection:
        question['prefix'] = 'protection'

    score_max_theorique = 0.0
    toutes_les_questions = questions_zone + questions_logement + questions_protection
    
    # On calcule le score maximum qu'un utilisateur pourrait théoriquement atteindre
    for question in toutes_les_questions:
        scores = question.get('scores_vulnerabilite')
        if scores:
            try:
                # On convertit les scores en nombres décimaux en ignorant les valeurs vides
                scores_valides = [float(score) for score in scores if score is not None]
                if scores_valides:
                    score_max_theorique += max(scores_valides)
            except (ValueError, TypeError):
                pass 

    return questions_zone, questions_logement, questions_protection, score_max_theorique


@app.route('/')
@app.route('/accueil')
def accueil():
    return render_template('accueil.html', now=datetime.now())

@app.route('/actualite')
def actualite():
    return render_template('actualite.html', now=datetime.now())

@app.route('/qui_sommes_nous')
def qui_sommes_nous():
    return render_template('qui_sommes_nous.html', now=datetime.now())

@app.route('/questionnaire')
def questionnaire():
    questions_zone, questions_logement, questions_protection, _ = recuperer_questions()

    # Etapes de base (informations utilisateur)
    etapes = [
        {'critere': 'Informations générales', 'question': 'Nom et Prénom :',                 'type': 'text', 'name': 'nom',         'placeholder': 'Ex: Dupont',                  'pattern': None, 'a_dependance': False},
        {'critere': 'Informations générales', 'question': 'Numéro et libellé de la voie :',  'type': 'text', 'name': 'adresse',     'placeholder': 'Ex: 10 Rue de la République', 'pattern': None, 'a_dependance': False},
        {'critere': 'Informations générales', 'question': 'Code postal :',                   'type': 'text', 'name': 'code_postal', 'placeholder': 'Ex: 37000',                   'pattern': '[0-9]{5}', 'a_dependance': False},
        {'critere': 'Informations générales', 'question': 'Ville :',                         'type': 'text', 'name': 'ville',       'placeholder': 'Ex: Tours',                   'pattern': None, 'a_dependance': False},
    ]

    toutes_les_questions = questions_zone + questions_logement + questions_protection
    for question in toutes_les_questions:
        # On ignore les questions qui sont calculées automatiquement (dont la 21)
        if question['critere'] in ["Hauteur d'eau potentielle", "Zone inondable"] or (question['prefix'] == 'logement' and question['id'] == 21):
            continue

        reponses = question['reponses']  
        nom_champ = f"rep_{question['prefix']}_{question['id']}"
        nom_parent = f"rep_{question['prefix']}_{question['id_question_liee']}" if question.get('a_dependance') else None

        etape_base = {
            'critere': question['critere'], 
            'question': question['question'],
            'name': nom_champ,
            'a_dependance': question.get('a_dependance', False),
            'id_question_liee': question.get('id_question_liee'),
            'parent_name': nom_parent
        }

        # Si la seule réponse possible est "x", c'est qu'on attend un nombre
        if len(reponses) == 1 and reponses[0] == 'x':
            etape_base.update({'type': 'number', 'placeholder': 'Ex: 0.50 m'})
        else:
            # Sinon on propose une liste déroulante
            etape_base.update({'type': 'select', 'options': list(enumerate(reponses))})
            
        etapes.append(etape_base)

    return render_template('questionnaire.html', etapes=etapes, now=datetime.now())


@app.route('/calcul')
def calcul():
    questions_zone, questions_logement, questions_protection, _ = recuperer_questions()
    toutes_les_questions_bdd = questions_zone + questions_logement + questions_protection
    
    details_calcul = []
    
    nom_utilisateur = request.args.get('nom', 'Utilisateur inconnu').strip()
    if not nom_utilisateur:
        nom_utilisateur = 'Utilisateur inconnu'
        
    # On structure les recommandations par catégories pour l'affichage final
    recommandations_groupees = {
        'zone': [],
        'logement': [],
        'protection': []
    }
    noms_categories = {
        'zone': 'Risques en zone inondable',
        'logement': 'Aménagement du logement',
        'protection': 'Protection des personnes'
    }
    rappel_questions_reponses = []
    
    niveau_plancher = 0.0
    
    adresse_brute = request.args.get('adresse', '')
    cp_brut = request.args.get('code_postal', '')
    ville_brute = request.args.get('ville', '')
    adresse_complete = f"{adresse_brute} {cp_brut} {ville_brute}".strip()
    
    longitude, latitude = None, None
    dans_zich = False
    hmax_zich = 0.0
    zone_choisie_texte = ""
    geometries_zich = None

    if adresse_complete:
        try:
            # Etape 1 : Obtenir les coordonnées GPS depuis l'adresse
            resultat_coordonnees = adresse_vers_coordonnees(adresse_complete)
            longitude = resultat_coordonnees['lon']
            latitude = resultat_coordonnees['lat']
            
            # Etape 2 : Chercher si l'adresse est dans une zone inondable (ZICH)
            liste_stations = recuperer_info_toutes_les_station()
            code_station, nom_station = trouver_station_plus_proche(liste_stations, longitude, latitude)
            hauteur_max_station, geom_brute_zich = recuperer_geom_zich(code_station)
            dans_zich, hmin_zich, hmax_zich, geometries_zich = est_dans_une_zich(code_station, longitude, latitude, hauteur_max_station, geom_brute_zich)
            
            if dans_zich:
                # Application du niveau d'alerte selon la hauteur d'eau
                if hmax_zich <= 1.0:
                    zone_choisie_texte = "Modéré"
                elif 1.0 < hmax_zich <= 2.50:
                    zone_choisie_texte = "Fort"
                else:
                    zone_choisie_texte = "Très fort"
                
                details_calcul.append(f"🌊 Analyse ZICH : En zone inondable (Station: {nom_station})")
                details_calcul.append(f"🌊 Submersion estimée : {hmax_zich} m -> Aléa automatiquement classé '{zone_choisie_texte}'")
            else:
                details_calcul.append("🌊 Analyse ZICH : Hors zone inondable pour le scénario extrême étudié.")
                
        except Exception as erreur:
            details_calcul.append(f"⚠️ Erreur lors de l'analyse de l'adresse. ({erreur})")


    # Sauvegarde des réponses de l'utilisateur en base de données
    reponses_utilisateur = {}
    curseur = conn.cursor()
    
    for question in toutes_les_questions_bdd:
        nom_champ = f"rep_{question['prefix']}_{question['id']}"
        reponse_donnee = request.args.get(nom_champ)
        
        if reponse_donnee is not None and str(reponse_donnee).strip() != '':
            texte_a_sauvegarder = ""
            
            if len(question['reponses']) == 1 and question['reponses'][0] == 'x':
                reponses_utilisateur[(question['prefix'], question['id'])] = reponse_donnee
                texte_a_sauvegarder = str(reponse_donnee)
            else:
                try:
                    indice = int(reponse_donnee)
                    reponses_utilisateur[(question['prefix'], question['id'])] = question['reponses'][indice]
                    texte_a_sauvegarder = question['reponses'][indice]
                except (ValueError, IndexError):
                    pass
            
            # Insertion en base de données
            if texte_a_sauvegarder:
                try:
                    curseur.execute(
                        "INSERT INTO public.reponses_utilisateurs (id_question, categorie, reponse_donnee) VALUES (%s, %s, %s)",
                        (question['id'], question['prefix'], texte_a_sauvegarder)
                    )
                except Exception as erreur:
                    print(f"Erreur d'insertion en BDD: {erreur}")

    # Calcul des scores du questionnaire
    score_total = 0.0
    score_max_dynamique = 0.0
    
    for question in toutes_les_questions_bdd:
        id_question = question['id']
        prefixe = question['prefix']
        critere = question['critere']
        reponses_possibles = question['reponses']
        scores = question['scores_vulnerabilite']
        recommandations = question.get('recommandations', [])
        
        # Gestion des questions dépendantes (on l'ignore si la question parente a été répondue par "Non")
        if question.get('a_dependance') and question.get('id_question_liee'):
            reponse_parente = reponses_utilisateur.get((prefixe, question['id_question_liee']))
            if not reponse_parente or reponse_parente.strip().lower() == 'non':
                continue
                
        # Mise à jour du score maximum que l'utilisateur aurait pu avoir
        try:
            scores_valides = [float(s) for s in scores if s is not None]
            if scores_valides:
                score_max_dynamique += max(scores_valides)
        except (ValueError, TypeError):
            pass
            
        # --- Traitement automatique des risques d'inondation ---
        if critere == 'Zone inondable':
            if dans_zich and zone_choisie_texte != '':
                indice_trouve = -1
                for index_reponse, texte_rep in enumerate(reponses_possibles):
                    if zone_choisie_texte in texte_rep: 
                        indice_trouve = index_reponse
                        break
                
                if indice_trouve != -1:
                    score_obtenu = float(scores[indice_trouve])
                    score_total += score_obtenu
                    details_calcul.append(f"Automatique - {critere} ({reponses_possibles[indice_trouve]}) : {score_obtenu} points")
            continue 

        if critere == "Hauteur d'eau potentielle":
            if dans_zich:
                hauteur_dans_logement = hmax_zich - niveau_plancher
                
                indice_regle = -1
                if hauteur_dans_logement >= 0.2 and 'h >= 0.2' in reponses_possibles:
                    indice_regle = reponses_possibles.index('h >= 0.2')
                elif hauteur_dans_logement < 0.2 and 'h <= 0.2' in reponses_possibles:
                    indice_regle = reponses_possibles.index('h <= 0.2')
                    
                if indice_regle != -1:
                    score_calcule = float(scores[indice_regle])
                    score_total += score_calcule
                    details_calcul.append(f"Automatique - Eau dans le logement ({hauteur_dans_logement:.2f} m) : {score_calcule} points")
            continue 

        # Vérification automatique si l'équipement de chauffage est submergé
        if prefixe == 'logement' and id_question == 21:
            valeur_hauteur_equipement = reponses_utilisateur.get(('logement', 20))
            if valeur_hauteur_equipement and dans_zich:
                try:
                    hauteur_equip = float(valeur_hauteur_equipement)
                    
                    # 0 = au-dessus (0 pts), 1 = en-dessous (10 pts)
                    indice_auto = 1 if hauteur_equip < hmax_zich else 0
                    
                    score_calcule = float(scores[indice_auto])
                    score_total += score_calcule
                    
                    texte_reponse = reponses_possibles[indice_auto]
                    texte_reco = recommandations[indice_auto] if recommandations and len(recommandations) > indice_auto else ""
                    
                    details_calcul.append(f"Automatique - Chauffage : {texte_reponse} (Equipement: {hauteur_equip}m vs Crue: {hmax_zich:.2f}m)")
                    
                    rappel_questions_reponses.append({
                        'question': question['question'],
                        'reponse': texte_reponse,
                        'recommandation': texte_reco
                    })
                    
                    if texte_reco and texte_reco not in recommandations_groupees[prefixe]:
                        recommandations_groupees[prefixe].append(texte_reco)
                except ValueError:
                    pass
            continue

        # --- Traitement standard pour les autres questions manuelles ---
        nom_champ = f"rep_{prefixe}_{id_question}"
        reponse_fournie = request.args.get(nom_champ)
        
        if reponse_fournie is not None and str(reponse_fournie).strip() != '':
            texte_reponse = ""
            texte_reco = ""
            
            # S'il y a eu une valeur numérique saisie (champ libre "x")
            if len(reponses_possibles) == 1 and reponses_possibles[0] == 'x':
                try:
                    reponse_decimale = float(reponse_fournie)
                    if prefixe == 'zone' and critere == 'Niveau du plancher':
                        niveau_plancher = reponse_decimale
                    texte_reponse = f"{reponse_decimale} m"
                    details_calcul.append(f"{critere} : {reponse_decimale} m")
                    texte_reco = recommandations[0] if recommandations and len(recommandations) > 0 else ""
                except ValueError:
                    pass
            else:
                # Choix dans une liste déroulante
                try:
                    indice = int(reponse_fournie)
                    texte_reponse = reponses_possibles[indice]
                    score_obtenu = float(scores[indice])
                    
                    score_total += score_obtenu
                    details_calcul.append(f"{critere} ({texte_reponse}) : {score_obtenu} points")
                    texte_reco = recommandations[indice] if recommandations and len(recommandations) > indice else ""
                except (ValueError, IndexError):
                    pass

            if texte_reponse:
                rappel_questions_reponses.append({
                    'question': question['question'],
                    'reponse': texte_reponse,
                    'recommandation': texte_reco
                })
                
                if texte_reco and texte_reco not in recommandations_groupees[prefixe]:
                    recommandations_groupees[prefixe].append(texte_reco)


    # Mise en forme finale des recommandations
    recommandations_finales = []
    for categorie_pref, liste_recos in recommandations_groupees.items():
        if liste_recos: 
            recommandations_finales.append({
                'titre': noms_categories[categorie_pref],
                'recos': liste_recos
            })

    # Calcul d'un pourcentage pour le score global et création d'une couleur (vert vers rouge)
    if score_max_dynamique > 0:
        score_pourcentage = (score_total / score_max_dynamique) * 100
    else:
        score_pourcentage = 0.0
        
    score_pourcentage = max(0, min(100, int(round(score_pourcentage))))
    teinte_couleur = max(0, 120 - (score_pourcentage * 1.2))
    couleur_score = f"hsl({teinte_couleur}, 100%, 40%)"
    
    # Enregistrement du score global pour nos statistiques
    try:
        curseur.execute("INSERT INTO public.scores_questionnaires (score) VALUES (%s)", (score_pourcentage,))
    except Exception as erreur:
        print(f"Erreur d'insertion du score global : {erreur}")
    
    # Sérialisation des polygones pour la carte sur l'interface
    geometrie_json = json.dumps(geometries_zich) if geometries_zich else 'null'

    return render_template('calcul.html', 
                       nom=nom_utilisateur,
                       score_total=round(score_total, 2),
                       score_cent=score_pourcentage,
                       couleur_score=couleur_score,
                       details=details_calcul,
                       lon=longitude,          
                       lat=latitude,     
                       adresse=adresse_complete,   
                       dans_zich=dans_zich,
                       hmax_zich=round(hmax_zich, 2) if hmax_zich else 0, 
                       zone_choisie_texte=zone_choisie_texte,
                       geom=geometrie_json,
                       recommandations_finales=recommandations_finales,
                       rappel_qr=rappel_questions_reponses)


@app.route('/statistiques')
def statistiques():
    questions_zone, questions_logement, questions_protection, _ = recuperer_questions()
    
    # On ne garde que les questions configurées pour apparaître dans les statistiques
    questions_zone = [q for q in questions_zone if q.get('inclure_stats') is True]
    questions_logement = [q for q in questions_logement if q.get('inclure_stats') is True]
    questions_protection = [q for q in questions_protection if q.get('inclure_stats') is True]
    
    categorie = request.args.get('categorie', 'logement')
    
    statistiques_reponses = []
    question_texte = "Question introuvable"
    id_question = 0
    moyenne_scores = None
    total_participants = 0
    
    curseur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if categorie == 'global':
        # On calcule simplement la moyenne de tous les questionnaires complétés
        try:
            curseur.execute("SELECT ROUND(AVG(score), 1) AS moyenne, COUNT(*) AS total FROM public.scores_questionnaires")
            donnees = curseur.fetchone()
            moyenne_scores = donnees['moyenne'] if donnees and donnees['moyenne'] is not None else None
            total_participants = donnees['total'] if donnees else 0
            question_texte = "Moyenne globale"
        except Exception as erreur:
            print(f"Erreur SQL lors du calcul des statistiques globales: {erreur}")
            
    else:
        # On définit un ID par défaut sur la première question de la catégorie choisie
        id_par_defaut = 1
        if categorie == 'logement' and questions_logement:
            id_par_defaut = questions_logement[0]['id']
        elif categorie == 'zone' and questions_zone:
            id_par_defaut = questions_zone[0]['id']
        elif categorie == 'protection' and questions_protection:
            id_par_defaut = questions_protection[0]['id']
            
        id_question = request.args.get('id', id_par_defaut, type=int)
        
        if categorie == 'logement':
            nom_table = "public.questions_logement"
        elif categorie == 'protection':
            nom_table = "public.protection_personnes"
        else:
            nom_table = "public.zone_inondable"
            
        try:
            curseur.execute(f"SELECT question FROM {nom_table} WHERE id = %s", (id_question,))
            resultat = curseur.fetchone()
            if resultat:
                question_texte = resultat['question']
                
            # Cette requête récupère la répartition des réponses pour une question donnée
            requete_sql = """
                SELECT 
                    reponse_donnee AS reponse,
                    COUNT(*) AS compte,
                    SUM(COUNT(*)) OVER() AS total,
                    ROUND((COUNT(*) * 100.0) / SUM(COUNT(*)) OVER(), 1) AS pourcentage
                FROM 
                    public.reponses_utilisateurs
                WHERE 
                    categorie = %s AND id_question = %s
                GROUP BY 
                    reponse_donnee
                ORDER BY 
                    compte DESC;
            """
            curseur.execute(requete_sql, (categorie, id_question))
            statistiques_reponses = curseur.fetchall()
        except Exception as erreur:
            print(f"Erreur SQL lors du calcul des statistiques spécifiques: {erreur}")

    return render_template('statistiques.html', 
                           stats=statistiques_reponses, 
                           question_texte=question_texte, 
                           id=id_question, 
                           categorie=categorie,
                           moyenne=moyenne_scores,
                           total=total_participants,
                           questions_zone=questions_zone,
                           questions_logement=questions_logement,
                           questions_protection=questions_protection,
                           now=datetime.now())

@app.route('/avis', methods=['GET', 'POST'])
def avis():
    # On regarde d'où vient l'utilisateur (URL)
    mode = request.args.get('mode', '')
    
    if request.method == 'POST':
        commentaire = request.form.get('commentaire')
        note = request.form.get('note')
        
        # Mode soumis dans le formulaire
        mode_formulaire = request.form.get('mode', '')
        
        if commentaire and note:
            try:
                curseur = conn.cursor()
                curseur.execute(
                    "INSERT INTO public.avis (commentaire, note) VALUES (%s, %s)",
                    (commentaire.strip(), int(note))
                )
            except Exception as erreur:
                print(f"Erreur d'insertion d'un nouvel avis: {erreur}")
                
        # Si on vient de la fin du questionnaire, on le renvoie à l'accueil
        if mode_formulaire == 'fin_parcours':
            return redirect(url_for('accueil'))
        return redirect(url_for('avis'))

    curseur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    curseur.execute("SELECT commentaire, note, date_avis FROM public.avis ORDER BY date_avis DESC")
    liste_avis = curseur.fetchall()

    # On passe la variable "mode" au template
    return render_template('avis.html', liste_avis=liste_avis, now=datetime.now(), mode=mode)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')