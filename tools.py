import datetime

from bson import ObjectId, SON
from flask import Blueprint, render_template, request, flash, current_app
from flask.ext.login import login_required, login_user, current_user
import pymongo

from auth import bcrypt, User
from database import mongo, add_constraint_to_criteria
from forms.bookmark import BookmarkForm
from forms.login import LoginForm


tools = Blueprint('tools', __name__)


@tools.route('/')
@login_required
def index():
    return render_template('tools/index.html')
