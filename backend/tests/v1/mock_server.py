import requests
from uuid import uuid4
from flask import Flask, request, jsonify
from threading import Thread


class MockServer(Thread):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.app = Flask(__name__)
        self.url = f"http://localhost:{self.port}"
        self.app.add_url_rule("/shutdown", view_func=self._shutdown_server)

    def _shutdown_server(self):
        if 'werkzeug.server.shutdown' not in request.environ:
            raise RuntimeError('Not running the development server')
        request.environ['werkzeug.server.shutdown']()
        return 'Server shutting down...'

    def shutdown_server(self):
        requests.get(f"http://localhost:{self.port}/shutdown")
        self.join()

    def add_callback_response(self, url, callback, methods=('GET',)):
        callback.__name__ = str(uuid4())
        self.app.add_url_rule(url, view_func=callback, methods=methods)

    def add_json_response(self, url, serializable, methods=('GET',)):
        def callback():
            return jsonify(serializable)

        self.add_callback_response(url, callback, methods=methods)

    def run(self):
        self.app.run(port=self.port, debug=False)
