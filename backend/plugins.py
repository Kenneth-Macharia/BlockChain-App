'''This module initializes all app plugins such databases'''

from flask_pymongo import PyMongo
from flask_redis import FlaskRedis

mongo = PyMongo()
redis_client = FlaskRedis()
