'''
This interfacing module:
    1. Persists and fetches data to and from the main Mongo database.
    2. Updates the Redis cache data whenever changes are made to the
        main database.
    3. Secures the blockchain and authenticates external requests for
        node data.
    4. Syncs blockchain and node registry data with other peer nodes
'''

import json
import requests
import hashlib
from flask import request
from time import time
from uuid import uuid4
from urllib.parse import urlparse
from ...configs import secret_key, init_node
from .models import BlockModel, NodeModel, BlockCacheModel


# TODO:Implement period syncs to keep all node updated


class CacheController(object):
    ''' Manges transmission of blockchain data to from the redis cache'''

    def update_blockchain_cache(self):
        '''Serializes blockchain data before adding to redis cache'''

        # TODO: Implement hashmap with select details to redis
        blocks = []

        for block in BlockModel().get_chain():
            blocks.append(
                {
                    'timestamp': blocks['timestamp'],
                    'size': blocks['transaction']['size'],
                    'location': blocks['transaction']['location'],
                    'county': blocks['transaction']['county'],
                    'current_owner': blocks['transaction']['buyer_id'],
                    'original_owner': blocks['transaction']['original_owner']
                }
            )

        BlockCacheModel().push_chain(blocks)


class BlockController(object):
    '''Manages block forging and access to the blockchain'''

    pending_transactions = False

    def __init__(self):
        '''Initializes this node with a seed block'''

        self.blockchain_db = BlockModel()

        if not NodeController().extract_nodes() and \
                self.blockchain_db.get_chain(True) == 0:
            self.forge_block(proof=100, previous_hash=10, index=1,
                             transaction={'seed_block': 'True'})

    def forge_block(self, proof=None, previous_hash=None,
                    index=None, transaction={}):

        '''
        1. Updates the chain, (ensuring all node have successfully
            returned their chains for comparison, to ensure TRUE consensus)
            if even one node did not, the new transaction is postponed
            until all nodes are available. This means leaving the
            transactions details in Redis and trying sync again after a
            while. If all these pass, then a new block for the new
            transaction is forged.
        2. Proof (int) is the proof computed by the proof of work algorithm.
        3. Previous_hash (str) is the previous block hash.
        4. Sync_result can be:
            (a) error_node list => stop blog forging until no error_nodes
            are returned
            (b) None => sync was successful with all registered node or
            no nodes to sync with (for init node): forge new block
            (new transaction or seed block)
        '''

        sync_result = self.sync(update_chain=True)

        if sync_result and index is None:
            BlockController.pending_transactions = True

            # TODO: Leave transactions in Redis until successful sync
            # TODO: Timed re-sync for prior failed syncs

            return sync_result

        security = SecurityController()
        last_block = self.blockchain_db.get_last_block()

        block = {
            'index': index or (last_block['index'] + 1),
            'timestamp': time(),
            'transaction': transaction,
            'proof': proof or security.proof_of_work(last_block['proof']),
            'previous_hash': previous_hash or security.hash_block(last_block)
        }

        if not transaction.get('seed_block', None):
            plt_no = transaction.get('plot_number', None)
            seller_id = transaction.get('seller_id', None)
            buyer_id = transaction.get('buyer_id', None)

            print(plt_no, seller_id, buyer_id)

            if self.blockchain_db.block_exists(
                    [plt_no, seller_id, buyer_id]):

                return {'validation_error': 'transaction already exist'}

        self.blockchain_db.persist_new_block(block)
        # TODO: Remove successful transaction details from Redis

        # CacheController().update_blockchain_cache()

        # TODO: Check no pending transactions in Redis first before resetting
        BlockController.pending_transactions = False

        return self.blockchain_db.get_last_block()

    def extract_chain(self):
        '''
        Fetches the blockchain cursor object, unpacks it and returns it.
        To return the chain, status of pending transactions should be
        false else advise requesting node of the status -> list
        '''

        if BlockController.pending_transactions:
            return None

        result_cursor = self.blockchain_db.get_chain()
        chain = [document for document in result_cursor]

        return chain

    def sync(self, update_chain=False):
        '''
        1. If param[update_chain] is False (default), then only the node
        registry will be synchornized, if it's True, then both the node
        registry and the blockchain will be synchronized with all the peer
        nodes.
        2. Synchronization means replacing our data with the most up-date,
        found among the all peer nodes.
        3. Ensures that successful contact was made with all nodes in the
        network for a chain update, else returns a list of nodes that chain
        syc did not succeed with
        -> None or list
        '''

        node_obj = NodeController()
        nodes_list = node_obj.extract_nodes()

        # If there are no nodes to sync with e.g an init node, stop sync
        if not nodes_list:
            return {'sync_error': 'No nodes to sync with'}

        response_data, max_len, endpoint = None, 0, ''

        endpoint = 'nodes'
        max_len = len(nodes_list)

        response_data = NetworkController().request_data(
            nodes_list, endpoint, max_len)

        if len(response_data['error_nodes']) > 0:
            return {'sync_error': response_data['error_nodes']}

        else:
            if len(response_data['payload']) > 0:
                for node_url in response_data['payload']:
                    node_obj.register_node(node_url)

                nodes_list = node_obj.extract_nodes()

        if update_chain:
            endpoint = 'blocks'
            max_len = self.blockchain_db.get_chain(True)

            response_data = NetworkController().request_data(
                nodes_list, endpoint, max_len)

            if len(response_data['error_nodes']) > 0:
                return {'sync_error': response_data['error_nodes']}

            else:
                if len(response_data['payload']) > 0:
                    self.blockchain_db.delete_chain()

                    for block in response_data['payload']:
                        self.blockchain_db.persist_new_block(block)


class NodeController(object):
    '''Manages node registration and access to the node registry'''

    def __init__(self):
        '''Initializes this node with a uuid and captures its host IP'''

        self.nodes_db = NodeModel()
        self.node_id = str(uuid4()).replace('-', '')
        self.node_host = urlparse(request.host_url).netloc
        # {'198.162.1.2:5000'}

        if init_node:
            self.register_node(init_node)

    def register_node(self, node_url):
        '''
        Adds a new peer node address ('198.162.1.2:5000'), ensuring it is not
        already registered and that we don't register this node -> None
        '''

        if not self.nodes_db.get_node(node_url) and node_url != self.node_host:
            node = {
                'node_url': node_url
            }

            self.nodes_db.persist_new_node(node)

    def extract_nodes(self):
        '''
        Fetches the node registry cursor object, unpacks it and returns it
        '''

        result_cursor = self.nodes_db.get_nodes()
        peer_nodes = [document['node_url'] for document in result_cursor]

        return peer_nodes


class NetworkController(object):
    '''Manages peer node interation in the blockchain network'''

    def request_data(self, node_url_list, endpoint, max_data_length):

        '''
        Sends HTTP GET requests to peer nodes for either their node
        registry or blockchain data and returns the payload and a dict of
        nodes that did not respond with a 200, if any -> dict
        '''

        security = SecurityController()
        error_nodes, payload, mlen = [], [], max_data_length

        auth_header = {
            'URL': NodeController().node_host,
            'API_KEY': security.blockchain_key()
        }

        for node_url in node_url_list:
            try:
                response = requests.get(
                    f'http://{node_url}/backend/v1/{endpoint}',
                    headers=auth_header)

            except Exception:
                error_nodes.append(
                    {
                        'message': f'Failed to connect to: {node_url}'
                    }
                )

                continue

            if response.status_code == 200:
                curr_len = len(response.json()['payload'])
                curr_data = response.json()['payload']

                if endpoint == 'blocks':
                    if curr_len > mlen and \
                            security.validate_chain(curr_data):
                        mlen = curr_len
                        payload = curr_data

                else:
                    if curr_len > mlen:
                        mlen = curr_len
                        payload = curr_data

            else:
                error_nodes.append(
                    {
                        'node': node_url,
                        'status_code': response.status_code,
                        'message': response.json()['message']  # TODOif no msg?
                    }
                )

        return {'payload': payload, 'error_nodes': error_nodes}


class SecurityController(object):
    '''Manages creation of node security features and authorization'''

    def validate_proof(self, last_proof, proof):
        '''
        Validates that the hash of two consequtive proofs concat(last_proof,
        current_proof), satisfies the proof_of_work algorithm, since the
        current_block's proof is computed using the previous_block's proof
        -> boolean
        '''

        guess_hash = hashlib.sha256(
            f'{last_proof}{proof}'.encode()).hexdigest()
        return guess_hash[:4] == '0000'

    def proof_of_work(self, last_proof, current_proof=None):
        '''
        Returns a valid proof for the new block to be forged. Computation
        algorithm: Find a number 'proof' (for the current block being forged)
        such that concat(last_proof, proof) contains at least 4 leading zeros
        -> int
        '''

        proof = 0
        while self.validate_proof(last_proof, proof) is False:
            proof += 1
        return proof

    def blockchain_key(self):
        '''Returns the hashed blockchain key -> str'''

        BLOCKCHAIN_ID = '87a56999-9a36-4359-a8c2-8217260f5a85'
        key = f'{secret_key}-{BLOCKCHAIN_ID}'
        return hashlib.sha256(key.encode()).hexdigest()

    def hash_block(self, block):
        '''
        Returns a SHA-256 hash of a block -> str
            1. dumps() deserializes json into str
            2. encode() turns str to unicode
            3. hexdigest() return block hash in hexadecimal digits
            4. The block dictionary should be ordered or the hashes will be
            inconsistent.
        '''

        block_uni = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_uni).hexdigest()

    def authorize_node(self, header):
        '''
        Authenticates and authorizes the requesting node to access our data
        -> str
        '''

        if header['Api-Key'] == self.blockchain_key() and \
                header['Url'] != NodeController().node_host:
            return header['Url']

    def validate_chain(self, chain):
        '''Checks a blockchain's validity -> boolean'''

        previous_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            current_block = chain[current_index]

            if current_block['previous_hash'] != \
                    self.hash_block(previous_block):
                return False

            if not self.validate_proof(previous_block['proof'],
                                       current_block['proof']):
                return False

            previous_block = current_block
            current_index += 1

        return True
