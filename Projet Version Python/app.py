from flask import Flask, render_template, request
from datetime import datetime
import psycopg2
import psycopg2.extras
import os
import json

from api_georisques import recuperer_coordonnees, est_dans_une_zone_inondable
from estdansunezich import adresse_vers_coordonnees, recuperer_info_toutes_les_station, trouver_station_plus_proche, recuperer_geom_zich, est_dans_une_zich

app = Flask(
    __name__,
    template_folder='front_end/templates',
    static_folder='front_end/static'
)

# connexion à la BDD
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))

# requetes SQL
def get_questions():
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT id, critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee FROM public.zone_inondable ORDER BY id")
    questions_zone = [dict(row) for row in cur.fetchall()]
    for q in questions_zone:
        q['prefix'] = 'zone'

    cur.execute("SELECT id, critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee FROM public.questions_logement ORDER BY id")
    questions_logement = [dict(row) for row in cur.fetchall()]
    for q in questions_logement:
        q['prefix'] = 'logement'

    score_max_theorique = 0.0
    all_questions = questions_zone + questions_logement
    for q in all_questions:
        scores = q.get('scores_vulnerabilite')
        if scores:
            try:
                valid_scores = [float(s) for s in scores if s is not None]
                if valid_scores:
                    score_max_theorique += max(valid_scores)
            except (ValueError, TypeError):
                pass 

    return questions_zone, questions_logement, score_max_theorique


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
    questions_zone, questions_logement, _ = get_questions()

    etapes = [
        {'critere': 'Informations générales', 'question': 'Numéro et libellé de la voie :',  'type': 'text', 'name': 'adresse',     'placeholder': 'Ex: 10 Rue de la République', 'pattern': None, 'a_dependance': False},
        {'critere': 'Informations générales', 'question': 'Code postal :',                   'type': 'text', 'name': 'code_postal', 'placeholder': 'Ex: 37000',                   'pattern': '[0-9]{5}', 'a_dependance': False},
        {'critere': 'Informations générales', 'question': 'Ville :',                         'type': 'text', 'name': 'ville',       'placeholder': 'Ex: Tours',                   'pattern': None, 'a_dependance': False},
    ]

    questions = questions_zone + questions_logement
    for q in questions:
        # --- NOUVEAU : On cache la question Zone inondable et Hauteur d'eau ---
        if q['critere'] in ["Hauteur d'eau potentielle", "Zone inondable"]:
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
    questions_zone, questions_logement, _ = get_questions()
    all_questions_db = questions_zone + questions_logement
    
    details = []
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

    # --- NOUVEAU : Récupération des données GPS et ZICH ---
    if adresse_complete:
        try:
            # 1. Obtenir les coordonnées GPS
            result_coords = adresse_vers_coordonnees(adresse_complete)
            lon = result_coords['lon']
            lat = result_coords['lat']
            
            # Appel API Géorisques classique (gardé à titre d'info)
            vulnerability = est_dans_une_zone_inondable(lat, lon)
            if vulnerability and vulnerability['found']:
                details.append(f"ℹ️ Géorisques : Risque détecté ({', '.join(vulnerability['risques'])})")
            
            # 2. Chercher les données de submersion ZICH
            stations = recuperer_info_toutes_les_station()
            code_station, nom_station = trouver_station_plus_proche(stations, lon, lat)
            hauteur_max_station, geom = recuperer_geom_zich(code_station)
            dans_zich, hmin_zich, hmax_zich, geom = est_dans_une_zich(code_station, lon, lat, hauteur_max_station, geom)
            
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


    # 1. Récupération des réponses saisies
    user_answers_text = {}
    for q in all_questions_db:
        input_name = f"rep_{q['prefix']}_{q['id']}"
        user_answer = request.args.get(input_name)
        
        if user_answer is not None and str(user_answer).strip() != '':
            if len(q['reponses']) == 1 and q['reponses'][0] == 'x':
                user_answers_text[(q['prefix'], q['id'])] = user_answer
            else:
                try:
                    index = int(user_answer)
                    user_answers_text[(q['prefix'], q['id'])] = q['reponses'][index]
                except (ValueError, IndexError):
                    pass

    # 2. Calcul du score
    score_total = 0.0
    score_max_dynamique = 0.0
    
    for q in all_questions_db:
        qid = q['id']
        prefix = q['prefix']
        critere = q['critere']
        reponses = q['reponses']
        scores = q['scores_vulnerabilite']
        
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
            
        # --- NOUVEAU : Traitement automatisé de la Zone Inondable ---
        if critere == 'Zone inondable':
            if dans_zich and zone_choisie_texte != '':
                idx = -1
                for i, r in enumerate(reponses):
                    if zone_choisie_texte in r: # Cherche "Modéré" dans "Modéré (M)" par exemple
                        idx = i
                        break
                
                if idx != -1:
                    score_obtenu = float(scores[idx])
                    score_total += score_obtenu
                    details.append(f"Automatique - {critere} ({reponses[idx]}) : {score_obtenu} points")
            continue 

        # --- NOUVEAU : Traitement automatisé de la Hauteur d'eau ---
        if critere == "Hauteur d'eau potentielle":
            if dans_zich:
                # Calcul de H (eau dans le logement) = Hauteur max de la zone - surélévation du plancher
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


        # Traitement normal pour les autres questions
        input_name = f"rep_{prefix}_{qid}"
        user_answer = request.args.get(input_name)
        
        if user_answer is not None:
            if len(reponses) == 1 and reponses[0] == 'x':
                try:
                    niveau_plancher = float(user_answer)
                    details.append(f"{critere} : {niveau_plancher} m")
                except ValueError:
                    pass
            else:
                try:
                    index = int(user_answer)
                    texte_reponse = reponses[index]
                    score_obtenu = float(scores[index])
                    
                    score_total += score_obtenu
                    details.append(f"{critere} ({texte_reponse}) : {score_obtenu} points")
                except (ValueError, IndexError):
                    pass

    # 3. Affichage des couleurs et du score
    if score_max_dynamique > 0:
        score_cent = (score_total / score_max_dynamique) * 100
    else:
        score_cent = 0.0
        
    score_cent = max(0, min(100, int(round(score_cent))))
    hue = max(0, 120 - (score_cent * 1.2))
    couleur_score = f"hsl({hue}, 70%, 45%)"
    
    geom_json = json.dumps(geom) if geom else 'null'

    return render_template('calcul.html', 
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
                       geom=geom_json)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')