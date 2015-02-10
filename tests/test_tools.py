# -*- coding: utf-8 -*-
from StringIO import StringIO
import datetime
from bson import ObjectId
from nose.tools import assert_equal
from auth import bcrypt
from database import mongo
from tests import mongo_data, WebAppTestCase


class TestTools(WebAppTestCase):

    @mongo_data(users=[{'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}])
    def test_index(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.get('/tools', follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('tools/index.html')


class TestDeleteAllBookmarks(WebAppTestCase):

    @mongo_data(users=[{'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}])
    def test_display_delete_all_bookmarks(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.get('/tools/delete_all', follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('tools/delete_all.html')

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


class TestExportBookmarks(WebAppTestCase):

    @mongo_data(users=[{'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}])
    def test_display_import_bookmark(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.get('/tools/export', follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('tools/export.html')

    # @mongo_data(users=[{'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)},
    #                    {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'tony@stark.com', 'nickname': 'ironman', 'password': bcrypt.generate_password_hash('jarvis', rounds=12)}],
    #             bookmarks=[{'url': 'http://www.foo.com', 'title': 'titre 1', 'referrer': 'http://a', 'description': 'description 1', 'tags': ['test', 'unitaire'], 'user': {'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'foo@bar.com'}, 'published': datetime.datetime.now()},
    #                        {'url': 'http://www.bar.com', 'title': 'titre 2', 'referrer': 'http://b', 'description': 'description 1', 'tags': ['tag'], 'user': {'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'foo@bar.com'}, 'published': datetime.datetime.now()},
    #                        {'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb6'), 'email': 'tony@stark.com'}, 'published': datetime.datetime.now()}])
    # def test_export(self):
    #     pass


class TestImportBookmarks(WebAppTestCase):

    @mongo_data(users=[{'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}])
    def test_display_import_bookmark(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.get('/tools/import', follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('tools/import.html')

    @mongo_data(users=[{'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'foo@bar.com', 'nickname': 'james', 'password': bcrypt.generate_password_hash('password', rounds=12)}],
                bookmarks=[{'url': 'http://www.foo.com', 'user': {'_id': ObjectId('5495f2a88766017d44130bb1'), 'email': 'foo@bar.com'}, 'published': datetime.datetime.now()}])
    def test_import_bookmarks(self):
        self.client.post('/', data=dict(email='foo@bar.com', password='password'))
        response = self.client.post('/tools/import', data=dict(atom_file=(StringIO(XML_FILE_CONTENT), 'bookmarks.xml')))
        self.assert200(response)
        self.assertTemplateUsed('tools/import.html')
        self.assert_flashes(u'Fichier importé avec succès !')
        self.assertEqual(5, mongo.db.bookmarks.find().count())

        self.assertEqual({
            'url': 'https://www.simple.com/',
            'title': 'Simple | Worry-free Alternative to Traditional Banking',
            'referrer': 'http://colin-verdier.com/le-logiciel-devore-le-monde-depuis-les-etats-unis/',
            'description': '',
            'public': True,
            'tags': [],
            'user': {
                '_id': ObjectId('5495f2a88766017d44130bb1'),
                'email': 'foo@bar.com',
                'nickname': 'james'
            }
        }, mongo.db.bookmarks.find_one({'url': 'https://www.simple.com/', 'user._id': ObjectId('5495f2a88766017d44130bb1')}, {'_id': 0, 'published': 0}))

        self.assertEqual({
            'url': 'http://www.foo.com',
            'title': 'Update bookmark',
            'referrer': 'http://colin-verdier.com/le-logiciel-devore-le-monde-depuis-les-etats-unis/',
            'description': 'Test update bookmark',
            'public': True,
            'tags': [],
            'user': {
                '_id': ObjectId('5495f2a88766017d44130bb1'),
                'email': 'foo@bar.com',
                'nickname': 'james'
            }
        }, mongo.db.bookmarks.find_one({'url': 'http://www.foo.com', 'user._id': ObjectId('5495f2a88766017d44130bb1')}, {'_id': 0, 'published': 0}))

        self.assertEqual({
            'url': 'http://retrospectivewiki.org/index.php?title=Retrospective_Plans',
            'title': 'Retrospective Plans - Agile Retrospective Resource Wiki',
            'referrer': '',
            'description': 'A collection of detailed retrospective plans you can run or take inspiration from',
            'public': True,
            'tags': ['agile', 'wiki'],
            'user': {
                '_id': ObjectId('5495f2a88766017d44130bb1'),
                'email': 'foo@bar.com',
                'nickname': 'james'
            }
        }, mongo.db.bookmarks.find_one({'url': 'http://retrospectivewiki.org/index.php?title=Retrospective_Plans', 'user._id': ObjectId('5495f2a88766017d44130bb1')}, {'_id': 0, 'published': 0}))

        self.assertEqual({
            'url': 'http://www.asual.com/jquery/address/',
            'title': 'Asual | jQuery Address - Deep linking for the masses',
            'referrer': '',
            'description': 'The jQuery Address plugin provides powerful deep linking',
            'public': True,
            'tags': ['programmation', 'javascript', 'jQuery', 'open source', 'appb'],
            'user': {
                '_id': ObjectId('5495f2a88766017d44130bb1'),
                'email': 'foo@bar.com',
                'nickname': 'james'
            }
        }, mongo.db.bookmarks.find_one({'url': 'http://www.asual.com/jquery/address/', 'user._id': ObjectId('5495f2a88766017d44130bb1')}, {'_id': 0, 'published': 0}))

        self.assertEqual({
            'url': 'http://europa.eu/epso/index_fr.htm',
            'title': 'EUROPA - EPSO',
            'referrer': '',
            'description': '',
            'public': False,
            'tags': ['emploi'],
            'user': {
                '_id': ObjectId('5495f2a88766017d44130bb1'),
                'email': 'foo@bar.com',
                'nickname': 'james'
            }
        }, mongo.db.bookmarks.find_one({'url': 'http://europa.eu/epso/index_fr.htm', 'user._id': ObjectId('5495f2a88766017d44130bb1')}, {'_id': 0, 'published': 0}))


XML_FILE_CONTENT = """
<?xml version="1.0" encoding="UTF-8"?>

<feed xmlns="http://www.w3.org/2005/Atom" xmlns:bm="http://blogmarks.net/ns/" xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:app="http://www.w3.org/2007/app" xmlns:activity="http://activitystrea.ms/spec/1.0/" >

  <id>bm-marks-users:10091-includePrivates:1,10091-last:100000</id>
  <title>Mes marks</title>
  <updated>2012-11-08T08:44:14Z</updated>

  <openSearch:totalResults>1987</openSearch:totalResults>
  <openSearch:startIndex>0</openSearch:startIndex>
  <openSearch:itemsPerPage>100000</openSearch:itemsPerPage>

  <link rel="self" type="application/atom+xml" href="http://blogmarks.net/api/user/jpcaruana/marks/?last=100000&amp;includePrivates=1&amp;format=atom" title="Mes marks"/>
  <link rel="alternate" type="text/html" href="http://blogmarks.net/my/marks/?last=100000&amp;includePrivates=1" title="Mes marks"/>

<entry>
  <id>tag:blogmarks.net,2012:1058937637</id>
  <title>Simple | Worry-free Alternative to Traditional Banking</title>
  <updated>2012-11-08T08:44:14Z</updated>
  <published>2012-11-08T08:44:14Z</published>
  <author>
    <name>jpcaruana</name>
    <uri>http://blogmarks.net/user/jpcaruana</uri>
  </author>
  <link href="https://www.simple.com/"/>
  <link rel="related" href="https://www.simple.com/" type="text/html"/>
  <link rel="edit" href="http://blogmarks.net/api/user/jpcaruana/mark/1058937637" type="application/atom+xml"/>
  <link rel="alternate" href="https://www.simple.com/" type="text/html"/>
  <link rel="avatar" href="http://blogmarks.net/avatar/3c13ffe3d0e3d8512cdd4e3f5c000d9e"/>
  <link rel="via" href="http://colin-verdier.com/le-logiciel-devore-le-monde-depuis-les-etats-unis/" type="text/html"/>
  <link rel="enclosure" href="http://blogmarks.net/screenshots/2012/11/08/8a8c1ffc2616b643ab1fac34819c920f.jpg" type="image/jpg"/>
  <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
  <activity:object>
    <activity:object-type>http://activitystrea.ms/schema/1.0/bookmark</activity:object-type>
  </activity:object>
</entry>

<entry>
  <id>tag:blogmarks.net,2012:1058937638</id>
  <title>Update bookmark</title>
  <updated>2012-11-08T08:44:14Z</updated>
  <published>2012-11-08T08:44:14Z</published>
  <author>
    <name>jpcaruana</name>
    <uri>http://blogmarks.net/user/jpcaruana</uri>
  </author>
  <link href="http://www.foo.com"/>
  <link rel="related" href="http://www.foo.com" type="text/html"/>
  <link rel="edit" href="http://blogmarks.net/api/user/jpcaruana/mark/1058937638" type="application/atom+xml"/>
  <link rel="alternate" href="http://www.foo.com" type="text/html"/>
  <link rel="avatar" href="http://blogmarks.net/avatar/3c13ffe3d0e3d8512cdd4e3f5c000d9e"/>
  <link rel="via" href="http://colin-verdier.com/le-logiciel-devore-le-monde-depuis-les-etats-unis/" type="text/html"/>
  <link rel="enclosure" href="http://blogmarks.net/screenshots/2012/11/08/8a8c1ffc2616b643ab1fac34819c920f.jpg" type="image/jpg"/>
  <content type="text"><![CDATA[Test update bookmark]]></content>
  <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
  <activity:object>
    <activity:object-type>http://activitystrea.ms/schema/1.0/bookmark</activity:object-type>
  </activity:object>
</entry>

<entry>
  <id>tag:blogmarks.net,2012:1058937191</id>
  <title>Retrospective Plans - Agile Retrospective Resource Wiki</title>
  <updated>2012-11-06T08:50:42Z</updated>
  <published>2012-11-06T08:50:42Z</published>
  <author>
    <name>jpcaruana</name>
    <uri>http://blogmarks.net/user/jpcaruana</uri>
  </author>
  <link href="http://retrospectivewiki.org/index.php?title=Retrospective_Plans"/>
  <link rel="related" href="http://retrospectivewiki.org/index.php?title=Retrospective_Plans" type="text/html"/>
  <link rel="edit" href="http://blogmarks.net/api/user/jpcaruana/mark/1058937191" type="application/atom+xml"/>
  <link rel="alternate" href="http://retrospectivewiki.org/index.php?title=Retrospective_Plans" type="text/html"/>
  <link rel="avatar" href="http://blogmarks.net/avatar/3c13ffe3d0e3d8512cdd4e3f5c000d9e"/>
  <link rel="enclosure" href="http://blogmarks.net/screenshots/2012/11/06/34623c9a2b80f91741a65230134caf99.jpg" type="image/jpg"/>
  <category scheme="http://blogmarks.net/tag/" term="agile" label="agile"/>
  <category scheme="http://blogmarks.net/tag/" term="wiki" label="wiki"/>
  <content type="text"><![CDATA[A collection of detailed retrospective plans you can run or take inspiration from]]></content>
  <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
  <activity:object>
    <activity:object-type>http://activitystrea.ms/schema/1.0/bookmark</activity:object-type>
  </activity:object>
</entry>


<entry>
  <id>tag:blogmarks.net,2011:1058875925</id>
  <title>Asual | jQuery Address - Deep linking for the masses</title>
  <updated>2011-06-30T07:05:55Z</updated>
  <published>2011-06-30T07:05:33Z</published>
  <author>
    <name>jpcaruana</name>
    <uri>http://blogmarks.net/user/jpcaruana</uri>
  </author>
  <link href="http://www.asual.com/jquery/address/"/>
  <link rel="related" href="http://www.asual.com/jquery/address/" type="text/html"/>
  <link rel="edit" href="http://blogmarks.net/api/user/jpcaruana/mark/1058875925" type="application/atom+xml"/>
  <link rel="alternate" href="http://www.asual.com/jquery/address/" type="text/html"/>
  <link rel="avatar" href="http://blogmarks.net/avatar/3c13ffe3d0e3d8512cdd4e3f5c000d9e"/>
  <link rel="enclosure" href="http://blogmarks.net/screenshots/2011/06/30/7f183b38b267660c4efe2f8de2c31bbf.jpg" type="image/jpg"/>
  <category scheme="http://blogmarks.net/tag/" term="programmation" label="programmation"/>
  <category scheme="http://blogmarks.net/tag/" term="javascript" label="javascript"/>
  <category scheme="http://blogmarks.net/tag/" term="jQuery" label="jQuery"/>
  <category scheme="http://blogmarks.net/tag/" term="open%2Bsource" label="open source"/>
  <category scheme="http://blogmarks.net/user/jpcaruana/private-tag/" term="appb" label="appb"/>
  <content type="text"><![CDATA[The jQuery Address plugin provides powerful deep linking]]></content>
  <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
  <activity:object>
    <activity:object-type>http://activitystrea.ms/schema/1.0/bookmark</activity:object-type>
  </activity:object>
</entry>



<entry>
  <id>tag:blogmarks.net,2006:677738</id>
  <title>EUROPA - EPSO</title>
  <updated>2006-07-05T16:45:55Z</updated>
  <published>2006-07-05T16:45:53Z</published>
  <author>
    <name>jpcaruana</name>
    <uri>http://blogmarks.net/user/jpcaruana</uri>
  </author>
  <link href="http://europa.eu/epso/index_fr.htm"/>
  <link rel="related" href="http://europa.eu/epso/index_fr.htm" type="text/html"/>
  <link rel="edit" href="http://blogmarks.net/api/user/jpcaruana/mark/677738" type="application/atom+xml"/>
  <link rel="alternate" href="http://europa.eu/epso/index_fr.htm" type="text/html"/>
  <link rel="avatar" href="http://blogmarks.net/avatar/3c13ffe3d0e3d8512cdd4e3f5c000d9e"/>
  <link rel="enclosure" href="http://blogmarks.net/screenshots/2006/07/05/14966dd39e6e0f158aaccaeea2d5e619.png" type="image/png"/>
  <category scheme="http://blogmarks.net/user/jpcaruana/private-tag/" term="emploi" label="emploi"/>
  <bm:isPrivate>true</bm:isPrivate>
  <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
  <activity:object>
    <activity:object-type>http://activitystrea.ms/schema/1.0/bookmark</activity:object-type>
  </activity:object>
</entry>

</feed>"""
