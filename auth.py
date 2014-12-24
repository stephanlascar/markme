import argparse
import datetime
import os
from bson import ObjectId
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager, UserMixin, login_user, login_required, logout_user
from pymongo import Connection
from pymongo.uri_parser import parse_uri
from database import mongo
from forms.login import LoginForm
from forms.signin import SigninForm

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
                return redirect(request.args.get("next") or url_for('bookmarks.index'))
            else:
                flash('Utilisateur ou mot de passe non valide.')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('bookmarks.index'))


@auth.route('/signin', methods=['GET', 'POST'])
def sign_in():
    form = SigninForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            mongo.db.users.save({'email': form.email.data, 'nickname': form.nickname.data, 'password': bcrypt.generate_password_hash(form.password.data, rounds=12), 'inserted': datetime.datetime.utcnow()})
            flash('Vous pouvez maintenant vous connecter.')
            return redirect(url_for('bookmarks.index'))

    return render_template('auth/signin.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return User(mongo.db.users.find_one({'_id': ObjectId(user_id)}))


class User(UserMixin):

    def __init__(self, args):
        self.id = args['_id']
        self.nickname = args['nickname']
        self.email = args['email']
