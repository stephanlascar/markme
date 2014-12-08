import datetime
from flask import Blueprint, render_template
from database import mongo
from forms.bookmark import BookmarkForm

bookmark = Blueprint('bookmark', __name__)

@bookmark.route('/bookmark', methods=['POST'])
def create_bookmark():
    form = BookmarkForm()
    if form.validate_on_submit():
        mongo.db.bookmarks.save({'title': form.title.data,
                                'url': form.url.data,
                                'description':  form.description.data,
                                'referrer': form.referrer.data,
                                'tags': form.tags.data,
                                'date': datetime.datetime.now()})
        return render_template('bookmarket.html', form=form)
    return render_template('bookmarket.html', form=form)
