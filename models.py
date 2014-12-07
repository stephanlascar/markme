from database import db


tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                db.Column('page_id', db.Integer, db.ForeignKey('bookmark.id')))


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text())
    referrer = db.Column(db.String(1024))
    date = db.Column(db.DateTime(), nullable=False)
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('bookmarks', lazy='dynamic'))

    def __repr__(self):
        return 'Bookmark %r' % self.title


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return 'Tag %r' % self.value