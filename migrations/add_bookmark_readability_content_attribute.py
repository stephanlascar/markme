# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient


def do_it(database, parser_client):
    for bookmark in list(database.bookmarks.find({}, {'_id': 1, 'url': 1})):
        response = parser_client.get_article_content(bookmark['url'])
        database.bookmarks.update({'_id': bookmark['_id']}, {'$set': {'content': response.content['content']}}, multi=True)

if __name__ == '__main__':
    client = MongoClient(os.environ['MONGOLAB_URI'])
    do_it(client.get_default_database())


