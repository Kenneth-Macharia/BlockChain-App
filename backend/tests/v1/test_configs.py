'''Test DB configs'''

import os

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')

MONGO_URI = 'mongodb://%s:%s@%s/test_db' % (
    user, password, host)
