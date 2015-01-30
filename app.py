import os
from flask import Flask
from flask.ext.babel import Babel
from flask.ext.gravatar import Gravatar
from database import mongo
from auth import login_manager, bcrypt, auth
from bookmarks import bookmarks
from profil import profil
from tools import tools


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['MONGO_URI'] = os.environ['MONGOLAB_URI']
    app.secret_key = 'mon secret'
    Babel(default_locale='fr').init_app(app)
    Gravatar().init_app(app)
    mongo.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)
    app.register_blueprint(tools, url_prefix='/tools')
    app.register_blueprint(profil, url_prefix='/profil')
    return app
