''' This test module validates the nodes' intialized states on
    blockchain start-up.
 '''

from flask import json
from unittest import TestCase
from ... import create_app
from ...plugins import mongo


class TestNodeRegistry(TestCase):

    def setUp(self):
        '''  Setup before each test '''

        self.app = create_app().test_client()
        self.db = mongo.db

        # Clear same db used locally for dev and testing
        # for collection in self.db.list_collection_names():
        #     self.db.drop_collection(collection)

        VALID_API_KEY = '0f2372ebbfee3231a9ddf5db4bf505ddbc5ad6d \
            90c665e856baf224a8960cfa8'
        self.key = VALID_API_KEY.replace(' ', '')

        # Test node details
        self.test_node_url = 'http://localhost:5000/backend/v1/nodes'

        self.test_node_headers = {
            'URL': 'localhost:5000',
            'API_KEY': self.key,
            "Content-Type": "application/json"
        }

    def tearDown(self):
        ''' Wipes the test database after each test '''

        for collection in self.db.list_collection_names():
            self.db.drop_collection(collection)

    def test_nodes_get(self):
        ''' Tests /GET/nodes requests among peer nodes '''

        # A node can't authorize its self
        response = self.app.get(
            self.test_node_url, headers=self.test_node_headers)
        self.assertEqual(response.status_code, 401)

        # A peer node must include a valid API_KEY in its request header
        # to be authenticated by another peer node.
        invalid_key_header = {
            'URL': 'localhost:5001',
            'API_KEY': 'invalid api_key',
            "Content-Type": "application/json"
        }

        response = self.app.get(
            self.test_node_url, headers=invalid_key_header)
        self.assertEqual(response.status_code, 401)

        # A peer node must include an API_KEY & it's url in it's request header
        no_key_header = {
            'URL': 'localhost:5002',
            "Content-Type": "application/json"
        }

        response = self.app.get(
            self.test_node_url, headers=no_key_header)
        self.assertEqual(response.status_code, 400)

        no_url_header = {
            'API_KEY': self.key,
            "Content-Type": "application/json"
        }

        response = self.app.get(
            self.test_node_url, headers=no_url_header)
        self.assertEqual(response.status_code, 400)
