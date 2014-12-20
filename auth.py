import argparse
import datetime
import os
from bson import ObjectId
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager, UserMixin
from pymongo import Connection
from pymongo.uri_parser import parse_uri
from database import mongo

login_manager = LoginManager()
bcrypt = Bcrypt()


@login_manager.user_loader
def load_user(user_id):
    return User(mongo.db.users.find_one({'_id': ObjectId(user_id)}))


class User(UserMixin):

    def __init__(self, args):
        self.id = args['_id']
        self.email = args['email']

    def __str__(self):
        return self.email


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='Ajoute un nouvel utilisateur')
    arg_parser.add_argument('-e', '--email', required=True, dest="email")
    arg_parser.add_argument('-p', '--password', required=True, dest="password")
    args = arg_parser.parse_args()

    mongo_uri = os.environ['MONGOLAB_URI']
    mongo_creds = parse_uri(mongo_uri)
    connection = Connection(mongo_creds['nodelist'][0][0], mongo_creds['nodelist'][0][1])
    db = connection[mongo_creds['database']]
    db.authenticate(mongo_creds['username'], mongo_creds['password'])

    db.users.save({'email': args.email, 'password': bcrypt.generate_password_hash(args.password, rounds=12), 'inserted': datetime.datetime.utcnow()})
