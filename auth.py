import argparse
import datetime
import os
from bson import ObjectId
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager, UserMixin, login_user
from pymongo import Connection
from pymongo.uri_parser import parse_uri
from database import mongo
from forms.login import LoginForm

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = u'Merci de vous identifier.'
bcrypt = Bcrypt()
auth = Blueprint('auth', __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            mongo_user = mongo.db.users.find_one({'email': form.email.data})
            if mongo_user and bcrypt.check_password_hash(mongo_user['password'], form.password.data):
                login_user(User(mongo_user), remember=form.remember_me.data)
                return redirect(request.args.get("next") or url_for('main.index'))
            else:
                flash('Utilisateur ou mot de passe non valide.')

    return render_template('login.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return User(mongo.db.users.find_one({'_id': ObjectId(user_id)}))


class User(UserMixin):

    def __init__(self, args):
        self.id = args['_id']
        self.nickname = args['nickname']
        self.email = args['email']


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='Ajoute un nouvel utilisateur')
    arg_parser.add_argument('-e', '--email', required=True, dest="email")
    arg_parser.add_argument('-n', '--nickname', required=True, dest="nickname")
    arg_parser.add_argument('-p', '--password', required=True, dest="password")
    args = arg_parser.parse_args()

    mongo_uri = os.environ['MONGOLAB_URI']
    mongo_creds = parse_uri(mongo_uri)
    connection = Connection(mongo_creds['nodelist'][0][0], mongo_creds['nodelist'][0][1])
    db = connection[mongo_creds['database']]
    db.authenticate(mongo_creds['username'], mongo_creds['password'])

    db.users.save({'email': args.email, 'nickname': args.nickname, 'password': bcrypt.generate_password_hash(args.password, rounds=12), 'inserted': datetime.datetime.utcnow()})
