# -*- coding: utf-8 -*-
from bson import ObjectId
from flask.ext.login import current_user
from flask_wtf import Form
from wtforms import PasswordField, StringField, ValidationError
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Optional
from auth import bcrypt
from database import mongo


class UserForm(Form):

    nickname = StringField(u'Nom d\'utilisateur', validators=[DataRequired()])
    email = EmailField(u'Email', validators=[DataRequired(), Email()])
    actual_password = PasswordField(u'Mot de passe actuel')
    new_password = PasswordField(u'Nouveau mot de passe', validators=[Optional()])
    confirm_new_password = PasswordField(u'Confirmer le nouveau mot de passe', validators=[EqualTo('new_password', message=u'Les mots de passe doivent correspondre')])

    def validate_email(self, field):
        if mongo.db.users.find_one({'$and': [{'email': field.data}, {'_id': {'$ne': ObjectId(current_user.get_id())}}]}):
            raise ValidationError(field.gettext(u'Cet email est déjà utilisé.'))

    def validate_nickname(self, field):
        if mongo.db.users.find_one({'$and': [{'nickname': field.data}, {'_id': {'$ne': ObjectId(current_user.get_id())}}]}):
            raise ValidationError(field.gettext(u'Ce nom d\'utilisateur est déjà utilisé.'))

    def validate_actual_password(self, field):
        if self.new_password.data and not field.data:
            raise ValidationError(field.gettext(u'Ce champs est requis.'))

        if field.data:
            user = mongo.db.users.find_one({'_id': ObjectId(current_user.get_id())})
            if not bcrypt.check_password_hash(user['password'], field.data):
                raise ValidationError(field.gettext(u'Le mot de passe n\'est pas correct.'))
