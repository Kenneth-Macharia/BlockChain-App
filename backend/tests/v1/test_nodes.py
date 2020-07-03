''' This test module validates the nodes' intialized states on
    blockchain start-up.
 '''

import os
from flask import json
from unittest import TestCase
from ... import create_app
from ...plugins import mongo


class TestNodeRegistry(TestCase):

    def setUp(self):
        '''  Setup before each test '''

        self.app = create_app().test_client()
        self.db = mongo.db

        self.init_node = os.getenv('INIT_NODE_IP')

        VALID_API_KEY = '0f2372ebbfee3231a9ddf5db4bf505ddbc5ad6d \
            90c665e856baf224a8960cfa8'
        key = VALID_API_KEY.replace(' ', '')

        # Test node details
        self.test_node_url = 'http://localhost:5000/backend/v1/nodes'
        self.test_node_headers = {
            'URL': 'localhost:5000',
            'API_KEY': key,
            "Content-Type": "application/json"
        }

        # init node details
        self.init_node_header = {
            'URL': 'localhost:5001',
            'API_KEY': key,
            "Content-Type": "application/json"
        }

        # other node details
        self.other_node_header = {
            'URL': 'localhost:5002',
            'API_KEY': key,
            "Content-Type": "application/json"
        }

        # other node incorrect details
        self.other_node_wrong_header = {
            'URL': 'localhost:5003',
            'API_KEY': 'invalid api_key',
            "Content-Type": "application/json"
        }

    def tearDown(self):
        ''' Wipes the test database after each test '''

        for collection in self.db.list_collection_names():
            self.db.drop_collection(collection)

    def test_nodes(self):
        ''' Tests node states and interactions '''

        # A node can't authroize itself to make a nodes GET request
        response = self.app.get(
            self.test_node_url, headers=self.test_node_headers)
        self.assertEqual(response.status_code, 401)

        # A node without a valid API_KEY in it's GET request header
        # will not be authorized.
        response = self.app.get(
            self.test_node_url, headers=self.other_node_wrong_header)
        self.assertEqual(response.status_code, 401)
