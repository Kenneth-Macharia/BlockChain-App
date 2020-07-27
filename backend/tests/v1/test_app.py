'''This module tests the nodes resources'''

import responses
from flask import json
from unittest import TestCase
from ... import create_app
from ...plugins import mongo
from .configs import api_key, init_node

# Set up globals
test_client = create_app().test_client()
db = mongo.db
base_url = 'http://localhost:5000/backend/v1'


class TestNodeAuth(TestCase):

    def setUp(self):
        '''Setup before each test'''

        self.test_auth_url1 = f'{base_url}/nodes'
        self.test_auth_url2 = f'{base_url}/blocks'

        self.test_node_headers = {
            'URL': 'localhost:5000',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

    def tearDown(self):
        '''Wipes the test database after each test'''

        for collection in db.list_collection_names():
            db.drop_collection(collection)

    def test_nodes_access(self):
        '''Tests node access rules for /GET requests'''

        # A node can't authorize its self
        response = test_client.get(
            self.test_auth_url1, headers=self.test_node_headers)
        self.assertEqual(response.status_code, 401)
        response = test_client.get(
            self.test_auth_url2, headers=self.test_node_headers)
        self.assertEqual(response.status_code, 401)

        # A peer node must include a valid API_KEY in its request header
        # to be authenticated by another peer node.
        invalid_key_header = {
            'URL': 'localhost:5002',
            'API_KEY': 'invalid api_key',
            "Content-Type": "application/json"
        }

        response = test_client.get(
            self.test_auth_url1, headers=invalid_key_header)
        self.assertEqual(response.status_code, 401)
        response = test_client.get(
            self.test_auth_url2, headers=invalid_key_header)
        self.assertEqual(response.status_code, 401)

        # A peer node must include an API_KEY & it's url in it's request header
        no_key_header = {
            'URL': 'localhost:5002',
            "Content-Type": "application/json"
        }

        response = test_client.get(
            self.test_auth_url1, headers=no_key_header)
        self.assertEqual(response.status_code, 400)
        response = test_client.get(
            self.test_auth_url2, headers=no_key_header)
        self.assertEqual(response.status_code, 400)

        no_url_header = {
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        response = test_client.get(
            self.test_auth_url1, headers=no_url_header)
        self.assertEqual(response.status_code, 400)
        response = test_client.get(
            self.test_auth_url2, headers=no_url_header)
        self.assertEqual(response.status_code, 400)

        # Successful request
        correct_headers = {
            'URL': 'localhost:5002',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        response = test_client.get(
            self.test_auth_url1, headers=correct_headers)
        self.assertEqual(response.status_code, 200)

        response = test_client.get(
                self.test_auth_url2, headers=correct_headers)

        if init_node:
            # If not init_node, sync with init_node will fail as it is not live
            self.assertEqual(response.status_code, 403)
        else:
            # If init_node, the blockachain will be seeded
            self.assertEqual(response.status_code, 200)


class TestNodeRegistry(TestCase):

    def setUp(self):
        '''Setup before each test'''

        self.test_node_url = f'{base_url}/nodes'

    def tearDown(self):
        '''Wipes the test database after each test'''

        for collection in db.list_collection_names():
            db.drop_collection(collection)

    def test_node_states(self):
        '''Tests node registry states before and after /GET/nodes,
        when test node is the INIT_NODE'''

        # An authenticated node making a node registry request will
        # be registered automatically
        new_node_headers = {
            'URL': 'localhost:5002',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        # Node registry state before request
        self.assertEqual(db.nodes_collection.count_documents({}), 0)

        response = test_client.get(
            self.test_node_url, headers=new_node_headers)
        self.assertEqual(response.status_code, 200)

        res_payload = json.loads(response.data)['payload']

        if not init_node:
            # Only requesting node should be registered if test node
            # in init_node
            self.assertIn('localhost:5002', res_payload)
            self.assertEqual(len(res_payload), 1)
        else:
            # If test node is not the init_node, then the init_node +
            # the requesting node should be registered
            self.assertEqual(len(res_payload), 2)
            self.assertIn(init_node, res_payload)


class TestBlockChain(TestCase):

    def setUp(self):
        '''Setup before each test'''

        self.test_block_url = f'{base_url}/block'
        self.test_blockchain_url = f'{base_url}/blocks'

    def tearDown(self):
        '''Wipes the test database after each test'''

        for collection in db.list_collection_names():
            db.drop_collection(collection)

    def test_blockchain_states(self):
        '''Tests the blockchain states before and after /GET/blocks'''

        new_node_headers = {
            'URL': 'localhost:5002',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        # Blockchain should not have any blocks before request
        self.assertEqual(db.blocks_collection.count_documents({}), 0)

        response = test_client.get(
            self.test_blockchain_url, headers=new_node_headers)

        res_payload = json.loads(response.data)['payload']

        if not init_node:
            # Blockchain should only contain the seed block if test node
            # is not the init_node
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(res_payload), 1)
            self.assertIn('Seed Block', res_payload[0]['transaction'])
            self.assertEqual(res_payload[0]['index'], 1)
        else:
            # Non-init node should have no blocks as blockchain was already
            # seeded in init_node
            self.assertEqual(len(res_payload), 0)
            self.assertEqual(res_payload, [])

    def test_block_forging(self):
        '''Tests correct block forging on the /POST/block endpoint'''

        new_block = {
            "plot_number": "plt89567209",
            "size": "0.25 acres",
            "location": "Kangemi",
            "county": "Nairobi",
            "seller_id": 24647567,
            "buyer_id": 20466890,
            "amount": 1500000,
            "original_owner": "True"
        }

        '''Blocks can't be forged on unless there are atleast two peer
        nodes in the blockchain network.
        '''
        response = test_client.post(
            self.test_block_url,
            content_type='application/json',
            data=json.dumps(new_block)
        )

        self.assertEqual(response.status_code, 403)

        ''' A node with a registered peer node, can't forge a
        block unless it successfully sync with the registred peer.
        '''
        new_node_headers = {
            'URL': 'localhost:5002',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        # register a peer node
        response = test_client.get(
            f'{base_url}/nodes', headers=new_node_headers)

        self.assertEqual(response.status_code, 200)
        res_payload = json.loads(response.data)['payload']
        self.assertIn('localhost:5002', res_payload)

        # Attempt forging
        response = test_client.post(
            self.test_block_url,
            content_type='application/json',
            data=json.dumps(new_block)
        )

        self.assertEqual(response.status_code, 403)

        # Set up mock response from registered node to sync and allow
        # block forging
