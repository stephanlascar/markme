import datetime

from flask import Blueprint, render_template, request
import pymongo

from database import mongo
from forms.bookmark import BookmarkForm


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', bookmarks=mongo.db.bookmarks.find().sort('date', pymongo.DESCENDING))


@main.route('/bookmarklet')
def bookmarklet():
    return render_template('bookmarklet.html', form=BookmarkForm(request.args))


@main.route('/bookmark', methods=['POST'])
def add_bookmark():
    form = BookmarkForm()
    if form.validate_on_submit():
        mongo.db.bookmarks.save({'title': form.title.data,
                                 'url': form.url.data,
                                 'description': form.description.data,
                                 'referrer': form.referrer.data,
                                 'tags': form.tags.data,
                                 'date': datetime.datetime.utcnow()})
        return '<script type="text/javascript">window.close();</script>'
    return render_template('bookmarklet.html', form=form)
