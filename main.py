from flask import Blueprint, render_template
from models.bookmark import Bookmark

main = Blueprint('main', __name__)

@main.route('/')
def hello():
    bookmarks = Bookmark.query.all()
    return render_template('index.html', bookmarks=bookmarks)