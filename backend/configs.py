'''This module fetches and sets up app configurations'''

import os

testing = os.getenv('TEST')
init_node = os.getenv('INIT_NODE_IP')
secret_key = os.getenv('SECRET_KEY')
api_key = os.getenv('API_KEY')
fe_host = os.getenv('FRONTEND_HOST')

public_ip = os.getenv('HOST_IP')
port = os.getenv('HOST_PORT')

mhost = os.getenv('MONGO_DB_HOST')
muser = os.getenv('MONGO_DB_USER')
mpassword = os.getenv('MONGO_DB_PASSWORD')

MONGO_URI = 'mongodb://%s:%s@%s/blockchain_db?authSource=admin' % (
    muser, mpassword, mhost)

rhost = os.getenv('REDIS_DB_HOST')
ruser = os.getenv('REDIS_DB_USER')
rpassword = os.getenv('REDIS_DB_PASSWORD')

REDIS_URL = 'redis://%s:%s@%s:6379/0' % (ruser, rpassword, rhost)
