'''
This module fetches and sets up app configurations
'''

import os

#Application configurations


# Database configurations
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')

MONGO_URI = 'mongodb://%s:%s@%s/blockchain_db?authSource=admin' % (user, password, host)