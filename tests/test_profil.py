# -*- coding: utf-8 -*-
from bson import ObjectId
import datetime
from auth import bcrypt
from database import mongo
from tests import WebAppTestCase, mongo_data


class TestProfil(WebAppTestCase):

    @mongo_data(users=[{'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}])
    def test_index(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.get('/profil', follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('profil/index.html')

    @mongo_data(users=[{'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}])
    def test_change_password(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.post('/profil/', data=dict(nickname='james', email='foo@bar.com', actual_password='password', new_password='secret', confirm_new_password='secret'))

        self.assert200(response)
        self.assertTemplateUsed('profil/index.html')
        self.assertEqual({'email': 'foo@bar.com', 'nickname': 'james'},
                         mongo.db.users.find_one({'email': 'foo@bar.com'}, {'password': 0, '_id': 0}))
        self.assertTrue(bcrypt.check_password_hash(mongo.db.users.find_one({'email': 'foo@bar.com'}, {'password': 1})['password'], 'secret'))

    @mongo_data(users=[{'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}],
                bookmarks=[{'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'james'}, 'published': datetime.datetime.now()},
                           {'url': 'http://www.bar.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'james'}, 'published': datetime.datetime.now()},
                           {'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'tony@stark.com', 'nickname': 'tony'}, 'published': datetime.datetime.now()}])
    def test_change_email(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.post('/profil/', data=dict(nickname='james', email='tony@stark.com'))

        self.assert200(response)
        self.assertTemplateUsed('profil/index.html')
        self.assertEqual({'email': 'tony@stark.com', 'nickname': 'james'},
                         mongo.db.users.find_one({'email': 'tony@stark.com'}, {'password': 0, '_id': 0}))
        self.assertTrue(bcrypt.check_password_hash(mongo.db.users.find_one({'email': 'tony@stark.com'}, {'password': 1})['password'], 'password'))
        self.assertEqual([{'url': 'http://www.bar.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'tony@stark.com', 'nickname': 'james'}},
                          {'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'tony@stark.com', 'nickname': 'james'}}],
                         list(mongo.db.bookmarks.find({'user._id': ObjectId('5495f2a88766017d44130bb6')}, {'published': 0, '_id': 0}).sort('url')))

    @mongo_data(users=[{'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}],
                bookmarks=[{'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'james'}, 'published': datetime.datetime.now()},
                           {'url': 'http://www.bar.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'james'}, 'published': datetime.datetime.now()},
                           {'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'tony@stark.com', 'nickname': 'tony'}, 'published': datetime.datetime.now()}])
    def test_change_nickname(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.post('/profil/', data=dict(nickname='tony', email='foo@bar.com'))

        self.assert200(response)
        self.assertTemplateUsed('profil/index.html')
        self.assertEqual({'email': 'foo@bar.com', 'nickname': 'tony'},
                         mongo.db.users.find_one({'email': 'foo@bar.com'}, {'password': 0, '_id': 0}))
        self.assertTrue(bcrypt.check_password_hash(mongo.db.users.find_one({'email': 'foo@bar.com'}, {'password': 1})['password'], 'password'))
        self.assertEqual([{'url': 'http://www.bar.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'tony'}},
                          {'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'tony'}}],
                         list(mongo.db.bookmarks.find({'user._id': ObjectId('5495f2a88766017d44130bb6')}, {'published': 0, '_id': 0}).sort('url')))

    @mongo_data(users=[{'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}],
                bookmarks=[{'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'james'}, 'published': datetime.datetime.now()},
                           {'url': 'http://www.bar.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'james'}, 'published': datetime.datetime.now()},
                           {'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'tony@stark.com', 'nickname': 'tony'}, 'published': datetime.datetime.now()}])
    def test_change_all_values(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.post('/profil/', data=dict(nickname='tony', email='tony@stark.com', actual_password='password', new_password='secret', confirm_new_password='secret'))

        self.assert200(response)
        self.assertTemplateUsed('profil/index.html')
        self.assertEqual({'email': 'tony@stark.com', 'nickname': 'tony'},
                         mongo.db.users.find_one({'email': 'tony@stark.com'}, {'password': 0, '_id': 0}))
        self.assertTrue(bcrypt.check_password_hash(mongo.db.users.find_one({'email': 'tony@stark.com'}, {'password': 1})['password'], 'secret'))
        self.assertEqual([{'url': 'http://www.bar.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'tony@stark.com', 'nickname': 'tony'}},
                          {'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'tony@stark.com', 'nickname': 'tony'}}],
                         list(mongo.db.bookmarks.find({'user._id': ObjectId('5495f2a88766017d44130bb6')}, {'published': 0, '_id': 0}).sort('url')))
