from flask import Blueprint, render_template, request
from forms.bookmark import BookmarkForm

bookmarklet = Blueprint('bookmarklet', __name__)

@bookmarklet.route('/bookmarklet')
def index():
    form = BookmarkForm(request.args)
    return render_template('bookmarket.html', form=form)