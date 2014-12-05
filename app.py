import os
from flask import Flask
from api import api
from database import db
from main import main


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['CLEARDB_DATABASE_URL']
    db.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(api)
    return app