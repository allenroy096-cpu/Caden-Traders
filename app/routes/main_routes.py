from flask import render_template, Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('dashboard.html')

@main.route('/results')
def results():
    # You can fetch your bot's results from the database or a file here
    # For now, just render a placeholder template
    return render_template('results.html')
