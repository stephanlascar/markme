import datetime
from bson import ObjectId, SON

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.login import login_required, login_user, logout_user, current_user
import pymongo
from auth import bcrypt, User

from database import mongo
from forms.bookmark import BookmarkForm
from forms.login import LoginForm


main = Blueprint('main', __name__)

@main.route('/', endpoint='index', methods=['GET', 'POST'])
@main.route('/bookmarks', endpoint='bookmarks', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            mongo_user = mongo.db.users.find_one({'email': form.email.data})
            if mongo_user and bcrypt.check_password_hash(mongo_user['password'], form.password.data):
                login_user(User(mongo_user), remember=form.remember_me.data)
            else:
                flash('Utilisateur ou mot de passe non valide.')

    criteria = {'$or': [{'public': True}, {'user._id': ObjectId(current_user.get_id())}]} if current_user.is_authenticated() else {'public': True}
    bookmarks = mongo.db.bookmarks.find(criteria).sort('date', pymongo.DESCENDING)
    tags = mongo.db.bookmarks.aggregate([{'$match': criteria}, {'$unwind': '$tags'}, {'$group': {'_id': '$tags', 'count': {'$sum': 1}}}, {'$sort': SON([('count', -1), ('_id', -1)])}, {'$limit': 25}])
    users = mongo.db.bookmarks.aggregate([{"$group": {"_id": {"nickname": "$user.nickname", "email": "$user.email"}, "count": {"$sum": 1}}}, {"$sort": SON([("count", -1), ("_id", -1)])}])
    return render_template('index.html', bookmarks=bookmarks, tags=tags['result'], users=users['result'], form=form)


@main.route('/tag/<tag>', methods=['GET', 'POST'])
def bookmarks_by_tags(tag):
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            mongo_user = mongo.db.users.find_one({'email': form.email.data})
            if mongo_user and bcrypt.check_password_hash(mongo_user['password'], form.password.data):
                login_user(User(mongo_user), remember=form.remember_me.data)
            else:
                flash('Utilisateur ou mot de passe non valide.')

    criteria = {'$and': [{'tags': tag}, {'$or': [{'public': True}, {'user._id': ObjectId(current_user.get_id())}]}]} if current_user.is_authenticated() else {'$and': [{'tags': tag}, {'public': True}]}
    bookmarks = mongo.db.bookmarks.find(criteria).sort('date', pymongo.DESCENDING)
    tags = mongo.db.bookmarks.aggregate([{'$match': criteria}, {'$unwind': '$tags'}, {'$group': {'_id': '$tags', 'count': {'$sum': 1}}}, {'$sort': SON([('count', -1), ('_id', -1)])}, {'$limit': 25}])
    users = mongo.db.bookmarks.aggregate([{"$group": {"_id": {"nickname": "$user.nickname", "email": "$user.email"}, "count": {"$sum": 1}}}, {"$sort": SON([("count", -1), ("_id", -1)])}])
    return render_template('index.html', bookmarks=bookmarks, tags=tags['result'], users=users['result'], form=form)


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
                                 'public': form.public.data,
                                 'user': {
                                     '_id': ObjectId(current_user.get_id()),
                                     'nickname': current_user.nickname,
                                     'email': current_user.email
                                 }})
        return '<script type="text/javascript">window.close();</script>'
    return render_template('bookmarklet.html', form=form)
