from itertools import groupby
import arrow
from jinja2 import environmentfilter
from jinja2.filters import make_attrgetter, _GroupTuple
import pymongo
from app import create_app
from database import mongo

app = create_app()

@app.before_first_request
def create_mongo_index():
    mongo.db.bookmarks.ensure_index('published', pymongo.DESCENDING, background=True)
    mongo.db.bookmarks.ensure_index('user._id', pymongo.DESCENDING, background=True)
    mongo.db.bookmarks.ensure_index('title', pymongo.ASCENDING, background=True)
    mongo.db.bookmarks.ensure_index('description', background=True)
    mongo.db.bookmarks.ensure_index('tags', pymongo.ASCENDING, background=True)
    mongo.db.users.ensure_index('email', pymongo.ASCENDING, background=True, unique=True)
    mongo.db.users.ensure_index('nickname', pymongo.ASCENDING, background=True, unique=True)


@app.template_filter()
def humanize(datetime):
    return arrow.get(datetime, 'YYYY-MM-DDTHH:00:00').humanize(locale='FR_fr')


@environmentfilter
def group_by_date(environment, value, attribute, date_format):
    sorted_collections = sorted(value, key=make_attrgetter(environment, attribute))
    return map(_GroupTuple, groupby(sorted_collections, _make_attr_getter_for_date(environment, attribute, date_format)))
app.jinja_env.filters['group_by_date'] = group_by_date


def _make_attr_getter_for_date(environment, attribute, date_format):
    def callback(x):
        return environment.getitem(x, attribute).strftime(date_format)

    return callback
