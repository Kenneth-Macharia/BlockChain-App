'''
This module is the app's entry apoint.

    Runing app:

        $ export INIT_NODE_IP=None
        $ export KEY=2c635640-c8c4-4f0d-8790-e6008d8eecce
        $ export DB_USER=root
        $ export DB_PASSWORD=password1
        $ export DB_HOST=localhost
        $ export FLASK_ENV=development
        $ flask run

        If entry point is called wsgi.py, then FLASK_APP is not neccessary.
        Use ".filename" to import modules
        Flask allow parallel processes on separate ports. Set ports:
        FLASK_RUN_PORT)

        host 0.0.0.0 allows the app to be accessed from outside its container.
'''

from . import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
