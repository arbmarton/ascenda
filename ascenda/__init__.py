import os

from flask import Flask
from flask import Blueprint
from werkzeug.routing import BaseConverter

from . import ascenda

# Used to separate variadic string args from the url
class ListConverter(BaseConverter):
    def to_python(self, value):
        return value.split('+')

def create_app(test_config = None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.url_map.converters['list'] = ListConverter

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(ascenda.bp)

    return app
