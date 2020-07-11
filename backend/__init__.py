'''The flask app is built here'''

from flask import Flask
from flask_restful import Api
from .plugins import mongo
from . import configs
from .app.v1.blueprint import v1_bp
from .app.v1.resources import BlockResource, BlockResources, NodeResources


# Use the dev/testing or production configs
if configs.development:
    app_configs = 'backend.tests.v1.test_configs'
else:
    app_configs = 'backend.configs'


def create_app(config_object=app_configs):
    '''This is the app factory where the app is initialized with its plugins
    and configs and all it's extensions (blueprints) recorded'''

    # Initialize app with it's configurations
    app = Flask(__name__)

    # Add configs
    app.config.from_object(config_object)

    # Initialize plugins
    mongo.init_app(app)

    # Register all app components in the app context
    with app.app_context():

        # add resources
        api_v1 = Api(v1_bp)
        api_v1.add_resource(BlockResource, '/block')
        api_v1.add_resource(BlockResources, '/blocks')
        api_v1.add_resource(NodeResources, '/nodes')

        # Register app blueprints
        app.register_blueprint(v1_bp, url_prefix='/backend/v1')

    return app
