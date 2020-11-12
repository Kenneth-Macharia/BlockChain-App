'''This module contains a mock flask server to be used for testing peer
node communication'''

import requests
from uuid import uuid4
from flask import Flask, request, jsonify
from threading import Thread


class MockServer(Thread):
    '''The mock node server'''

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.app = Flask(__name__)
        self.url = f"http://localhost:{self.port}"
        self.app.add_url_rule("/shutdown", view_func=self._shutdown_server)

    def _shutdown_server(self):
        '''Shuts down the flask mock server'''

        if 'werkzeug.server.shutdown' not in request.environ:
            raise RuntimeError('Not running the development server')
        request.environ['werkzeug.server.shutdown']()
        return 'Server shutting down...'

    def shutdown_server(self):
        '''When called sends a request to the server to shut down'''

        requests.get(f"http://localhost:{self.port}/shutdown")
        self.join()

    def add_callback_response(self, url, callback, methods=('GET',)):
        '''Adds the url_rule for the desired endpoint to the server'''

        callback.__name__ = str(uuid4())
        self.app.add_url_rule(url, view_func=callback, methods=methods)

    def add_json_response(self, url, serializable, methods=('GET',)):
        '''When called adds an endpoint and corresponding response'''

        def callback():
            return jsonify(serializable)

        self.add_callback_response(url, callback, methods=methods)

    def run(self):
        '''Spins up the mock server'''

        self.app.run(port=self.port, debug=False)
