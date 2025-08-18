from flask import Flask
from app.routes.main_routes import main
from app.routes.results_routes import results

app = Flask(__name__)
app.register_blueprint(main)
app.register_blueprint(results)
