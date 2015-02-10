# -*- coding: utf-8 -*-
import datetime
from StringIO import StringIO
from io import BytesIO
from zipfile import ZipFile
from bson import ObjectId
import feedparser
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask.ext.login import login_required, current_user
from werkzeug.contrib.atom import AtomFeed
from database import mongo
from forms.imports import ImportForm


tools = Blueprint('tools', __name__)


@tools.route('/')
@login_required
def index():
    return render_template('tools/index.html')


@tools.route('/delete_all', methods=['GET', 'POST'])
@login_required
def delete_all_bookmarks():
    if request.method == 'POST':
        mongo.db.bookmarks.remove({'user._id': ObjectId(current_user.get_id())})
        flash(u'Tout vos bookmarks ont été supprimés !')
        return redirect(url_for('bookmarks.index'))

    return render_template('tools/delete_all.html')


@tools.route('/export')
@login_required
def export_bookmarks():
    return render_template('tools/export.html')


@tools.route('/download_atom')
@login_required
def download_atom():
    feed = AtomFeed(title='Mes bookmarks',
                    feed_url='xxx',
                    url='http://www.markme.com')

    for bookmark in mongo.db.bookmarks.find({'user._id': ObjectId(current_user.get_id())}):
        feed.add(id=bookmark['_id'], title=bookmark['title'], content=bookmark['description'],
                 content_type='text', updated=bookmark['published'],
                 links=[dict(href=bookmark['url']), dict(via=bookmark['referrer'])],
                 categories=[dict(term=tag, label=tag) for tag in bookmark['tags']],
                 author=dict(name=current_user.nickname, nickname=current_user.nickname, email=current_user.email))

    return send_file(StringIO(feed.to_string().encode('utf-8')), attachment_filename='bookmarks.xml', as_attachment=True, mimetype='application/atom+xml')


@tools.route('/import', methods=['GET', 'POST'])
@login_required
def import_bookmarks():
    form = ImportForm()

    if request.method == 'POST' and form.validate_on_submit():
        feed = feedparser.parse(form.atom_file.data.read())
        for mark in feed.entries:
            published = datetime.datetime.strptime(mark.published, "%Y-%m-%dT%H:%M:%SZ")
            referrers = filter(lambda link: 'via' == link['rel'], mark['links']) or [{'href': ''}]

            mongo.db.bookmarks.update({'url': mark.link, 'user._id': ObjectId(current_user.get_id())},
                                      {'$set': {
                                          'user': {
                                              '_id': ObjectId(current_user.get_id()),
                                              'nickname': current_user.nickname,
                                              'email': current_user.email
                                          },
                                          'published': published,
                                          'title': mark.title,
                                          'url': mark.link,
                                          'description': mark.get('summary', ''),
                                          'referrer': referrers[0]['href'],
                                          'public': not mark.get('bm_isprivate', False),
                                          'tags': [tag.label for tag in mark.get('tags', [])]
                                      }}, upsert=True)
        flash(u'Fichier importé avec succès !')

    return render_template('tools/import.html', form=form)
