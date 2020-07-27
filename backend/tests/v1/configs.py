'''Test DB configs'''

from ...configs import user, password, host, api_key, init_node

MONGO_URI = 'mongodb://%s:%s@%s/test_db' % (
    user, password, host)
