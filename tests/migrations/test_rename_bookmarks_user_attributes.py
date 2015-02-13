# -*- coding: utf-8 -*-
from unittest import TestCase
from bson import ObjectId
import mongomock
from migrations import rename_bookmarks_user_attributes


class TestRenameBookmarksUserAttributes(TestCase):

    def setUp(self):
        self.database = mongomock.Connection().db

    def test_rename_bookmarks_user_attributes(self):
        self.database.users.insert([
            {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'foo@bar.com', 'nickname': 'james'},
            {'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'tony@stark.com', 'nickname': 'tony'}
        ])

        self.database.bookmarks.insert([
            {
                'url': 'http://www.google.fr',
                'user': {
                    '_id': ObjectId('5495f2a88766017d44130bb6'),
                    'email': 'other@test.com',
                    'nickname': 'other test'
                }
            }, {
                'url': 'http://www.yahoo.fr',
                'user': {
                    '_id': ObjectId('5495f2a88766017d44130bb6'),
                    'email': 'test@ok.com',
                    'nickname': 'test'
                }
            }, {
                'url': 'http://www.aol.fr',
                'user': {
                    '_id': ObjectId('5495f2a88766017d44130bb1'),
                    'email': 'bruce@wayne.com',
                    'nickname': 'batman'
                }
            }
        ])
        rename_bookmarks_user_attributes.do_it(self.database)

        self.assertEqual([
            {
                'url': 'http://www.aol.fr',
                'user': {
                    '_id': ObjectId('5495f2a88766017d44130bb1'),
                    'email': 'tony@stark.com',
                    'nickname': 'tony'
                }
            }, {
                'url': 'http://www.google.fr',
                'user': {
                    '_id': ObjectId('5495f2a88766017d44130bb6'),
                    'email': 'foo@bar.com',
                    'nickname': 'james'
                }
            }, {
                'url': 'http://www.yahoo.fr',
                'user': {
                    '_id': ObjectId('5495f2a88766017d44130bb6'),
                    'email': 'foo@bar.com',
                    'nickname': 'james'
                }
            }], list(self.database.bookmarks.find({}, {'_id': 0}).sort([('url', 1)])))
