'''This module tests the nodes resources'''

import requests
from flask import json
from unittest import TestCase
from ...plugins import mongo
from .configs import api_key, init_node
from ... import create_app
from .mock_server import MockServer


# Set up globals
test_client = create_app().test_client()
base_url = 'http://localhost:5000/backend/v1'
mock_node_server = MockServer(5003)
db = mongo.db


class TestNodeAuth(TestCase):
    '''Tests inter-peer nodes authenticate to gain access to their data'''

    def setUp(self):
        '''Setup before each test'''

        self.test_auth_nodes = f'{base_url}/nodes'
        self.test_auth_blocks = f'{base_url}/blocks'

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
        '''Tests node access rules for /GET/nodes & /GET/blocks requests'''

        # A node can't authorize its self
        response = test_client.get(
            self.test_auth_nodes, headers=self.test_node_headers)
        self.assertEqual(response.status_code, 401)

        response = test_client.get(
            self.test_auth_blocks, headers=self.test_node_headers)
        self.assertEqual(response.status_code, 401)

        # A peer node must include a valid API_KEY in its request header
        # to be authenticated by another peer node.
        invalid_key_header = {
            'URL': 'localhost:5002',
            'API_KEY': 'invalid api_key',
            "Content-Type": "application/json"
        }

        response = test_client.get(
            self.test_auth_nodes, headers=invalid_key_header)
        self.assertEqual(response.status_code, 401)

        response = test_client.get(
            self.test_auth_blocks, headers=invalid_key_header)
        self.assertEqual(response.status_code, 401)

        # A peer node must include an API_KEY & it's url in it's request header
        no_key_header = {
            'URL': 'localhost:5002',
            "Content-Type": "application/json"
        }

        response = test_client.get(
            self.test_auth_nodes, headers=no_key_header)
        self.assertEqual(response.status_code, 400)

        response = test_client.get(
            self.test_auth_blocks, headers=no_key_header)
        self.assertEqual(response.status_code, 400)

        no_url_header = {
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        response = test_client.get(
            self.test_auth_nodes, headers=no_url_header)
        self.assertEqual(response.status_code, 400)

        response = test_client.get(
            self.test_auth_blocks, headers=no_url_header)
        self.assertEqual(response.status_code, 400)

        # Successful /GET request
        correct_headers = {
            'URL': 'localhost:5002',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        response = test_client.get(
            self.test_auth_nodes, headers=correct_headers)
        self.assertEqual(response.status_code, 200)

        response = test_client.get(
                self.test_auth_blocks, headers=correct_headers)
        self.assertEqual(response.status_code, 200)


class TestNodeRegistry(TestCase):
    '''Tests inter-peer node registration. Nodes automatically
    register authenitcated nodes that make /GET request for node
    or block resources'''

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
    '''Tests block forging and blockchain auto sync with other peer nodes'''

    def setUp(self):
        '''Setup before each test'''

        # set up test endpoints
        self.test_block_url = f'{base_url}/block'
        self.test_blockchain_url = f'{base_url}/blocks'

        self.new_block = {
            "plot_number": "plt89567209",
            "size": "0.25 acres",
            "location": "Kangemi",
            "county": "Nairobi",
            "seller_id": 24647567,
            "buyer_id": 20466890,
            "amount": 1500000,
            "original_owner": "True"
        }

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
            # Blockchain should only contain the seed block if test client
            # is the init_node
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(res_payload), 1)
            self.assertIn('seed_block', res_payload[0]['transaction'])
            self.assertEqual(res_payload[0]['index'], 1)
        else:
            # Non-init node should have no blocks as blockchain was already
            # seeded in init_node
            self.assertEqual(len(res_payload), 0)
            self.assertEqual(res_payload, [])

    def test_block_forging_no_sync(self):
        '''Tests failed block forging on the /POST/block endpoint'''

        '''Blocks can't be forged on unless there are atleast two peer
        nodes in the blockchain network.
        '''
        response = test_client.post(
            self.test_block_url,
            content_type='application/json',
            data=json.dumps(self.new_block)
        )

        self.assertEqual(response.status_code, 403)

        ''' A node with a registered peer node, can't forge a
        block unless it successfully syncs with the registred peer.
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

        # Block forging on test client fails because it cannot sync with
        # the newly registered node 'localhost:5002' as it is not live.
        response = test_client.post(
            self.test_block_url,
            content_type='application/json',
            data=json.dumps(self.new_block)
        )

        self.assertEqual(response.status_code, 403)

    def test_block_forging_with_sync(self):
        '''Tests successful block forging on the /POST/block endpoint'''

        # Start mock server: localhost:5003
        mock_node_server.start()

        # Register mock node with test client (simulate a request sent from
        # mock node to auto register it on test client localhost:5000)
        mock_node_headers = {
            'URL': 'localhost:5003',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        response = test_client.get(
            f'{base_url}/nodes', headers=mock_node_headers)

        self.assertEqual(response.status_code, 200)
        res_payload = json.loads(response.data)['payload']
        self.assertIn('localhost:5003', res_payload)

        '''For test client to be able to forge a new block, it
        must be able to sync its node registry and blockchain with
        the registered mock node'''

        # Add desired response from mock server for /GET/nodes
        nodes_response_payload = {
            "message": "Registered_nodes",
            "payload": ['localhost:5000']
        }
        mock_node_server.add_json_response(
            '/backend/v1/nodes', nodes_response_payload)

        # Add desired blockchain response from mock server for /GET/blocks
        blocks_response_payload = {
            "message": "Blockchain",
            "payload": []
        }
        mock_node_server.add_json_response(
            '/backend/v1/blocks', blocks_response_payload)

        # Forge new block on test client
        response = test_client.post(
            self.test_block_url,
            content_type='application/json',
            data=json.dumps(self.new_block)
        )

        if init_node:
            #  If test client or mock server is no the init node,
            # block forging on test client should fail because the
            # init node is not live thus not reacheable for sync
            self.assertEqual(response.status_code, 403)

        else:
            # If either mock server or test client is the init node then
            # sync will be successfull as both are live.

            self.assertEqual(response.status_code, 201)
            res_payload = json.loads(response.data)['payload']
            self.assertIn('plt89567209', res_payload['transaction']
                          ['plot_number'])
            self.assertEqual(20466890, res_payload['transaction']
                             ['transfer_fee']['sender'])

            # Test forging of duplicate blocks is not possible
            response = test_client.post(
                self.test_block_url, content_type='application/json',
                data=json.dumps(self.new_block))

            self.assertEqual(response.status_code, 400)
            res_payload = json.loads(response.data)['payload']
            self.assertIn('Transaction already exist', res_payload)

        # Shut down mock server
        mock_node_server.shutdown_server()
