'''This module contains the app resources'''

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
                BlockController()   # Intializes Blockchain if first node
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

    # def post(self):
    #     '''
    #     Exposes the unprotected block forging endpoint, internally to the
    #     frontend service -> json

    #     Input samples:
    #         {
    #             "plot_number":"plt89567209",
    #             "size": "0.25 acres",
    #             "location":"Kangemi",
    #             "county":"Nairobi",
    #             "seller_id":24647567,
    #             "buyer_id":20466890,
    #             "amount":1500000,
    #             "original_owner":"True"
    #         }
    #         {
    #             "plot_number":"plt344567209",
    #             "size": "0.5 acres",
    #             "location":"Kikuyu",
    #             "county":"Kiambu",
    #             "seller_id":18647567,
    #             "buyer_id":28976890,
    #             "amount":800000,
    #             "original_owner":"False"
    #         }
    #         {
    #             "plot_number":"plt624523479",
    #             "size": "1 acres",
    #             "location":"Othaya",
    #             "county":"Nyeri",
    #             "seller_id":20647534,
    #             "buyer_id":19976843,
    #             "amount":970000,
    #             "original_owner":"True"
    #         }
    #     '''

    #     values = request.get_json()

    #     transaction = {
    #         'plot_number': values['plot_number'],
    #         'size': values['size'],
    #         'location': values['location'],
    #         'county': values['county'],
    #         'seller_id': values['seller_id'],
    #         'buyer_id': values['buyer_id'],
    #         'transfer_amount': values['amount'],
    #         'original_owner': values['original_owner'],
    #         'transfer_fee': {
    #             'sender': values['buyer_id'],
    #             'recipient': NodeController().node_id,
    #             'amount': 10000,
    #         }
    #     }

    #     result = BlockController().forge_block(
    #         transaction=transaction)

    #     message, status_code, payload = '', 0, []

    #     if 'sync_error' in result.keys():
    #         message = 'Sync Error'
    #         status_code = 403
    #         payload = result['sync_error']

    #     elif 'validation_error' in result.keys():
    #         message = 'Validation Error'
    #         status_code = 400
    #         payload = result['validation_error']

    #     else:
    #         message = 'Transaction recorded'
    #         status_code = 201
    #         payload = result

    #     response = {
    #         'message': message,
    #         'payload': payload
    #     }

    #     return response, status_code
