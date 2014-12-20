import datetime
from bson import ObjectId

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.login import login_required, login_user, logout_user, current_user
import pymongo
from auth import bcrypt, User

from database import mongo
from forms.bookmark import BookmarkForm
from forms.login import LoginForm


main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            mongo_user = mongo.db.users.find_one({'email': form.email.data})
            if mongo_user and bcrypt.check_password_hash(mongo_user['password'], form.password.data):
                login_user(User(mongo_user), remember=form.remember_me.data)
            else:
                flash('Utilisateur ou mot de passe non valide.')

    return render_template('index.html', bookmarks=mongo.db.bookmarks.find().sort('date', pymongo.DESCENDING), form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/bookmarklet')
@login_required
def bookmarklet():
    return render_template('bookmarklet.html', form=BookmarkForm(request.args))


@main.route('/bookmark', methods=['POST'])
@login_required
def add_bookmark():
    form = BookmarkForm()
    if form.validate_on_submit():
        mongo.db.bookmarks.save({'title': form.title.data,
                                 'url': form.url.data,
                                 'description': form.description.data,
                                 'referrer': form.referrer.data,
                                 'tags': form.tags.data,
                                 'published': datetime.datetime.utcnow(),
                                 'public': True,
                                 'user': {
                                     '_id': ObjectId(current_user.get_id()),
                                     'email': current_user.email
                                 }})
        return '<script type="text/javascript">window.close();</script>'
    return render_template('bookmarklet.html', form=form)
