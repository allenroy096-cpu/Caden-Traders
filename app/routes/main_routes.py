from flask import render_template, Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('dashboard.html')


@main.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

