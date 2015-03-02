# -*- coding: utf-8 -*-
from itertools import groupby
import operator
import os

import arrow
from jinja2 import environmentfilter
from jinja2.filters import make_attrgetter, _GroupTuple
import pymongo
from flask import Flask
from flask.ext.babel import Babel
from flask.ext.gravatar import Gravatar

from auth import login_manager, bcrypt, auth
from bookmarks import bookmarks
from profil import profil
from tools import tools
from database import mongo, db


def create_app(mongo_uri, debug=False, testing=False):
    app = Flask(__name__)
    app.config['DEBUG'] = debug
    app.config['TESTING'] = testing
    app.config['WTF_CSRF_ENABLED'] = not testing
    app.config['MONGO_URI'] = mongo_uri
    app.secret_key = os.environ.get('SECRET_KEY', 'clef pour les tests')
    Babel(default_locale='fr').init_app(app)
    Gravatar().init_app(app)
    mongo.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)
    app.register_blueprint(tools, url_prefix='/tools')
    app.register_blueprint(profil, url_prefix='/profil')

    @app.before_first_request
    def create_mongo_index():
        mongo.db.bookmarks.ensure_index('published', pymongo.DESCENDING, background=True)
        mongo.db.bookmarks.ensure_index('user._id', pymongo.DESCENDING, background=True)
        mongo.db.bookmarks.ensure_index('title', pymongo.ASCENDING, background=True)
        mongo.db.bookmarks.ensure_index('description', background=True)
        mongo.db.bookmarks.ensure_index('tags', pymongo.ASCENDING, background=True)
        mongo.db.bookmarks.ensure_index([('user._id', pymongo.ASCENDING), ('url', pymongo.ASCENDING)], background=True, unique=True)

        mongo.db.users.ensure_index('email', pymongo.ASCENDING, background=True, unique=True)
        mongo.db.users.ensure_index('nickname', pymongo.ASCENDING, background=True, unique=True)

        # test = Test(title='testo erchuorecuh', url='htteuoep://', tags=['oeu', ',euoue'], user=Toto(email='aaa@'))
        # test.save()


    @environmentfilter
    def group_by_humanize_date(environment, value, attribute):
        sorted_collections = sorted(value, key=make_attrgetter(environment, attribute))
        return map(_GroupTuple, groupby(sorted_collections, _make_attr_getter_for_date(environment, attribute)))
    app.jinja_env.filters['group_by_humanize_date'] = group_by_humanize_date

    @app.template_filter()
    def group_by_first_letter(array_of_string):
        return groupby(array_of_string, key=operator.itemgetter(0))

    def _make_attr_getter_for_date(environment, attribute):
        def callback(x):
            return arrow.get(environment.getitem(x, attribute)).humanize(locale='FR_fr')

        return callback

    return app
