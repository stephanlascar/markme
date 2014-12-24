from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo


class SigninForm(Form):

    email = EmailField(u'Email', validators=[DataRequired(), Email()])
    password = PasswordField(u'Mot de passe', validators=[DataRequired()])
    confirm_password = PasswordField(u'Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password', message=u'Les mots de passe doivent correspondre')])
    nickname = StringField(u'Nom d\'utilisateur', validators=[DataRequired()])
