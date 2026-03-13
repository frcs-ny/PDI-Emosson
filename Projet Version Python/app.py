from flask import Flask, render_template, request
from datetime import datetime
import psycopg2
import psycopg2.extras
import os
from api_georisques import recuperer_coordonnees, est_dans_une_zone_inondable

app = Flask(
    __name__,
    template_folder='front_end/templates',
    static_folder='front_end/static'
)

# connextion à la BDD
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))

# requetes SQL
def get_questions():
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT id, critere, question, reponses, scores_vulnerabilite FROM public.zone_inondable ORDER BY id")
    questions_zone = [dict(row) for row in cur.fetchall()]
    for q in questions_zone:
        q['prefix'] = 'zone'

    cur.execute("SELECT id, critere, question, reponses, scores_vulnerabilite FROM public.questions_logement ORDER BY id")
    questions_logement = [dict(row) for row in cur.fetchall()]
    for q in questions_logement:
        q['prefix'] = 'logement'

    # Calcul dynamique du score maximum théorique
    score_max_theorique = 0.0
    all_questions = questions_zone + questions_logement
    for q in all_questions:
        scores = q.get('scores_vulnerabilite')
        if scores:
            try:
                # On filtre les éventuelles valeurs nulles et on convertit en float
                valid_scores = [float(s) for s in scores if s is not None]
                if valid_scores:
                    score_max_theorique += max(valid_scores)
            except (ValueError, TypeError):
                pass # Ignore si la conversion échoue

    return questions_zone, questions_logement, score_max_theorique


# routes flask

@app.route('/')
@app.route('/accueil')
def accueil():
    return render_template('accueil.html', now=datetime.now())


@app.route('/questionnaire')
def questionnaire():
    questions_zone, questions_logement, _ = get_questions()

    etapes = [
        {'critere': 'Informations générales', 'question': 'Numéro et libellé de la voie :',  'type': 'text', 'name': 'adresse',     'placeholder': 'Ex: 10 Rue de la République', 'pattern': None},
        {'critere': 'Informations générales', 'question': 'Code postal :',                   'type': 'text', 'name': 'code_postal', 'placeholder': 'Ex: 37000',                   'pattern': '[0-9]{5}'},
        {'critere': 'Informations générales', 'question': 'Ville :',                         'type': 'text', 'name': 'ville',       'placeholder': 'Ex: Tours',                   'pattern': None},
        ]

    questions = questions_zone + questions_logement
    for q in questions:
        if q['critere'] == "Hauteur d'eau potentielle":
            continue

        reponses = q['reponses']  
        input_name = f"rep_{q['prefix']}_{q['id']}"

        if len(reponses) == 1 and reponses[0] == 'x':
            etapes.append({
                'critere': q['critere'], 
                'question': q['question'],
                'type': 'number', 
                'name': input_name,
                'placeholder': 'Ex: 0.50 m'
            })
        else:
            etapes.append({
                'critere': q['critere'], 
                'question': q['question'],
                'type': 'select', 
                'name': input_name,
                'options': list(enumerate(reponses))
            })

    return render_template('questionnaire.html', etapes=etapes, now=datetime.now())

@app.route('/calcul')
def calcul():
    questions_zone, questions_logement, score_max_theorique = get_questions()
    
    score_total = 0.0
    details = []
    niveau_plancher = 0.0
    zone_choisie_texte = ''
    
    # --- Appel API Géorisques automatique ---
    adresse_brute = request.args.get('adresse', '')
    cp_brut = request.args.get('code_postal', '')
    ville_brute = request.args.get('ville', '')
    
    adresse_complete = f"{adresse_brute} {cp_brut} {ville_brute}".strip()
    
    if adresse_complete:
        coords = recuperer_coordonnees(adresse_complete)
        if coords:
            vulnerability = est_dans_une_zone_inondable(coords['lat'], coords['lon'])
            if vulnerability['found']:
                risques_str = ", ".join(vulnerability['risques'])
                details.append(f"ℹ️ Analyse Géorisques : Zone à risque détectée ({risques_str})")
            else:
                details.append("ℹ️ Analyse Géorisques : Aucun risque majeur (TRI) détecté à cette adresse.")
    
    # --- Calcul du score ---
    all_questions_db = questions_zone + questions_logement
    
    for q in all_questions_db:
        qid = q['id']
        prefix = q['prefix']
        critere = q['critere']
        
        reponses = q['reponses']
        scores = q['scores_vulnerabilite']
        
        input_name = f"rep_{prefix}_{qid}"
        user_answer = request.args.get(input_name)
        
        if user_answer is not None:
            # Cas A : C'est le niveau du plancher ("x")
            if len(reponses) == 1 and reponses[0] == 'x':
                try:
                    niveau_plancher = float(user_answer)
                    details.append(f"{critere} : {niveau_plancher} m")
                except ValueError:
                    pass
            
            # Cas B : Liste déroulante
            else:
                try:
                    index = int(user_answer)
                    texte_reponse = reponses[index]
                    score_obtenu = float(scores[index])
                    
                    score_total += score_obtenu
                    details.append(f"{critere} ({texte_reponse}) : {score_obtenu} points")
                    
                    if critere == 'Zone inondable':
                        zone_choisie_texte = texte_reponse
                except (ValueError, IndexError):
                    pass
        
        # --- Traitement du "Calcul H" ---
        if critere == "Hauteur d'eau potentielle" and zone_choisie_texte != '':
            hauteurs_reference = {
                "Zone de dissipation de l'énergie (ZDE)": 1.5,
                "Ecoulement préférentiel (EP)": 1.2,
                "Modéré (M)": 0.5,
                "Fort (F)": 1.0,
                "Très fort (TF)": 2.0
            }
            
            niveau_inondation = hauteurs_reference.get(zone_choisie_texte, 0)
            H = niveau_inondation - niveau_plancher
            
            idx_regle = -1
            if H >= 0.2 and 'h >= 0.2' in reponses:
                idx_regle = reponses.index('h >= 0.2')
            elif H < 0.2 and 'h <= 0.2' in reponses:
                idx_regle = reponses.index('h <= 0.2')
                
            if idx_regle != -1:
                score_calc = float(scores[idx_regle])
                score_total += score_calc
                details.append(f"Hauteur d'eau H ({H:.2f} m) : {score_calc} points")

    # --- Transformation du score en pourcentage et calcul de la couleur ---
    if score_max_theorique > 0:
        score_cent = (score_total / score_max_theorique) * 100
    else:
        score_cent = 0.0
        
    # On borne la valeur entre 0 et 100
    score_cent = max(0, min(100, int(round(score_cent))))
    
    # Calcul de la couleur HSL : de Vert (120) pour 0% vers Rouge (0) pour 100%
    hue = max(0, 120 - (score_cent * 1.2))
    couleur_score = f"hsl({hue}, 70%, 45%)"

    return render_template('calcul.html', 
                           score_total=round(score_total, 2),
                           score_cent=score_cent,
                           couleur_score=couleur_score,
                           details=details)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')