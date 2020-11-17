'''This module contains the app resources'''

import json
from flask import request
from flask_restful import Resource
from .controllers import SecurityController, NodeController, BlockController


class NodeResources(Resource):
    '''Manages node resources'''

    def get(self):
        '''Exposes the protected get all registered peer nodes endpoint to
        other peer nodes -> json'''

        header = request.headers

        if 'Api-Key' not in header.keys() or 'Url' not in header.keys():

            message = 'Invalid Request'
            status_code = 400
            payload = None

        else:
            url = SecurityController().authorize_node(header)

            if not url:
                message = 'Unauthorized node'
                status_code = 401
                payload = None

            else:
                NodeController().register_node(url)

                node_List = NodeController().extract_nodes()
                message = 'Registered_nodes'
                status_code = 200
                payload = node_List

        response = {
            'message': message,
            'payload': payload
        }

        return response, status_code


class BlockResources(Resource):
    '''Manages block resources'''

    def get(self):
        '''Exposes the protected get entire blockchain endpoint to ther peer
        nodes -> json'''

        header = request.headers

        if 'Api-Key' not in header.keys() or 'Url' not in header.keys():

            message = 'Invalid Request'
            status_code = 400
            payload = None

        else:
            url = SecurityController().authorize_node(header)

            if not url:
                message = 'Unauthorized node'
                status_code = 401
                payload = None

            else:
                blocks = BlockController()
                NodeController().register_node(url)

                result = blocks.extract_chain()

                if result is None:
                    message = 'Chain not complete due to pending transactions'
                    status_code = 403
                    payload = []

                else:
                    message = 'Blockchain'
                    status_code = 200
                    payload = result

        response = {
            'message': message,
            'payload': payload
        }

        return response, status_code


class SystemResource(Resource):
    '''Manages sytem checks requests by the frontend'''

    def post(self):
        '''Initializes the backend'''

        BlockController()
        return {'message': 'Backend initialized'}, 201


class BlockResource(Resource):
    '''Manages a block resource'''

    def post(self):
        '''Exposes the backend transaction validation endpoint, internally
        to the frontend service -> json
        '''

        values = request.get_json()

        validation_data = {
            'plot_number': values['plot_number'],
            'seller_id': values['seller_id'],
            'buyer_id': values['buyer_id'],
        }

        result = BlockController().validate_transaction(validation_data)
        message, status_code, payload = '', 0, []

        if result:
            status_code = 400
            message = result
        else:
            status_code = 200
            message = 'transaction is unique'

        response = {
            'message': message,
            'payload': payload
        }

        return response, status_code


class BlockResourcesDemo(Resource):
    '''Demo block resources manager'''

    def get(self):
        '''Exposes the demo get entire blockchain endpoint -> json'''

        blocks = BlockController()
        result = blocks.extract_chain()

        if result is None:
            message = 'Chain not complete due to pending transactions'
            status_code = 403
            payload = []

        else:
            message = 'Blockchain'
            status_code = 200
            payload = result

        response = {
            'message': message,
            'payload': payload,
        }

        return response, status_code
