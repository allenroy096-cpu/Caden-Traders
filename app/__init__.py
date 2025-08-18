from flask import Flask
from app.routes.main_routes import main

app = Flask(__name__)
app.register_blueprint(main)
