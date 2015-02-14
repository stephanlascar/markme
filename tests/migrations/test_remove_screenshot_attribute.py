# -*- coding: utf-8 -*-
from unittest import TestCase
import mongomock
from migrations import remove_bookmark_screenshot_attribute


class TestRemoveScreenshotAttribute(TestCase):

    def setUp(self):
        self.database = mongomock.Connection().db

    def test_remove_screenshot_attribute(self):
        self.database.bookmarks.insert([
            {
                'url': 'http://www.google.fr',
                'foo': 'bar',
                'screenshot': 'http://image.com/test.jpg'
            }, {
                'url': 'http://www.yahoo.fr',
                'tony': 'stark',
                'screenshot': 'http://image.com/tony.jpg'
            }, {
                'url': 'http://www.aol.fr',
                'bruce': 'wayne'
            }
        ])
        remove_bookmark_screenshot_attribute.do_it(self.database)

        self.assertEqual([
            {
                'url': 'http://www.aol.fr',
                'bruce': 'wayne'
            }, {
                'url': 'http://www.google.fr',
                'foo': 'bar'
            }, {
                'url': 'http://www.yahoo.fr',
                'tony': 'stark'
            }], list(self.database.bookmarks.find({}, {'_id': 0}).sort([('url', 1)])))
