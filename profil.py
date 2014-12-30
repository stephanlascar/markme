# -*- coding: utf-8 -*-
from bson import ObjectId
from flask import Blueprint, render_template, request, flash
from flask.ext.login import login_required, current_user
from auth import bcrypt

from database import mongo
from forms.user import UserForm


profil = Blueprint('profil', __name__)


@profil.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = UserForm(nickname=current_user.nickname, email=current_user.email)
    if request.method == 'POST' and form.validate():
        mongo.db.users.update({'_id': ObjectId(current_user.get_id())}, {'$set': {'email': form.email.data, 'nickname': form.nickname.data}})
        if form.new_password.data:
            mongo.db.users.update({'_id': ObjectId(current_user.get_id())}, {'$set': {'password': bcrypt.generate_password_hash(form.new_password.data, rounds=12)}})
        flash(u'Les modifications ont été correctement enregistrées.')

    return render_template('profil/index.html', form=form)
