import datetime
from flask import Blueprint, render_template, redirect, url_for
from database import db
from forms.bookmark import BookmarkForm
from models import Bookmark

bookmark = Blueprint('bookmark', __name__)

@bookmark.route('/bookmark', methods=['POST'])
def create_bookmark():
    form = BookmarkForm()
    if form.validate_on_submit():
        model = Bookmark()
        form.populate_obj(model)
        model.date = datetime.datetime.now()
        db.session.add(model)
        db.session.commit()
        return render_template('bookmarket.html', form=form)
    return render_template('bookmarket.html', form=form)