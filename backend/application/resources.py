'''
This module contains the application blueprint and resources
'''

from flask import request, Blueprint
from flask_restful import Resource
from .controllers import SecurityController, NodeController, BlockController


# Initialize this module as a blueprint
app_bp = Blueprint('app_bp', __name__)

# TODO: Use actual atuhorization rather than passing key via headers


class BlockResource(Resource):
    ''' Manages a block resource '''

    def post(self):
        '''
        Exposes the unprotect block forging endpoint, internally to the
        frontend service -> json

        Input samples:
            {
                "plot_number":"plt89567209",
                "size": "0.25 acres",
                "location":"Kangemi",
                "county":"Nairobi",
                "seller_id":24647567,
                "buyer_id":20466890,
                "amount":1500000,
                "original_owner":"True"
            }
            {
                "plot_number":"plt344567209",
                "size": "0.5 acres",
                "location":"Kikuyu",
                "county":"Kiambu",
                "seller_id":18647567,
                "buyer_id":28976890,
                "amount":800000,
                "original_owner":"False"
            }
            {
                "plot_number":"plt624523479",
                "size": "1 acres",
                "location":"Othaya",
                "county":"Nyeri",
                "seller_id":20647534,
                "buyer_id":19976843,
                "amount":970000,
                "original_owner":"True"
            }
        '''

        values = request.get_json()

        required = ['plot_number', 'size', 'location', 'county',
                    'seller_id', 'buyer_id', 'amount', 'original_owner']

        if not all(k in values for k in required):
            return "Missing values", 400

        transaction = {
            'plot_number': values['plot_number'],
            'size': values['size'],
            'location': values['location'],
            'county': values['county'],
            'seller_id': values['seller_id'],
            'buyer_id': values['buyer_id'],
            'transfer_amount': values['amount'],
            'original_owner': values['original_owner'],
            'transfer_fee': {
                'sender': values['buyer_id'],
                'recipient': NodeController().node_id,
                'amount': 10000,
            }
        }

        forged_block = BlockController().create_block(
            transactions=transaction)

        message, status_code, payload = '', 0, []

        if forged_block is None:
            message = 'Transaction not recorded. Register atleast one \
                peer node to maintain blockchain integrity'
            status_code = 403
            payload = []

        else:
            message = 'Transaction recorded'
            status_code = 201
            payload = forged_block

        response = {
            'message': message,
            'payload': payload
        }

        return response, status_code


class BlockResources(Resource):
    ''' Manages block resources '''

    def get(self):
        ''' Exposes the protected get entire blockchain endpoint -> json '''

        # TODO:DO NOT AUTHORIZE YOURSELF

        if not SecurityController().authorize_node(request.headers['key']):
            message = 'Request from an unauthorized node'
            status_code = 401
            payload = None

        else:
            NodeController().register_node(request.headers['url'])

            result = BlockController().extract_chain()

            if isinstance(result, dict):
                message = 'Pending transactions'
                status_code = 403
                payload = result['error_nodes']

            else:
                message = 'Blockchain'
                status_code = 200
                payload = result

        response = {
            'message': message,
            'payload': payload
        }

        return response, status_code


class NodeResources(Resource):
    ''' Manages node resources '''

    def get(self):
        ''' Exposes the protected get all registered peer nodes endpoint
        -> json '''

        # TODO:DO NOT AUTHORIZE YOURSELF

        if not SecurityController().authorize_node(request.headers['key']):
            message = 'Request from an unauthorized node'
            status_code = 401
            payload = None

        else:
            NodeController().register_node(request.headers['url'])

            node_List = NodeController().extract_nodes()
            message = 'Registered_nodes'
            status_code = 200
            payload = node_List

        response = {
            'message': message,
            'payload': payload
        }

        return response, status_code
