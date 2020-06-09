'''
The flask app is built here.
'''

from flask import Flask
from .plugins import mongo
from .blockchain.blockchain import blockchain_bp


def create_app(config_object='backend.configs'):
    '''
    This is the app factory where the app is initialized with its plugins
    and configs and all it's extensions (blueprints) recorded.
    '''

    # Initialize app with it's configurations
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize plugins
    mongo.init_app(app)

    # Register all app components in the app context
    with app.app_context():

        # Register app blueprints e.g app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(blockchain_bp, url_prefix='/backend')

    return app