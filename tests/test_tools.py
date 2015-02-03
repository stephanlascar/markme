# -*- coding: utf-8 -*-
import os
from bson import ObjectId
import datetime
from flask.ext.testing import TestCase
from nose.tools import assert_equal
from auth import bcrypt
from database import mongo
import markme
from tests import mongo_data


class TestTools(TestCase):

    def create_app(self):
        return markme.create_app(os.environ['MONGO_UNITTEST_URI'], debug=True, testing=True)

    @mongo_data(users=[{'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}])
    def test_index(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.get('/tools', follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('tools/index.html')

    @mongo_data(users=[{'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)},
                       {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'tony@stark.com', 'nickname': 'ironman', 'password': bcrypt.generate_password_hash('jarvis', rounds=12)}],
                bookmarks=[{'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'foo@bar.com'}, 'published': datetime.datetime.now()},
                           {'url': 'http://www.bar.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'foo@bar.com'}, 'published': datetime.datetime.now()},
                           {'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'tony@stark.com'}, 'published': datetime.datetime.now()}])
    def test_delete_all_bookmarks(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.post('/tools/delete_all', follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('bookmarks/public.html')
        assert_equal(list(mongo.db.bookmarks.find({}, {'_id': 0, 'published': 0})),
                     [{'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'tony@stark.com'}}])