from flask import Blueprint, render_template

api = Blueprint('api', __name__)

@api.route('/api/bookmark', methods=['POST'])
def get_all_bookmarks():
    return render_template('index.html')