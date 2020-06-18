'''
This interfacing module:
    1. Persists and fetches data to and from the main Mongo database.
    2. Updates the Redis cache data whenever changes are made to the
        main database.
    3. Secures the blockchain and authenticates external requests for
        node data.
    4. Syncs blockchain and node registry data with other peer nodes.
'''

import hashlib
import json
import requests
from flask import request
from time import time
from uuid import uuid4
from urllib.parse import urlparse
from ..configs import KEY, INIT_NODE_IP
from .models import BlockModel, NodeModel


# TODO:Implement connection and updating Redis upon chain & node updates

class BlockController(object):
    ''' Manages block forging and access to the blockchain '''

    def __init__(self):
        ''' Initializes this node with a seed block '''

        self.blockchain_db = BlockModel()

        if not NodeController().extract_nodes() and \
                self.blockchain_db.get_chain(True) == 0:
            self.create_block(proof=100, previous_hash=10, index=1,
                              transactions=['Seed Block'])

        self.pending_transactions = False

    def create_block(self, proof=None, previous_hash=None,
                     index=None, transactions=[]):

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

        if sync_result is not None:

            # TODO: Ensure transaction details are left in Redis
            # until successful sync

            # TODO: Timed re-sync for prior failed syncs

            self.pending_transactions = True
            return sync_result

        security = SecurityController()
        last_block = self.blockchain_db.get_last_block()

        block = {
            'index': index or (last_block['index'] + 1),
            'timestamp': time(),
            'transaction': transactions,
            'proof': proof or security.proof_of_work(last_block['proof']),
            'previous_hash': previous_hash or security.hash_block(last_block)
        }

        self.blockchain_db.persist_new_block(block)

        # TODO: Remove successful transaction details from Redis
        # TODO: Check no pending tranactions in Redis first

        self.pending_transactions = False

        return self.blockchain_db.get_last_block()

    def extract_chain(self):
        ''' Fetches the blockchain cursor object, unpacks it and returns it.
        To return the chain, status of pending transactions should be
        false else advise requesting node of the status '''

        if self.pending_transactions:
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

        nodes_list = NodeController().extract_nodes()

        # If there are no nodes to sync with e.g an init node, stop sync
        if not nodes_list:
            return

        response_data, max_len, endpoint = None, 0, ''

        endpoint = 'nodes'
        max_len = len(nodes_list)
        response_data = NetworkController().request_data(
            nodes_list, endpoint, max_len, update_chain)

        # TODO: Investigate why init node's seed is being replaced by
        # node 2 empty chain. Logical problem with this code?

        if update_chain:
            endpoint = 'blocks'
            max_len = self.blockchain_db.get_chain(True)
            response_data = NetworkController().request_data(
                nodes_list, endpoint, max_len, update_chain)

        if len(response_data['error_nodes']) > 0:
            return {'error_nodes': response_data['error_nodes']}

        else:
            if update_chain:
                self.blockchain_db.delete_chain()

                for block in response_data['payload']:
                    self.blockchain_db.persist_new_block(block)

            else:
                for node_url in response_data['payload']:
                    NodeController().register_node(node_url)


class NodeController(object):
    ''' Manages node registration and access to the node registry '''

    def __init__(self):
        ''' Initializes this node with a uuid and captures its host IP '''

        self.nodes_db = NodeModel()
        self.node_id = str(uuid4()).replace('-', '')
        self.node_host = urlparse(request.host_url).netloc
        # {'198.162.1.2:5000'}

        if INIT_NODE_IP != 'None':
            self.register_node(INIT_NODE_IP)

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

        return peer_nodes if len(peer_nodes) > 0 else []


class NetworkController(object):
    ''' Manages peer node interation in the blockchain network '''

    def request_data(self, node_url_list, endpoint, max_data_length,
                     update_chain=False):

        ''' Sends HTTP GET requests to peer nodes for either their node
        registry or blockchain data and returns the payload and a dict of
        nodes that did not respond with a 200, if any -> dict '''

        security = SecurityController()
        error_nodes, payload, max_len = [], [], max_data_length

        REQUEST_HEADER = {
                'key': security.blockchain_key(),
                'url': NodeController().node_host
            }

        for node_url in node_url_list:
            response = requests.get(f'http://{node_url}/backend/{endpoint}',
                                    headers=REQUEST_HEADER)

            if response.status_code == 200:
                curr_len = len(response.json()['payload'])
                curr_data = response.json()['payload']

                if update_chain:
                    if curr_len > max_len and \
                            security.validate_chain(curr_data):
                        max_len = curr_len
                        payload = curr_data

                elif not update_chain:
                    if curr_len > max_len:
                        max_len = curr_len
                        payload = curr_data

            else:
                error_nodes.append(
                    {
                        'node': node_url,
                        'status_code': response.status_code,
                        'message': response.json()['message']
                    }
                )

        return {'payload': payload, 'error_nodes': error_nodes}


class SecurityController(object):
    ''' Manages creation of node security features and authorization '''

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

    def blockchain_key(self):
        ''' Returns SHA-256 hash of the blockchain key -> str '''

        return hashlib.sha256(KEY.encode()).hexdigest()

    def authorize_node(self, hashed_blockchain_key):
        '''
        Verifies if the supplied hashed key in a node request correponds to
        the verified blockchain key -> boolean
        '''

        return hashed_blockchain_key == self.blockchain_key()

    def validate_chain(self, chain):
        ''' Checks a blockchain's validity -> boolean '''

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
