'''
This module is the interface between the Redis cache and the persistant back-end. It:

    1. Forges new blocks in the chain
    2. Synchronizes the blockchain across the peer nodes in the blockchain network
    3. Validates and secure the blockchain
    4. Fetches transactions to be included in new nodes from Redis
    5. Fetches queries for transaction data from Redis and save back the query results
    6. Maintains updated data in the Redis cache
'''

import hashlib, json, requests
from time import time
from urllib.parse import urlparse
from .models import BlockModel, NodeModel

class BlockController(object):
    ''' Manages block forging, blockchain verification and security. '''

    def __init__(self):
        '''
            Initializes the blocks back-end with a seed block if first node in the network. A new node, that is not the first node, joining the network updates it's blockchain using the exisitng peer node data, added via the front-end.
        '''

        # Create seed block
        if BlockModel().get_chain(True) == 0:
            self.new_block(proof=100, previous_hash=10, index=1)


        #TODO If not first block, update blockchain from network peer added via UI

    def extract_chain(self):
        ''' Return the full blockchain from the back-end -> list '''

        result_cursor = BlockModel().get_chain()
        chain = []

        for document in result_cursor:
            chain.append(document)

        return chain

    def new_block(self, proof=None, previous_hash=None, index=None, transactions=[]):
        '''
        Forges a new block. Proof (int) is the proof computed by the proof of work algorithm. Previous_hash (str) is the previous block hash -> dict
        '''

        last_block = BlockModel().get_last_block()

        block = {
            'index': index or (last_block['index'] + 1),
            'timestamp': time(),
            'transaction': transactions,
            'proof': proof or self.proof_of_work(last_block['proof']),
            'previous_hash': previous_hash or self.hash_block(last_block)
        }

        BlockModel().persist_new_block(block)

        return BlockModel().get_last_block()

    def update_chain(self):
        '''
        Checks if our chain is in sync with the rest of the network, if not, it updates our chain by replacing our chain with the longest one in the network -> True (if up-to-date) or False (if not, in which case it's updated)
        '''

        # Get all the peer nodes in our records
        neighbour_nodes = NodeController().fetch_all_nodes()

        # Initialize our chain as currently the longest
        max_length = BlockModel().get_chain(True)

        new_chain = None

        # Grab and verify the chains from all the nodes in our network
        for node in neighbour_nodes:
            # For each node in our records, fetch its chain
            response = requests.get(f'http://{node["address"]}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

            # Check if the length is longer and the chain is valid
            if length > max_length and BlockController.validate_chain(chain):
                max_length = length
                new_chain = chain

        # Replace our chain if we discovered a valid chain, longer than ours.
        if new_chain:
            BlockModel().delete_chain()

            for block in new_chain:
                BlockModel().insert_one(block)

            return True

        return False

    @classmethod
    def validate_chain(cls, chain):
        ''' Checks a blockchain's validity -> boolean '''

        previous_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            current_block = chain[current_index]

            # Check that all the block hashes in the chain are correct
            if current_block['previous_hash'] != cls.hash_block(previous_block):
                return False

            # Check that all the block proofs in the chain are correct
            if not cls.validate_proof(previous_block['proof'], current_block['proof']):
                return False

            previous_block = current_block
            current_index += 1

        return True

    @classmethod
    def validate_proof(cls, last_proof, proof):
        '''
        Validates that the hash of two consequtive proofs concat(last_proof, current_proof), satisfies the proof_of_work algorithm, since the current_block's proof is computed using the previous_block's proof -> boolean
        '''

        guess_hash = hashlib.sha256(f'{last_proof}{proof}'.encode()).hexdigest()
        return guess_hash[:4] == '0000'

    @classmethod
    def proof_of_work(cls, last_proof, current_proof=None):
        '''
        Returns a valid proof for the new block to be forged. Computation algorithm: Find a number 'proof' (for the current block being forged) such that concat(last_proof, proof) conatains at least 4 leading zeros -> int
        '''

        proof = 0
        while cls.validate_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @classmethod
    def hash_block(cls, block):
        '''
        Returns a SHA-256 hash of a block -> str
            1. dumps() deserializes json into str
            2. encode() turns str to unicode
            3. hexdigest() return block hash in hexadecimal digits
            4. The block dictionary should be ordered or the hashes will be inconsistent.
        '''

        block_uni = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_uni).hexdigest()


class NodeController(object):
    ''' Manages peer-to-peer node relationship in the blockchain network. '''

    def fetch_all_nodes(self):
        return NodeModel().get_all_nodes()


    def register_node(self, address):
        '''
        Adds new node, ensuring it is not already registered, beforehand. Address of node (str) e.g 'http://198.162.1.2:5000' -> None
        '''

        parsed_url = urlparse(address).netloc

        if not NodeModel().get_one_node(parsed_url):
            node = {
                'address': parsed_url,
            }

            NodeModel().persist_new_node(node)
            return NodeModel().get_one_node(parsed_url)
