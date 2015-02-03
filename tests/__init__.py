# -*- coding: utf-8 -*-
from functools import update_wrapper
from database import mongo


def mongo_data(**collections):
    def decorator(decorated):
        def wrapper(self):
            for collection, data in collections.items():
                mongo.db[collection].remove()
                mongo.db[collection].insert(data)
            decorated(self)
        return update_wrapper(wrapper, decorated)
    return decorator
