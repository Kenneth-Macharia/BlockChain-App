'''This module tests the nodes resources'''

import requests
from flask import json
from unittest import TestCase
from ...plugins import mongo, redis_client
from .configs import api_key, init_node
from ... import app
from .mock_server import MockServer


# -------- GLOBALS ---------
TEST_CLIENT = app.test_client()
DB = mongo.db
MOCK_NODE1 = MockServer(5001)
BASE_URL = 'http://localhost:5000/backend/v1'
NEW_TRANSACTION = {
    "plot_number": "plt89567209",
    "size": "0.25 acres",
    "location": "Kangemi",
    "county": "Nairobi",
    "seller_id": 24647567,
    "buyer_id": 20466890,
    "amount": 1500000,
    "original_owner": "True"
}


# ------ HELPER FUNCTIONS ------
def start_mockserver():
    MOCK_NODE1.start()


def stop_mockserver():
    MOCK_NODE1.shutdown_server()


def reset_test_datastores():
    # MongoDB
    for collection in DB.list_collection_names():
        DB.drop_collection(collection)

    # Redis
    redis_client.expire('records_cache', 0)


# ------- TEST CASES ----------
class TestNodeAuth(TestCase):
    '''Tests inter-peer nodes authenticate to gain access to their data'''

    def setUp(self):
        '''Setup before each test'''

        self.test_auth_nodes = f'{BASE_URL}/nodes'
        self.test_auth_blocks = f'{BASE_URL}/blocks'

        self.test_node_headers = {
            'URL': 'localhost:5000',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

    def tearDown(self):
        '''Wipes the test database after each test'''

        reset_test_datastores()

    def test_nodes_access(self):
        '''Tests node access rules for /GET/nodes & /GET/blocks requests'''

        # A node can't authorize its self
        response = TEST_CLIENT.get(
            self.test_auth_nodes, headers=self.test_node_headers)
        self.assertEqual(response.status_code, 401)

        response = TEST_CLIENT.get(
            self.test_auth_blocks, headers=self.test_node_headers)
        self.assertEqual(response.status_code, 401)

        # A peer node must include a valid API_KEY in its request header
        # to be authenticated by another peer node.
        invalid_key_header = {
            'URL': 'localhost:5002',
            'API_KEY': 'invalid api_key',
            "Content-Type": "application/json"
        }

        response = TEST_CLIENT.get(
            self.test_auth_nodes, headers=invalid_key_header)
        self.assertEqual(response.status_code, 401)

        response = TEST_CLIENT.get(
            self.test_auth_blocks, headers=invalid_key_header)
        self.assertEqual(response.status_code, 401)

        # A peer node must include an API_KEY & it's url in it's request header
        no_key_header = {
            'URL': 'localhost:5002',
            "Content-Type": "application/json"
        }

        response = TEST_CLIENT.get(
            self.test_auth_nodes, headers=no_key_header)
        self.assertEqual(response.status_code, 400)

        response = TEST_CLIENT.get(
            self.test_auth_blocks, headers=no_key_header)
        self.assertEqual(response.status_code, 400)

        no_url_header = {
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        response = TEST_CLIENT.get(
            self.test_auth_nodes, headers=no_url_header)
        self.assertEqual(response.status_code, 400)

        response = TEST_CLIENT.get(
            self.test_auth_blocks, headers=no_url_header)
        self.assertEqual(response.status_code, 400)

        # Successful /GET request
        correct_headers = {
            'URL': 'localhost:5002',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        response = TEST_CLIENT.get(
            self.test_auth_nodes, headers=correct_headers)
        self.assertEqual(response.status_code, 200)

        response = TEST_CLIENT.get(
                self.test_auth_blocks, headers=correct_headers)
        self.assertEqual(response.status_code, 200)


class TestNodeRegistry(TestCase):
    '''Tests inter-peer node registration. Nodes automatically
    register authenitcated nodes that make /GET request for node
    or block resources'''

    def setUp(self):
        '''Setup before each test'''

        self.test_node_url = f'{BASE_URL}/nodes'

    def tearDown(self):
        '''Wipes the test database after each test'''

        reset_test_datastores()

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
        self.assertEqual(DB.nodes_collection.count_documents({}), 0)

        response = TEST_CLIENT.get(
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
        self.test_block_url = f'{BASE_URL}/block'
        self.test_blockchain_url = f'{BASE_URL}/blocks'

    def tearDown(self):
        '''Wipes the test database after each test'''

        reset_test_datastores()

    def test_blockchain_states(self):
        '''Tests the blockchain states before and after /GET/blocks'''

        new_node_headers = {
            'URL': 'localhost:5002',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        # Blockchain should not have any blocks before request
        self.assertEqual(DB.blocks_collection.count_documents({}), 0)

        response = TEST_CLIENT.get(
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
        response = TEST_CLIENT.post(
            self.test_block_url,
            content_type='application/json',
            data=json.dumps(NEW_TRANSACTION)
        )

        # self.assertEqual(response.status_code, 403)

        ''' A node with a registered peer node, can't forge a
        block unless it successfully syncs with the registred peer.
        '''
        new_node_headers = {
            'URL': 'localhost:5002',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }

        # register a peer node
        response = TEST_CLIENT.get(
            f'{BASE_URL}/nodes', headers=new_node_headers)

        self.assertEqual(response.status_code, 200)
        res_payload = json.loads(response.data)['payload']
        self.assertIn('localhost:5002', res_payload)

        # Block forging on test client fails because it cannot sync with
        # the newly registered node 'localhost:5002' as it is not live.
        response = TEST_CLIENT.post(
            self.test_block_url,
            content_type='application/json',
            data=json.dumps(NEW_TRANSACTION)
        )

        # self.assertEqual(response.status_code, 403)

    def test_block_forging_with_sync_data_replacement(self):
        '''
        Tests successful block forging on the /POST/block
        endpoint including updating of node registry and blockchain
        from peers.

        Test scenario:
            INIT_NODE == Server1 (localhost:5003)
            test_client (localhost:5000)

            initial Server1 node registry => None
            initial Server1 => ['seed']

            test_client node registry => ['Server1']
            test_client blockchain => []

            Forge new_block on test_client
            test_client blockchain => ['seed', 'new_block']
        '''

        # Start Mock servers to enable nodes sync while block forging
        start_mockserver()

        if init_node:
            server1_headers = {
                'URL': 'localhost:5001',
                'API_KEY': api_key,
                "Content-Type": "application/json"
            }

            # test client's node registry
            response = TEST_CLIENT.get(
                f'{BASE_URL}/nodes', headers=server1_headers)

            self.assertEqual(response.status_code, 200)
            res_payload = json.loads(response.data)['payload']
            self.assertEqual(1, len(res_payload))
            self.assertIn('localhost:5001', res_payload)

            # test client's blockchain
            response = TEST_CLIENT.get(
                f'{BASE_URL}/blocks', headers=server1_headers)

            self.assertEqual(response.status_code, 200)
            res_payload = json.loads(response.data)['payload']
            self.assertEqual(0, len(res_payload))

            # Add server1 node registry response
            s1_nodes_response_payload = {
                "message": "Registered_nodes",
                "payload": []
            }
            MOCK_NODE1.add_json_response(
                    '/backend/v1/nodes', s1_nodes_response_payload)

            # Add server1 blockchain response
            s1_blocks_response_payload = {
                "message": "Blockchain",
                "payload": [
                    {
                        "index": 1,
                        "timestamp": 1602169193.1990635,
                        "transaction": [
                            "seed_block"
                        ],
                        "proof": 100,
                        "previous_hash": 10
                    }
                ]
            }
            MOCK_NODE1.add_json_response(
                '/backend/v1/blocks', s1_blocks_response_payload)

            # Forge new block on test client
            response = TEST_CLIENT.post(
                self.test_block_url,
                content_type='application/json',
                data=json.dumps(NEW_TRANSACTION)
            )

            # self.assertEqual(response.status_code, 201)

            # Test inclusion of 'seed block from server1 on sync + new block
            response = TEST_CLIENT.get(
                f'{BASE_URL}/blocks', headers=server1_headers)

            self.assertEqual(response.status_code, 200)
            res_blockchain = json.loads(response.data)['payload']
            # self.assertEqual(2, len(res_blockchain))
            # self.assertIn('seed_block', res_blockchain[0]['transaction'])
            # self.assertIn('plt89567209', res_blockchain[1]
                        #   ['transaction']['plot_number'])

            # Test forging of duplicate blocks is not possible
            response = TEST_CLIENT.post(
                self.test_block_url, content_type='application/json',
                data=json.dumps(NEW_TRANSACTION))

            # self.assertEqual(response.status_code, 400)
            res_payload = json.loads(response.data)['payload']
            # self.assertIn('Transaction already exist', res_payload)


class TestRedisCache(TestCase):
    '''Tests Redis cache update on blockchain update'''

    def setUp(self):
        '''Setup before each test'''

        self.test_block_url = f'{BASE_URL}/block'

    def tearDown(self):
        '''Wipes the test cache after each test'''

        stop_mockserver()
        reset_test_datastores()

    def test_cache_states(self):
        '''Test the state of the cache before and after blockchain updates'''

        # Ensure the cache is empty
        self.assertEqual(0, redis_client.hlen('records_cache'))

        # Forge a block
        mock_node_headers = {
            'URL': 'localhost:5001',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }
        response = TEST_CLIENT.get(
            f'{BASE_URL}/nodes', headers=mock_node_headers)
        self.assertEqual(response.status_code, 200)

        nodes_response_payload = {
            "message": "Registered_nodes",
            "payload": ['localhost:5000']
        }
        MOCK_NODE1.add_json_response(
            '/backend/v1/nodes', nodes_response_payload)

        blocks_response_payload = {
            "message": "Blockchain",
            "payload": []
        }
        MOCK_NODE1.add_json_response(
            '/backend/v1/blocks', blocks_response_payload)

        response = TEST_CLIENT.post(
            self.test_block_url,
            content_type='application/json',
            data=json.dumps(NEW_TRANSACTION)
        )

        # if not init_node:
        #     self.assertEqual(response.status_code, 201)

        #     Confirm cache has been updated with the new blockchain
        #     self.assertEqual(1, redis_client.hlen('records_cache'))
        #     cached_record = json.loads(redis_client.hget('records_cache',
        #                                NEW_TRANSACTION["plot_number"]))
        #     self.assertEqual(cached_record['current_owner'],
        #                      NEW_TRANSACTION['buyer_id'])
