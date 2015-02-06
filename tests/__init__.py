# -*- coding: utf-8 -*-
from functools import update_wrapper
import os
from flask.ext.testing import TestCase
from database import mongo
import markme


class WebAppTestCase(TestCase):

    def create_app(self):
        return markme.create_app(os.environ['MONGO_UNITTEST_URI'], debug=True, testing=True)

    def assert_flashes(self, expected_message, expected_category='message'):
        with self.client.session_transaction() as session:
            try:
                category, message = session['_flashes'][0]
            except KeyError:
                raise AssertionError('nothing flashed')
            assert expected_message in message
            assert expected_category == category


def mongo_data(**collections):
    def decorator(decorated):
        def wrapper(self):
            for collection, data in collections.items():
                mongo.db[collection].remove()
                mongo.db[collection].insert(data)
            decorated(self)
        return update_wrapper(wrapper, decorated)
    return decorator
