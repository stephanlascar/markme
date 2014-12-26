from itertools import groupby
import operator

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


@environmentfilter
def group_by_humanize_date(environment, value, attribute):
    sorted_collections = sorted(value, key=make_attrgetter(environment, attribute))
    return map(_GroupTuple, groupby(sorted_collections, _make_attr_getter_for_date(environment, attribute)))
app.jinja_env.filters['group_by_humanize_date'] = group_by_humanize_date


@app.template_filter()
def group_by_first_letter(array_of_string):
    return groupby(array_of_string, key=operator.itemgetter(0))


def _make_attr_getter_for_date(environment, attribute):
    def callback(x):
        return arrow.get(environment.getitem(x, attribute)).humanize(locale='FR_fr')

    return callback
