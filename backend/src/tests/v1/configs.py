'''Test DB configs'''

from ...configs import (muser, mpassword, mhost, api_key, init_node,
                        ruser, rpassword, rhost)

MONGO_URI = 'mongodb://%s:%s@%s/test_db' % (muser, mpassword, mhost)
REDIS_URL = 'redis://%s:%s@%s:6379/0' % (ruser, rpassword, rhost)
