'''This module tests the nodes resources'''

import requests
from flask import json
from unittest import TestCase
from ...plugins import mongo, redis_client
from .configs import api_key, init_node
from ... import create_app
from .mock_server import MockServer


# Set up globals
test_client = create_app().test_client()
base_url = 'http://localhost:5000/backend/v1'
db = mongo.db
mock_node_server1 = MockServer(5003)
mock_node_server2 = MockServer(5004)
new_transaction = {
    "plot_number": "plt89567209",
    "size": "0.25 acres",
    "location": "Kangemi",
    "county": "Nairobi",
    "seller_id": 24647567,
    "buyer_id": 20466890,
    "amount": 1500000,
    "original_owner": "True"
}


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

    def tearDown(self):
        '''Wipes the test database after each test'''

        redis_client.expire('records_cache', 0)

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
            data=json.dumps(new_transaction)
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
            data=json.dumps(new_transaction)
        )

        self.assertEqual(response.status_code, 403)

    def test_block_forging_with_sync(self):
        '''Tests successful block forging on the /POST/block endpoint'''

        # Start mock server1
        mock_node_server1.start()

        # Start mock server2
        mock_node_server2.start()

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
        mock_node_server1.add_json_response(
            '/backend/v1/nodes', nodes_response_payload)

        # Add desired blockchain response from mock server for /GET/blocks
        blocks_response_payload = {
            "message": "Blockchain",
            "payload": []
        }
        mock_node_server1.add_json_response(
            '/backend/v1/blocks', blocks_response_payload)

        # Forge new block on test client
        response = test_client.post(
            self.test_block_url,
            content_type='application/json',
            data=json.dumps(new_transaction)
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
                data=json.dumps(new_transaction))

            self.assertEqual(response.status_code, 400)
            res_payload = json.loads(response.data)['payload']
            self.assertIn('Transaction already exist', res_payload)

    # def test_block_forging_with_sync_data_replacement(self):
    #     '''Tests successful block forging on the /POST/block
    #     endpoint including updating of node registry and blockchain
    #     from peers'''

    #     # Fetch test client's node registry (also registers server1
    #     # with test client)
    #     server1_headers = {
    #         'URL': 'localhost:5003',
    #         'API_KEY': api_key,
    #         "Content-Type": "application/json"
    #     }

    #     response = test_client.get(
    #         f'{base_url}/nodes', headers=server1_headers)

    #     # Ensure test client only knows about server1 #
    #     self.assertEqual(response.status_code, 200)
    #     res_payload = json.loads(response.data)['payload']
    #     self.assertIn('localhost:5003', res_payload)
    #     self.assertNotIn('localhost:5004', res_payload)

    #     # Add server1 node registry response
    #     s1_nodes_response_payload = {
    #         "message": "Registered_nodes",
    #         "payload": ['localhost:5000', 'localhost:5003', 'localhost:5004']
    #     }
    #     mock_node_server1.add_json_response(
    #         '/backend/v1/nodes', s1_nodes_response_payload)

    #     # Add server1 blockchain response
    #     s1_blocks_response_payload = {
    #         "message": "Blockchain",
    #         "payload": [
    #             {
    #                 "index": 1,
    #                 "timestamp": 1602169193.1990635,
    #                 "transaction": [
    #                     "seed_block"
    #                 ],
    #                 "proof": 100,
    #                 "previous_hash": 10
    #             },
    #             {
    #                 "index": 2,
    #                 "timestamp": 1602169217.505347,
    #                 "transaction": {
    #                     "plot_number": "plt624523479",
    #                     "size": "1 acres",
    #                     "location": "Othaya",
    #                     "county": "Nyeri",
    #                     "seller_id": 20647534,
    #                     "buyer_id": 19976843,
    #                     "transfer_amount": 970000,
    #                     "original_owner": "True",
    #                     "transfer_fee": {
    #                         "sender": 19976843,
    #                         "recipient": "5769da5212f149cdaad5e63803700d8a",
    #                         "amount": 10000
    #                     }
    #                 },
    #                 "proof": 35293,
    #                 "previous_hash": "56e023e4050e119e57f887cc014cbcfd2613040e24d3fd2032c38beae2473e7f"
    #             }
    #         ]
    #     }
    #     mock_node_server1.add_json_response(
    #         '/backend/v1/blocks', s1_blocks_response_payload)

    #     # Add server2 node registry response
    #     s2_nodes_response_payload = {
    #         "message": "Registered_nodes",
    #         "payload": ['localhost:5003', 'localhost:5004']
    #     }
    #     mock_node_server2.add_json_response(
    #         '/backend/v1/nodes', s2_nodes_response_payload)

    #     # Add server2 blockchain response
    #     s2_blocks_response_payload = {
    #         "message": "Blockchain",
    #         "payload": []
    #     }
    #     mock_node_server2.add_json_response(
    #         '/backend/v1/blocks', s2_blocks_response_payload)

    #     # Forge new block on test client
    #     response = test_client.post(
    #         self.test_block_url,
    #         content_type='application/json',
    #         data=json.dumps(new_transaction)
    #     )

    #     # Ensure test client has 3 block (the one its forging above plus
    #     # the two from server2)
    #     if init_node:
    #         # Init node localhost:5001 can't be reached
    #         self.assertEqual(response.status_code, 403)
    #         res_payload_post = json.loads(response.data)['payload']
    #         self.assertIn(
    #             'Failed to connect to: localhost:5001',
    #             res_payload_post[0]['message'])

    #     else:
    #         # Succesfull block forging
    #         self.assertEqual(response.status_code, 201)
    #         res_payload_post = json.loads(response.data)['payload']
    #         self.assertIn('plt89567209',
    #                       res_payload_post['transaction']['plot_number'])

    #         # Ensure test client has registered server 2 as well
    #         # from server1's data during sync above #
    #         response = test_client.get(
    #             f'{base_url}/nodes', headers=server1_headers)

    #         res_payload_nodes = json.loads(response.data)['payload']

    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn('localhost:5004', res_payload_nodes)

    #         # Ensure test client's blockchain has been updated with
    #         # 3 the additional blocks from server2 #
    #         server1_headers = {
    #             'URL': 'localhost:5003',
    #             'API_KEY': api_key,
    #             "Content-Type": "application/json"
    #         }

    #         response = test_client.get(
    #             f'{base_url}/blocks', headers=server1_headers)

    #         res_payload_blocks = json.loads(response.data)['payload']

    #         self.assertEqual(3, len(res_payload_blocks))
    #         self.assertIn('seed_block', res_payload_blocks[0]['transaction'])
    #         self.assertIn('plt624523479', res_payload_blocks[1]
    #                       ['transaction']['plot_number'])
    #         self.assertIn('plt89567209', res_payload_blocks[2]
    #                       ['transaction']['plot_number'])


class TestRedisCache(TestCase):
    '''Tests Redis cache update on blockchain update'''

    def setUp(self):
        '''Setup before each test'''

        self.test_block_url = f'{base_url}/block'

    def tearDown(self):
        '''Wipes the test cache after each test'''

        # redis_client.expire('records_cache', 0)

        for collection in db.list_collection_names():
            db.drop_collection(collection)

    def test_cache_states(self):
        '''Test the state of the cache before and after blockchain updates'''

        # Ensure the cache is empty
        self.assertEqual(0, redis_client.hlen('records_cache'))

        # Forge a block
        mock_node_headers = {
            'URL': 'localhost:5003',
            'API_KEY': api_key,
            "Content-Type": "application/json"
        }
        response = test_client.get(
            f'{base_url}/nodes', headers=mock_node_headers)
        self.assertEqual(response.status_code, 200)

        nodes_response_payload = {
            "message": "Registered_nodes",
            "payload": ['localhost:5000']
        }
        mock_node_server1.add_json_response(
            '/backend/v1/nodes', nodes_response_payload)

        blocks_response_payload = {
            "message": "Blockchain",
            "payload": []
        }
        mock_node_server1.add_json_response(
            '/backend/v1/blocks', blocks_response_payload)

        response = test_client.post(
            self.test_block_url,
            content_type='application/json',
            data=json.dumps(new_transaction)
        )

        if not init_node:
            self.assertEqual(response.status_code, 201)

            # Confirm cache has been updated with the new blockchain
            self.assertEqual(1, redis_client.hlen('records_cache'))
            cached_record = json.loads(redis_client.hget('records_cache',
                                       new_transaction["plot_number"]))
            self.assertEqual(cached_record['current_owner'],
                             new_transaction['buyer_id'])

        # Shut down the mock servers
        mock_node_server1.shutdown_server()
        mock_node_server2.shutdown_server()
