# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import PasswordField, StringField, ValidationError
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo
from database import mongo


class SigninForm(Form):

    email = EmailField(u'Email', validators=[DataRequired(), Email()])
    password = PasswordField(u'Mot de passe', validators=[DataRequired()])
    confirm_password = PasswordField(u'Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password', message=u'Les mots de passe doivent correspondre')])
    nickname = StringField(u'Nom d\'utilisateur', validators=[DataRequired()])

    def validate_email(self, field):
        if mongo.db.users.find_one({'email': field.data}):
            raise ValidationError(field.gettext(u'Cet email est déjà utilisé.'))

    def validate_nickname(self, field):
        if mongo.db.users.find_one({'nickname': field.data}):
            raise ValidationError(field.gettext(u'Ce nom d\'utilisateur est déjà utilisé.'))
