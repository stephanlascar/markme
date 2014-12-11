import arrow
import pymongo
from app import create_app
from database import mongo

app = create_app()

@app.before_first_request
def create_mongo_index():
    mongo.db.bookmarks.ensure_index('date', pymongo.DESCENDING, background=True)
    mongo.db.bookmarks.ensure_index('title', pymongo.ASCENDING, background=True)
    mongo.db.bookmarks.ensure_index('description', background=True)
    mongo.db.bookmarks.ensure_index('tags', pymongo.ASCENDING, background=True)


@app.template_filter()
def humanize(datetime):
    return arrow.Arrow.fromdatetime(datetime).humanize(locale='FR_fr')
