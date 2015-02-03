# -*- coding: utf-8 -*-
import os
from flask.ext.testing import TestCase
from auth import bcrypt
import markme
from tests import mongo_data


class TestTools(TestCase):

    def create_app(self):
        return markme.create_app(os.environ['MONGO_UNITTEST_URI'], debug=True, testing=True)

    @mongo_data(users=[{'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}])
    def test_index(self):
        a = self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.get('/tools', follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('tools/index.html')
