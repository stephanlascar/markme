from flask import Blueprint, render_template
from models import Bookmark

main = Blueprint('main', __name__)

@main.route('/')
def index():
    bookmarks = Bookmark.query.all()
    return render_template('index.html', bookmarks=bookmarks)