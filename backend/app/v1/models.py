'''This module contains the application models'''

from ...plugins import mongo, redis_client


class BlockCacheModel(object):
    '''Manages the blockchain data in the Redis cache'''

    def __init__(self):
        '''Initializes the redis cache model'''

        self.__redis_conn = redis_client

    def push_chain(self, key, block):
        '''Pushes updated blockchain to redis cache'''

        if self.__redis_conn.exists():
            self.__redis_conn.delete('blockchain_cache')

        for block in blocks:
            self.__redis_conn.rpush('blockchain_cache', block)

        self.__redis_conn.persist('blockchain_cache')


class BlockModel(object):
    '''Manages the blockchain data in the mongoDB'''

    def __init__(self):
        '''Initializes a collection for block documents in the db'''

        self.__db_conn = mongo.db.blocks_collection

    def get_chain(self, length=False):
        '''Returns the entire block_chain or it's length if param[length] is
        set to True -> cursor object or int'''

        if length:
            return self.__db_conn.count_documents({})

        else:
            return self.__db_conn.find({}, {'_id': False})

    def persist_new_block(self, new_block):
        '''Saves a new block to the database -> None'''

        self.__db_conn.insert_one(new_block)

    def block_exists(self, criteria):
        '''Finds the a block that meets the criteria list -> boolean'''

        #TODO: Fix args # error ofr count_documents
        return True if self.__db_conn.count_documents(
            {"transaction['plot_number']": {'$eq': criteria[0]}},
            {"transaction['seller_id']": {'$eq': criteria[1]}},
            {"transaction['buyer_id']": {'$eq': criteria[2]}}) != 0 else False

    def get_last_block(self, index=False):
        '''Returns the last block in the chain or it's index, if param[index]
        is set to True -> dict or int'''

        last_index = self.get_chain(True)

        last_block = self.__db_conn.find_one(
            {"index": last_index}, {'_id': False})

        return last_block['index'] if index else last_block

    def delete_chain(self):
        '''Deletes all blocks in our chain -> None'''

        self.__db_conn.delete_many({})


class NodeModel(object):
    '''Manages the peer node data in the blockchain network'''

    def __init__(self):
        ''' Initializes a collection for node documents in the db. '''

        self.__db_conn = mongo.db.nodes_collection

    def get_nodes(self, length=False):
        '''Returns all registered nodes or number of nodes if param[length]
        is set to True -> cursor object or int'''

        if length:
            return self.__db_conn.count_documents({})

        else:
            return self.__db_conn.find({}, {'_id': False})

    def persist_new_node(self, node):
        '''Saves a network new peer node to the database -> None'''

        self.__db_conn.insert_one(node)

    def get_node(self, url):
        '''Returns the node with the specified url -> dict'''

        return self.__db_conn.find_one({"node_url": url}, {'_id': False})

    def delete_all_nodes(self):
        '''Deletes the entire node registry -> None'''

        self.__db_conn.delete_many({})
