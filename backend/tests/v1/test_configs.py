'''Test DB configs'''

from ...configs import user, password, host

MONGO_URI = 'mongodb://%s:%s@%s/test_db' % (
    user, password, host)
