from flask import Blueprint, render_template
from database import mongo

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', bookmarks=mongo.db.bookmarks.find())
