# -*- coding: utf-8 -*-
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
