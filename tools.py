# -*- coding: utf-8 -*-
from bson import ObjectId
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from database import mongo


tools = Blueprint('tools', __name__)


@tools.route('/')
@login_required
def index():
    return render_template('tools/index.html')


@tools.route('/delete_all', methods=['GET', 'POST'])
@login_required
def delete_all():
    if request.method == 'POST':
        mongo.db.bookmarks.remove({'user._id': ObjectId(current_user.get_id())})
        flash(u'Tout vos bookmarks ont été supprimés !')
        return redirect(url_for('bookmarks.index'))

    return render_template('tools/delete_all.html')

