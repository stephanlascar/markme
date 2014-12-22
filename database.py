from flask.ext.pymongo import PyMongo

mongo = PyMongo()


def add_constraint_to_criteria(criteria, constraint):
    return {'$and': [criteria, constraint]}