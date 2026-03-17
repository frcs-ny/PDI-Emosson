from flask import Flask, render_template, request
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

# requetes SQL
def get_questions():
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT id, critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations FROM public.zone_inondable ORDER BY id")
    questions_zone = [dict(row) for row in cur.fetchall()]
    for q in questions_zone:
        q['prefix'] = 'zone'

    cur.execute("SELECT id, critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations FROM public.questions_logement ORDER BY id")
    questions_logement = [dict(row) for row in cur.fetchall()]
    for q in questions_logement:
        q['prefix'] = 'logement'

    cur.execute("SELECT id, critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations FROM public.protection_personnes ORDER BY id")
    questions_protection = [dict(row) for row in cur.fetchall()]
    for q in questions_protection:
        q['prefix'] = 'protection'

    score_max_theorique = 0.0
    all_questions = questions_zone + questions_logement + questions_protection
    for q in all_questions:
        scores = q.get('scores_vulnerabilite')
        if scores:
            try:
                valid_scores = [float(s) for s in scores if s is not None]
                if valid_scores:
                    score_max_theorique += max(valid_scores)
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
    questions_zone, questions_logement, questions_protection, _ = get_questions()

    etapes = [
        {'critere': 'Informations générales', 'question': 'Nom et Prénom :',                 'type': 'text', 'name': 'nom',         'placeholder': 'Ex: Dupont',                  'pattern': None, 'a_dependance': False},
        {'critere': 'Informations générales', 'question': 'Numéro et libellé de la voie :',  'type': 'text', 'name': 'adresse',     'placeholder': 'Ex: 10 Rue de la République', 'pattern': None, 'a_dependance': False},
        {'critere': 'Informations générales', 'question': 'Code postal :',                   'type': 'text', 'name': 'code_postal', 'placeholder': 'Ex: 37000',                   'pattern': '[0-9]{5}', 'a_dependance': False},
        {'critere': 'Informations générales', 'question': 'Ville :',                         'type': 'text', 'name': 'ville',       'placeholder': 'Ex: Tours',                   'pattern': None, 'a_dependance': False},
    ]

    questions = questions_zone + questions_logement + questions_protection
    for q in questions:
        # On ignore les questions automatiques pour ne pas les afficher (dont la 21)
        if q['critere'] in ["Hauteur d'eau potentielle", "Zone inondable"] or (q['prefix'] == 'logement' and q['id'] == 21):
            continue

        reponses = q['reponses']  
        input_name = f"rep_{q['prefix']}_{q['id']}"
        parent_name = f"rep_{q['prefix']}_{q['id_question_liee']}" if q.get('a_dependance') else None

        etape_base = {
            'critere': q['critere'], 
            'question': q['question'],
            'name': input_name,
            'a_dependance': q.get('a_dependance', False),
            'id_question_liee': q.get('id_question_liee'),
            'parent_name': parent_name
        }

        if len(reponses) == 1 and reponses[0] == 'x':
            etape_base.update({'type': 'number', 'placeholder': 'Ex: 0.50 m'})
        else:
            etape_base.update({'type': 'select', 'options': list(enumerate(reponses))})
            
        etapes.append(etape_base)

    return render_template('questionnaire.html', etapes=etapes, now=datetime.now())


@app.route('/calcul')
def calcul():
    questions_zone, questions_logement, questions_protection, _ = get_questions()
    all_questions_db = questions_zone + questions_logement + questions_protection
    
    details = []
    
    nom_utilisateur = request.args.get('nom', 'Utilisateur inconnu').strip()
    if not nom_utilisateur:
        nom_utilisateur = 'Utilisateur inconnu'
        
    # Structuration par catégories
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
    rappel_qr = []
    
    niveau_plancher = 0.0
    
    adresse_brute = request.args.get('adresse', '')
    cp_brut = request.args.get('code_postal', '')
    ville_brute = request.args.get('ville', '')
    adresse_complete = f"{adresse_brute} {cp_brut} {ville_brute}".strip()
    
    lon, lat = None, None
    dans_zich = False
    hmax_zich = 0.0
    zone_choisie_texte = ""
    geom = None

    if adresse_complete:
        try:
            # 1. Obtenir les coordonnées GPS
            result_coords = adresse_vers_coordonnees(adresse_complete)
            lon = result_coords['lon']
            lat = result_coords['lat']
            
            # 2. Chercher les données de submersion ZICH
            stations = recuperer_info_toutes_les_station()
            code_station, nom_station = trouver_station_plus_proche(stations, lon, lat)
            hauteur_max_station, geom_zich = recuperer_geom_zich(code_station)
            dans_zich, hmin_zich, hmax_zich, geom = est_dans_une_zich(code_station, lon, lat, hauteur_max_station, geom_zich)
            
            if dans_zich:
                # 3. Application de la classification du tableau PPRI
                if hmax_zich <= 1.0:
                    zone_choisie_texte = "Modéré"
                elif 1.0 < hmax_zich <= 2.50:
                    zone_choisie_texte = "Fort"
                else:
                    zone_choisie_texte = "Très fort"
                
                details.append(f"🌊 Analyse ZICH : En zone inondable (Station: {nom_station})")
                details.append(f"🌊 Submersion estimée : {hmax_zich} m -> Aléa automatiquement classé '{zone_choisie_texte}'")
            else:
                details.append("🌊 Analyse ZICH : Hors zone inondable pour le scénario extrême étudié.")
                
        except Exception as e:
            details.append(f"⚠️ Erreur lors de l'analyse spatiale de l'adresse. ({e})")


    # 1. Récupération des réponses saisies ET sauvegarde en BDD
    user_answers_text = {}
    cur = conn.cursor() # Création d'un curseur pour l'insertion
    
    for q in all_questions_db:
        input_name = f"rep_{q['prefix']}_{q['id']}"
        user_answer = request.args.get(input_name)
        
        if user_answer is not None and str(user_answer).strip() != '':
            texte_a_sauvegarder = ""
            
            if len(q['reponses']) == 1 and q['reponses'][0] == 'x':
                user_answers_text[(q['prefix'], q['id'])] = user_answer
                texte_a_sauvegarder = str(user_answer)
            else:
                try:
                    index = int(user_answer)
                    user_answers_text[(q['prefix'], q['id'])] = q['reponses'][index]
                    texte_a_sauvegarder = q['reponses'][index]
                except (ValueError, IndexError):
                    pass
            
            # Sauvegarde de la réponse dans la nouvelle table
            if texte_a_sauvegarder:
                try:
                    cur.execute(
                        "INSERT INTO public.reponses_utilisateurs (id_question, categorie, reponse_donnee) VALUES (%s, %s, %s)",
                        (q['id'], q['prefix'], texte_a_sauvegarder)
                    )
                except Exception as e:
                    print(f"Erreur d'insertion en BDD: {e}")

    # 2. Calcul du score
    score_total = 0.0
    score_max_dynamique = 0.0
    
    for q in all_questions_db:
        qid = q['id']
        prefix = q['prefix']
        critere = q['critere']
        reponses = q['reponses']
        scores = q['scores_vulnerabilite']
        recommandations = q.get('recommandations', [])
        
        # Dépendances
        if q.get('a_dependance') and q.get('id_question_liee'):
            parent_answer = user_answers_text.get((prefix, q['id_question_liee']))
            if not parent_answer or parent_answer.strip().lower() == 'non':
                continue
                
        # Score max dynamique
        try:
            valid_scores = [float(s) for s in scores if s is not None]
            if valid_scores:
                score_max_dynamique += max(valid_scores)
        except (ValueError, TypeError):
            pass
            
        # Traitement automatisé de la Zone Inondable
        if critere == 'Zone inondable':
            if dans_zich and zone_choisie_texte != '':
                idx = -1
                for i, r in enumerate(reponses):
                    if zone_choisie_texte in r: 
                        idx = i
                        break
                
                if idx != -1:
                    score_obtenu = float(scores[idx])
                    score_total += score_obtenu
                    details.append(f"Automatique - {critere} ({reponses[idx]}) : {score_obtenu} points")
            continue 

        # Traitement automatisé de la Hauteur d'eau
        if critere == "Hauteur d'eau potentielle":
            if dans_zich:
                H = hmax_zich - niveau_plancher
                
                idx_regle = -1
                if H >= 0.2 and 'h >= 0.2' in reponses:
                    idx_regle = reponses.index('h >= 0.2')
                elif H < 0.2 and 'h <= 0.2' in reponses:
                    idx_regle = reponses.index('h <= 0.2')
                    
                if idx_regle != -1:
                    score_calc = float(scores[idx_regle])
                    score_total += score_calc
                    details.append(f"Automatique - Eau dans le logement ({H:.2f} m) : {score_calc} points")
            continue 

        # Traitement automatisé de la Question 21 (Chauffage vs Crue)
        if prefix == 'logement' and qid == 21:
            valeur_q20 = user_answers_text.get(('logement', 20))
            if valeur_q20 and dans_zich:
                try:
                    h_equipement = float(valeur_q20)
                    
                    # Indice 0 = au-dessus (0 pts), Indice 1 = en-dessous (10 pts)
                    idx_auto = 1 if h_equipement < hmax_zich else 0
                    
                    score_calc = float(scores[idx_auto])
                    score_total += score_calc
                    
                    texte_reponse = reponses[idx_auto]
                    texte_reco = recommandations[idx_auto] if recommandations and len(recommandations) > idx_auto else ""
                    
                    details.append(f"Automatique - Chauffage : {texte_reponse} (Equipement: {h_equipement}m vs Crue: {hmax_zich:.2f}m)")
                    
                    rappel_qr.append({
                        'question': q['question'],
                        'reponse': texte_reponse,
                        'recommandation': texte_reco
                    })
                    
                    if texte_reco and texte_reco not in recommandations_groupees[prefix]:
                        recommandations_groupees[prefix].append(texte_reco)
                except ValueError:
                    pass
            continue

        # Traitement normal pour les autres questions
        input_name = f"rep_{prefix}_{qid}"
        user_answer = request.args.get(input_name)
        
        if user_answer is not None and str(user_answer).strip() != '':
            texte_reponse = ""
            texte_reco = ""
            
            if len(reponses) == 1 and reponses[0] == 'x':
                try:
                    reponse_float = float(user_answer)
                    if prefix == 'zone' and critere == 'Niveau du plancher':
                        niveau_plancher = reponse_float
                    texte_reponse = f"{reponse_float} m"
                    details.append(f"{critere} : {reponse_float} m")
                    texte_reco = recommandations[0] if recommandations and len(recommandations) > 0 else ""
                except ValueError:
                    pass
            else:
                try:
                    index = int(user_answer)
                    texte_reponse = reponses[index]
                    score_obtenu = float(scores[index])
                    
                    score_total += score_obtenu
                    details.append(f"{critere} ({texte_reponse}) : {score_obtenu} points")
                    texte_reco = recommandations[index] if recommandations and len(recommandations) > index else ""
                except (ValueError, IndexError):
                    pass

            if texte_reponse:
                rappel_qr.append({
                    'question': q['question'],
                    'reponse': texte_reponse,
                    'recommandation': texte_reco
                })
                
                if texte_reco and texte_reco not in recommandations_groupees[prefix]:
                    recommandations_groupees[prefix].append(texte_reco)


    # Préparation de la liste finale pour le template
    recommandations_finales = []
    for pref, recos in recommandations_groupees.items():
        if recos: 
            recommandations_finales.append({
                'titre': noms_categories[pref],
                'recos': recos
            })

    # 3. Affichage des couleurs et du score
    if score_max_dynamique > 0:
        score_cent = (score_total / score_max_dynamique) * 100
    else:
        score_cent = 0.0
        
    score_cent = max(0, min(100, int(round(score_cent))))
    hue = max(0, 120 - (score_cent * 1.2))
    couleur_score = f"hsl({hue}, 100%, 40%)"
    
    geom_json = json.dumps(geom) if geom else 'null'

    return render_template('calcul.html', 
                       nom=nom_utilisateur,
                       score_total=round(score_total, 2),
                       score_cent=score_cent,
                       couleur_score=couleur_score,
                       details=details,
                       lon=lon,          
                       lat=lat,     
                       adresse=adresse_complete,   
                       dans_zich=dans_zich,
                       hmax_zich=round(hmax_zich, 2) if hmax_zich else 0, 
                       zone_choisie_texte=zone_choisie_texte,
                       geom=geom_json,
                       recommandations_finales=recommandations_finales,
                       rappel_qr=rappel_qr)


@app.route('/statistiques')
def statistiques():
    # Récupération de toutes les questions pour alimenter la liste déroulante
    questions_zone, questions_logement, questions_protection, _ = get_questions()
    
    categorie = request.args.get('categorie', 'logement')
    
    # Définir l'ID par défaut sur la première question de la catégorie choisie
    default_id = 1
    if categorie == 'logement' and questions_logement:
        default_id = questions_logement[0]['id']
    elif categorie == 'zone' and questions_zone:
        default_id = questions_zone[0]['id']
    elif categorie == 'protection' and questions_protection:
        default_id = questions_protection[0]['id']
        
    question_id = request.args.get('id', default_id, type=int)

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    if categorie == 'logement':
        table_name = "public.questions_logement"
    elif categorie == 'protection':
        table_name = "public.protection_personnes"
    else:
        table_name = "public.zone_inondable"
        
    question_texte = "Question introuvable"
    try:
        cur.execute(f"SELECT question FROM {table_name} WHERE id = %s", (question_id,))
        result = cur.fetchone()
        if result:
            question_texte = result['question']
            
        # Requête pour calculer les statistiques
        query = """
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
        cur.execute(query, (categorie, question_id))
        stats = cur.fetchall()
    except Exception as e:
        print(f"Erreur SQL: {e}")
        stats = []

    return render_template('statistiques.html', 
                           stats=stats, 
                           question_texte=question_texte, 
                           id=question_id, 
                           categorie=categorie,
                           questions_zone=questions_zone,
                           questions_logement=questions_logement,
                           questions_protection=questions_protection,
                           now=datetime.now())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')