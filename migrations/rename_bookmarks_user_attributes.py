# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient


def do_it(database):
    for user in list(database.users.find({}, {'password': 0})):
        database.bookmarks.update({'user._id': user['_id']}, {'$set': {'user.email': user['email'], 'user.nickname': user['nickname']}}, multi=True)

if __name__ == '__main__':
    client = MongoClient(os.environ['MONGOLAB_URI'])
    do_it(client.get_default_database())


