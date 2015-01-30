# -*- coding: utf-8 -*-
import datetime
import urllib2

from bson import ObjectId, SON
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
import flask
from flask.ext.login import login_required, login_user, current_user
import gridfs
import pymongo
import tempfile
import subprocess

from auth import bcrypt, User
from database import mongo, add_constraint_to_criteria
from forms.bookmark import BookmarkForm
from forms.login import LoginForm


bookmarks = Blueprint('bookmarks', __name__)

@bookmarks.route('/', endpoint='index', methods=['GET', 'POST'])
@bookmarks.route('/bookmarks', endpoint='bookmarks', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    if request.method == 'POST':
        _validate_and_log_user(form)

    criteria = {'$or': [{'public': True}, {'user._id': ObjectId(current_user.get_id())}]} if current_user.is_authenticated() else {'public': True}
    bookmarks = mongo.db.bookmarks.find(criteria).sort('date', pymongo.DESCENDING)
    return render_template('bookmarks/public.html', bookmarks=bookmarks, tags=_get_top_tags(criteria), users=_get_most_active_users(), form=form)


@bookmarks.route('/user/<nickname>', methods=['GET', 'POST'])
def public_user_bookmarks(nickname):
    form = LoginForm()

    if request.method == 'POST':
        _validate_and_log_user(form)

    criteria = {'$and': [{'public': True}, {'user.nickname': nickname}]}
    bookmarks = mongo.db.bookmarks.find(criteria).sort('date', pymongo.DESCENDING)
    return render_template('bookmarks/user.html', bookmarks=bookmarks, tags=_get_top_tags(criteria), users=_get_most_active_users(), form=form, nickname=nickname)


@bookmarks.route('/my/bookmarks')
@login_required
def private_bookmarks():
    criteria = {'user._id': ObjectId(current_user.get_id())}
    bookmarks = mongo.db.bookmarks.find(criteria).sort('date', pymongo.DESCENDING)
    return render_template('bookmarks/private.html', bookmarks=bookmarks, tags=_get_top_tags(criteria), users=_get_most_active_users())


@bookmarks.route('/bookmarks/tag/<tag>', methods=['GET', 'POST'])
def bookmarks_by_tags(tag):
    form = LoginForm()

    if request.method == 'POST':
        _validate_and_log_user(form)

    criteria = add_constraint_to_criteria({'tags': tag}, {'$or': [{'public': True}, {'user._id': ObjectId(current_user.get_id())}]}) if current_user.is_authenticated() else {'public': True}
    bookmarks = mongo.db.bookmarks.find(criteria).sort('date', pymongo.DESCENDING)
    return render_template('bookmarks/public.html', bookmarks=bookmarks, tags=_get_top_tags(criteria), users=_get_most_active_users(), form=form)


@bookmarks.route('/my/tags')
@login_required
def private_tags():
    criteria = {'user._id': ObjectId(current_user.get_id())}
    tags = mongo.db.bookmarks.find(criteria).distinct('tags')
    return render_template('tags/private.html', my_tags=tags, tags=_get_top_tags(criteria), users=_get_most_active_users())


@bookmarks.route('/filter', methods=['POST'])
def search():
    search_criteria = {'$or': [{'title': {'$regex': '%s' % request.form['search'], '$options': 'i'}}, {'description': {'$regex': '%s' % request.form['search'], '$options': 'i'}}, {'tags': {'$regex': '%s' % request.form['search'], '$options': 'i'}}, {'url': {'$regex': '%s' % request.form['search'], '$options': 'i'}}]}
    criteria = add_constraint_to_criteria(search_criteria, {'$or': [{'public': True}, {'user._id': ObjectId(current_user.get_id())}]}) if current_user.is_authenticated() else {'public': True}
    bookmarks = mongo.db.bookmarks.find(criteria).sort('date', pymongo.DESCENDING)
    return render_template('bookmarks/public.html', bookmarks=bookmarks, tags=_get_top_tags(criteria), users=_get_most_active_users(), form=LoginForm())


def _validate_and_log_user(form):
    if form.validate_on_submit():
        mongo_user = mongo.db.users.find_one({'email': form.email.data})
        if mongo_user and bcrypt.check_password_hash(mongo_user['password'], form.password.data):
            login_user(User(mongo_user), remember=form.remember_me.data)
        else:
            flash('Utilisateur ou mot de passe non valide.')


def _get_most_active_users():
    return mongo.db.bookmarks.aggregate([{'$group': {'_id': {'nickname': '$user.nickname', 'email': '$user.email'}, 'count': {'$sum': 1}, 'last_bookmark': {'$last': '$published'}}}, {'$sort': SON([('count', -1), ('_id', -1)])}])['result']


def _get_top_tags(criteria):
    return mongo.db.bookmarks.aggregate([{'$match': criteria}, {'$unwind': '$tags'}, {'$group': {'_id': '$tags', 'count': {'$sum': 1}}}, {'$sort': SON([('count', -1), ('_id', -1)])}, {'$limit': 25}])['result']


@bookmarks.route('/bookmarklet')
@login_required
def bookmarklet():
    criteria = {'user._id': ObjectId(current_user.get_id()), 'url': request.args.get('url', None)}
    bookmark = mongo.db.bookmarks.find_one(criteria)
    form = BookmarkForm(title=bookmark['title'], url=bookmark['url'], description=bookmark['description'], tags=bookmark['tags'], public=bookmark['public'], referrer=bookmark['referrer']) if bookmark else BookmarkForm(request.args)
    return render_template('bookmarklet.html', form=form)


@bookmarks.route('/bookmark', methods=['POST'])
@login_required
def add_bookmark():
    form = BookmarkForm()
    if form.validate_on_submit():
        _save_bookmark(form)
        return '<script type="text/javascript">window.close();</script>'
    return render_template('bookmarklet.html', form=form)


@bookmarks.route('/bookmarks/new', methods=['GET', 'POST'])
@login_required
def new_bookmark():
    form = BookmarkForm()

    if request.method == 'POST' and form.validate_on_submit():
        _save_bookmark(form)
        flash(u'Votre bookmark est correctement enregistré.')
        return redirect(url_for('.index'))

    criteria = {'user._id': ObjectId(current_user.get_id())}
    return render_template('bookmarks/new.html', tags=_get_top_tags(criteria), users=_get_most_active_users(), form=form)


@bookmarks.route('/bookmarks/delete/<bookmark_id>')
@login_required
def delete_bookmark(bookmark_id):
    mongo.db.bookmarks.remove({'_id': ObjectId(bookmark_id), 'user._id': ObjectId(current_user.get_id())})
    return redirect(url_for('.index'))


@bookmarks.route('/bookmarks/edit/<bookmark_id>')
@login_required
def edit_bookmark(bookmark_id):
    criteria = {'user._id': ObjectId(current_user.get_id()), '_id': ObjectId(bookmark_id)}
    bookmark = mongo.db.bookmarks.find_one(criteria)
    form = BookmarkForm(title=bookmark['title'], url=bookmark['url'], description=bookmark['description'], tags=bookmark['tags'], public=bookmark['public'], referrer=bookmark['referrer']) if bookmark else BookmarkForm(request.args)

    return render_template('bookmarks/new.html', tags=_get_top_tags(criteria), users=_get_most_active_users(), form=form)


@bookmarks.route('/bookmark/screenshot/<screenshot_id>')
def get_screenshot(screenshot_id):
    _file = gridfs.GridFS(mongo.db).get(ObjectId(screenshot_id))
    response = flask.make_response(_file.read())
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content-Disposition'] = 'attachment;filename={screenshot_id}.png'.format(screenshot_id=screenshot_id)
    return response


@bookmarks.route('/bookmark/pdf/<pdf_id>')
def get_pdf(pdf_id):
    # mongo.send_file()
    _file = gridfs.GridFS(mongo.db).get(ObjectId(pdf_id))
    response = flask.make_response(_file.read())
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment;filename={pdf_id}.png'.format(pdf_id=pdf_id)
    return response


def _save_bookmark(bookmark_form):
    response = urllib2.urlopen(bookmark_form.url.data)
    html = response.read()
    response.close()

    pdf_file = gridfs.GridFS(mongo.db).put(_html_to_pdf(html), url=bookmark_form.url.data)
    png_file = gridfs.GridFS(mongo.db).put(_html_to_png(html), url=bookmark_form.url.data)

    # mongo.save_file(filename='', fileobj=_html_to_pdf(html), content_type='application/pdf')
    # mongo.save_file(filename='', fileobj=_html_to_png(html), content_type='image/png')

    mongo.db.bookmarks.update({'url': bookmark_form.url.data, 'user': {'_id': ObjectId(current_user.get_id())}},
                              {'$set': {
                                  'title': bookmark_form.title.data,
                                  'url': bookmark_form.url.data,
                                  'description': bookmark_form.description.data,
                                  'referrer': bookmark_form.referrer.data,
                                  'tags': bookmark_form.tags.data,
                                  'published': datetime.datetime.utcnow(),
                                  'public': bookmark_form.public.data,
                                  #'pdf': pdf_file,
                                  #'screenshot': png_file,
                                  'user': {
                                      '_id': ObjectId(current_user.get_id()),
                                      'nickname': current_user.nickname,
                                      'email': current_user.email
                                  }
                              }}, upsert=True)


def _html_to_pdf(html):
    html_tmp = tempfile.NamedTemporaryFile(mode='w+b', dir='scripts', suffix='.html')
    pdf_tmp = tempfile.NamedTemporaryFile(mode='r+b', suffix='.pdf')

    phantom_cmd = ['phantomjs', 'scripts/rasterize_pdf.js', '%s' % html_tmp.name, '%s' % pdf_tmp.name]

    try:
        html_tmp.write(html)
        html_tmp.flush()
        subprocess.call(phantom_cmd)  # TODO check 0
        return pdf_tmp.read()
    finally:
        html_tmp.close()
        pdf_tmp.close()


def _html_to_png(html):
    html_tmp = tempfile.NamedTemporaryFile(mode='w+b', dir='scripts', suffix='.html')
    png_tmp = tempfile.NamedTemporaryFile(mode='r+b', suffix='.png')

    phantom_cmd = ['phantomjs', 'scripts/rasterize_pdf.js', '%s' % html_tmp.name, '%s' % png_tmp.name]

    try:
        html_tmp.write(html)
        html_tmp.flush()
        subprocess.call(phantom_cmd)  # TODO check 0
        return png_tmp.read()
    finally:
        html_tmp.close()
        png_tmp.close()
