'''
This module is the app's entry apoint
'''

from . import create_app

app = create_app()

if __name__ == "__main__":
    app.run()

'''
    Runing app:

        $ FLASK_ENV=development python wsgi.py
            (use 'filename' to import modules)

            or

        $ export DB_USER=root
        $ export DB_PASSWORD=password1
        $ export DB_HOST=localhost
        $ export FLASK_ENV=development
        $ flask run

            (If entry point is called wsgi.py, then FLASK_APP is not neccessary)
            (use '.filename' to import modules)
            (Allows parallel processes on separate ports. Set ports: FLASK_RUN_PORT)

        (NB) host 0.0.0.0 allows the app to be accessed from outside it's container
'''
