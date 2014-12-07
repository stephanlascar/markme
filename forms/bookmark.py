from flask_wtf import Form
from wtforms import StringField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, URL
from fields.tag_list_field import TagListField


class BookmarkForm(Form):

    title = StringField('Titre', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired(), URL()])
    description = TextAreaField('Description')
    referrer = HiddenField('Referrer')
    tags = TagListField('Tags')