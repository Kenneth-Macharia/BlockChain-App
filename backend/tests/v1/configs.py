'''Test DB configs'''

from ...configs import muser, mpassword, mhost, api_key, init_node

MONGO_URI = 'mongodb://%s:%s@%s/test_db' % (
    user, password, host)
