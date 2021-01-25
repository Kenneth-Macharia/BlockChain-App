'''This module contains the app resources'''

import json
from flask import request
from flask_restful import Resource
from .controllers import (SecurityController, NodeController,
                          BlockController, CacheController)
from ...configs import init_node, public_ip, port


class SystemResource(Resource):
    '''Manages sytem checks requests by the frontend'''

    def post(self):
        '''Updates both blockchainand node registry on hub initialization'''

        BlockController()
        blocks = BlockController()
        payload = 'Blockchain initialized'
        status = 201

        # if init_node:
        #     response = blocks.sync(update_chain=True)

        #     if response:
        #         payload = 'Backend sync error, contact IT!'
        #         status = 500

        return {'message': payload}, status


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
        '''Exposes the protected get entire blockchain endpoint to the peer
        network -> json'''

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

    def post(self):
        '''Exposes the protected update blockchain to the peer network -> json.

        To ensure the peer network keep the blockchain updated and in
        sync in realtime, a hub that forges a new block on its blockchain,
        will send it's updated blockchain to all peer hubs to validate
        and update their blockchains.
        '''

        header = request.headers
        data = request.get_json()

        if 'Api-Key' not in header.keys() or 'Url' not in header.keys():

            message = 'Invalid Request'
            status_code = 400

        else:
            security = SecurityController()
            url = security.authorize_node(header)

            if not url:
                message = 'Unauthorized node'
                status_code = 401

            else:
                blocks = BlockController()
                result = blocks.extract_chain()

                if len(data) > len(result) and \
                        security.validate_chain(data):
                    blocks.replace_blockchain(data)
                    CacheController().update_blockchain_cache(data[1:])

                    message = f'{public_ip}:{port} Updated'
                    status_code = 201

                else:
                    message = f'Error updating {public_ip}:{port}'
                    status_code = 500

        response = {
            'message': message,
        }

        return response, status_code


class BlockResource(Resource):
    '''Manages a block resource'''

    def post(self):
        '''Exposes the backend transaction validation endpoint, internally
        to the frontend service and ensures that invalid transactions are
        not recorded -> json
        '''

        values = request.get_json()
        validation_data = {
            'buyer_id': values['buyer_id'],
        }

        result = BlockController().validate_transaction(validation_data)
        message, status_code = '', 0

        if result:
            status_code = 400
            message = result
        else:
            status_code = 200

        return message, status_code


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
