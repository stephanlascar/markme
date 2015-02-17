# -*- coding: utf-8 -*-
from database import db


class Toto(db.Document):
    email = db.StringField()
    nickname = db.StringField()


class Test(db.Document):
    title = db.StringField()
    url = db.StringField()
    description = db.StringField(required=False)
    referrer = db.StringField(required=False)
    tags = db.ListField(db.StringField('tag'), required=False)
    published = db.CreatedField()
    updated = db.ModifiedField()
    public = db.BoolField(default=False)
    user = db.DocumentField(Toto)

    # url_index = Index().ascending('url').unique()


