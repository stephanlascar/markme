from flask import Flask
from flask.ext.babel import Babel
from bookmark import bookmark
from bookmarklet import bookmarklet
from database import mongo
from main import main


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost/markme'
    app.secret_key = 'mon secret'
    Babel(default_locale='fr').init_app(app)
    mongo.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(bookmark)
    app.register_blueprint(bookmarklet)
    return app
