from flask import Flask, render_template

# Initialisation de l'application Flask
app = Flask(__name__)

# Exemple de route (remplace un Flight::route)
@app.route('/')
def accueil():
    # render_template va chercher automatiquement "index.html" dans le dossier "templates"
    return render_template('index.html') 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')