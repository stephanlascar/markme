from database import db


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024))
    title = db.Column(db.String(256))
    description = db.Column(db.Text())

    def __repr__(self):
        return '<Bookmark %r>' % self.title