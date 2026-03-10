from flask import Flask, render_template
from datetime import datetime

app = Flask(
    __name__,
    template_folder='front_end/templates',
    static_folder='front_end/static'
)

@app.route('/')
@app.route('/accueil')
def accueil():
    return render_template('accueil.html', now=datetime.now())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')