'''This module tests the nodes resources'''

from flask import json
from unittest import TestCase
from ... import create_app
from ...plugins import mongo
from .test_configs import api_key, init_node


class TestNodeRegistry(TestCase):

    # Fetch the flask app to test
    app = create_app()

    def setUp(self):
        '''Setup before each test'''

        # Generate a test_client for the flask app
        self.test_client = TestNodeRegistry.app.test_client()

        # Fetch test_client configs
        self.db = mongo.db
        self.key = api_key

        # Generate the test_client request data
        self.test_node_url = 'http://localhost:5000/backend/v1/nodes'
        self.test_node_headers = {
            'URL': 'localhost:5000',
            'API_KEY': self.key,
            "Content-Type": "application/json"
        }

    def tearDown(self):
        '''Wipes the test database after each test'''

        for collection in self.db.list_collection_names():
            self.db.drop_collection(collection)

    def test_nodes_access(self):
        '''Tests node access rules for /GET/node request'''

        # A node can't authorize its self
        response = self.test_client.get(
            self.test_node_url, headers=self.test_node_headers)
        self.assertEqual(response.status_code, 401)

        # A peer node must include a valid API_KEY in its request header
        # to be authenticated by another peer node.
        invalid_key_header = {
            'URL': 'localhost:5001',
            'API_KEY': 'invalid api_key',
            "Content-Type": "application/json"
        }

        response = self.test_client.get(
            self.test_node_url, headers=invalid_key_header)
        self.assertEqual(response.status_code, 401)

        # A peer node must include an API_KEY & it's url in it's request header
        no_key_header = {
            'URL': 'localhost:5002',
            "Content-Type": "application/json"
        }

        response = self.test_client.get(
            self.test_node_url, headers=no_key_header)
        self.assertEqual(response.status_code, 400)

        no_url_header = {
            'API_KEY': self.key,
            "Content-Type": "application/json"
        }

        response = self.test_client.get(
            self.test_node_url, headers=no_url_header)
        self.assertEqual(response.status_code, 400)

        # Successful request
        correct_headers = {
            'URL': 'localhost:5001',
            'API_KEY': self.key,
            "Content-Type": "application/json"
        }

        response = self.test_client.get(
            self.test_node_url, headers=correct_headers)
        self.assertEqual(response.status_code, 200)

    def test_init_nodes_states(self):
        '''Tests node registry states after /GET/nodes and assumes test
        node is the INIT_NODE'''

        # An authenticated node making a node registry request will
        # be registered automatically
        new_node_headers = {
            'URL': 'localhost:5001',
            'API_KEY': self.key,
            "Content-Type": "application/json"
        }

        # Node registry state before request
        self.assertEqual(self.db.nodes_collection.count_documents({}), 0)

        response = self.test_client.get(
            self.test_node_url, headers=new_node_headers)
        self.assertEqual(response.status_code, 200)

        # Node registry state after request
        curr_obj = self.db.nodes_collection.find({}, {'_id': False})
        nodes_registered = [node['node_url'] for node in curr_obj]

        self.assertEqual(len(nodes_registered), 1)
        self.assertIn('localhost:5001', nodes_registered)

    def test_non_init_nodes_states(self):
        '''Tests node registry states after /GET/nodes and assumes test
        node is not the INIT_NODE'''

        new_node_headers = {
            'URL': 'localhost:5002',
            'API_KEY': self.key,
            "Content-Type": "application/json"
        }

        # Node registry before request
        self.assertEqual(self.db.nodes_collection.count_documents({}), 0)

        response = self.test_client.get(
            self.test_node_url, headers=new_node_headers)
        self.assertEqual(response.status_code, 200)

        # Node registry state after request, requesting node + init_node
        curr_obj = self.db.nodes_collection.find({}, {'_id': False})
        nodes_registered = [node['node_url'] for node in curr_obj]

        self.assertIn('localhost:5002', nodes_registered)

        if init_node:
            self.assertEqual(len(nodes_registered), 2)
            self.assertIn(init_node, nodes_registered)
