#!/usr/bin/python3
"""
API module
"""

from flask import Flask, Blueprint, jsonify
from os import getenv
from models import storage
from api.v1.views import app_views
from flask_cors import CORS


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})  # Allow CORS for 0.0.0.0


@app.teardown_appcontext
def teardown_appcontext(error):
    """Closes the database"""
    storage.close()


if __name__ == '__main__':
    host = getenv('HBNB_API_HOST', '0.0.0.0')
    port = getenv('HBNB_API_PORT', '5000')
    app.run(host=host, port=port, threaded=True)
