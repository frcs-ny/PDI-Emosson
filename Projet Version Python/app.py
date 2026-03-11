from flask import Flask, render_template, request
from datetime import datetime
import psycopg2
import psycopg2.extras
import os

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

    return questions_zone, questions_logement


# routes flask

@app.route('/')
@app.route('/accueil')
def accueil():
    return render_template('accueil.html', now=datetime.now())


@app.route('/questionnaire')
def questionnaire():
    questions_zone, questions_logement = get_questions()

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

'''
@app.route('/calcul')
def calcul():
    questions_zone, questions_logement = get_questions()
    return render_template('calcul.html',
                           questions_zone_db=questions_zone,
                           questions_logement_db=questions_logement,
                           now=datetime.now())
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')