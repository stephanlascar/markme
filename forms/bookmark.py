from flask_wtf import Form
from wtforms import StringField, TextAreaField, HiddenField, BooleanField
from wtforms.validators import DataRequired, URL, Length, Optional
from fields.tag_list_field import TagListField


class BookmarkForm(Form):

    title = StringField('Titre', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired(), URL()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=700)])
    referrer = HiddenField('Referrer')
    public = BooleanField('Public')
    tags = TagListField('Tags')
