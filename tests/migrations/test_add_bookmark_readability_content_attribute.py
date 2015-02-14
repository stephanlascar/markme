# -*- coding: utf-8 -*-
from unittest import TestCase

from httplib2 import Response
from mock import MagicMock
import mongomock
from readability import ParserClient

from migrations import add_bookmark_readability_content_attribute


class TestAddBookmarkReadabilityContentAttribute(TestCase):

    def setUp(self):
        self.database = mongomock.Connection().db
        self.parser_client = ParserClient('readability secret parser key')
        response = Response(dict())
        response.content = dict(content='<p>article</p>')
        self.parser_client.get_article_content = MagicMock(return_value=response)

    def test_add_bookmark_readability_content_attribute(self):
        self.database.bookmarks.insert([
            {
                'url': 'https://en.wikipedia.org/wiki/Mark_Twain'
            }, {
                'url': 'https://en.wikipedia.org/wiki/Marco_Polo'
            }
        ])
        add_bookmark_readability_content_attribute.do_it(self.database, self.parser_client)

        self.assertEqual([
            {
                'url': 'https://en.wikipedia.org/wiki/Marco_Polo',
                'content': '<p>article</p>'
            }, {
                'url': 'https://en.wikipedia.org/wiki/Mark_Twain',
                'content': '<p>article</p>'
            }], list(self.database.bookmarks.find({}, {'_id': 0}).sort([('url', 1)])))
