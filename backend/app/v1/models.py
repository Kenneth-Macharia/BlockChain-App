'''This module contains the application models'''

from ...plugins import mongo, redis_client


class BlockCacheModel:
    '''Manages the blockchain data in the Redis cache'''

    def __init__(self):
        '''Initializes the redis cache model'''

        self.__redis_conn = redis_client

    def push_to_cache(self, transaction_field, transaction_data):
        '''Pushes updated blockchain transactions to redis cache -> None'''

        self.__redis_conn.hset(
            'records_cache', transaction_field, transaction_data)

        self.__redis_conn.persist(transaction_field)

    def pop_from_queue(self, length=False):
        '''Returns a popped transaction from the Redis queue,
        otherwise returns its length if param[length] is set to True
        -> dict or int'''

        trans_list, list_len = [], 0

        if length:
            list_len = self.__redis_conn.llen('records_queue')
        else:
            trans_list.append(self.__redis_conn.blpop('records_queue', 2))

            if None in trans_list:
                trans_list.remove(None)

        return list_len if length else trans_list

    def push_to_queue(self, transaction):
        '''Pushes a transaction to the front of the queue -> None'''

        self.__redis_conn.lpush('records_queue', transaction)


class BlockModel:
    '''Manages the blockchain data in the mongoDB'''

    def __init__(self):
        '''Initializes a collection for block documents in the db'''

        self.__db_conn = mongo.db.blocks_collection

    def block_exists(self, criteria):
        '''Checks if a block in the chain matching the search criteria
        list -> Boolean'''

        query_result = self.__db_conn.find_one(
            {"$and": [
                {"transaction.plot_num": {'$eq': criteria[0]}},
                {"transaction.seller_id": {'$eq': criteria[1]}},
                {"transaction.buyer_id": {'$eq': criteria[2]}}
            ]}
        )

        return True if query_result else False

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


class NodeModel:
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
