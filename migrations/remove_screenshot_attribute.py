# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient


def do_it(database):
    database.bookmarks.update({'screenshot': {'$exists': True}}, {'$unset': {'screenshot': ''}}, multi=True)
    assert not list(database.bookmarks.find({'screenshot': {'$exists': True}}))


if __name__ == '__main__':
    client = MongoClient(os.environ['MONGOLAB_URI'])
    do_it(client.get_default_database())


