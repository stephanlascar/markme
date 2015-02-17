from flask.ext.mongoalchemy import MongoAlchemy
from flask.ext.pymongo import PyMongo
from mongoalchemy import session


class CustomMongoAlchemy(MongoAlchemy):

    def init_app(self, app, config_prefix='MONGOALCHEMY'):
        self.config_prefix = config_prefix

        def key(suffix):
            return '%s_%s' % (config_prefix, suffix)

        self.session = session.Session.connect(app.config.get('MONGO_URI').split('/')[-1],
                                               safe=app.config.get(key('SAFE_SESSION'), False),
                                               host=app.config.get('MONGO_URI'))
        self.Document._session = self.session


mongo = PyMongo()
db = CustomMongoAlchemy()


def add_constraint_to_criteria(criteria, constraint):
    return {'$and': [criteria, constraint]}
