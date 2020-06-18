'''
The flask app is built here.
'''

from flask import Flask
from flask_restful import Api
from .plugins import mongo
from .application.resources import app_bp, BlockResource, BlockResources, NodeResources

def create_app(config_object='backend.configs'):
    '''
    This is the app factory where the app is initialized with its plugins
    and configs and all it's extensions (blueprints) recorded.
    '''

    # Initialize app with it's configurations
    app = Flask(__name__)

    # Add configs
    app.config.from_object(config_object)

    # Initialize plugins
    mongo.init_app(app)

    # Register all app components in the app context
    with app.app_context():
        # add resources
        api = Api(app_bp)
        api.add_resource(BlockResource, '/block')
        api.add_resource(BlockResources, '/blocks')
        api.add_resource(NodeResources, '/nodes')

        # Register app blueprints e.g app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(app_bp, url_prefix='/backend')

    return app