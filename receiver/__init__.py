import logging

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-18"
__app__ = "mdbreceiver"
__status__ = "Development"

import os
from flask import Flask
from pymongo.errors import ServerSelectionTimeoutError
from flask_pymongo import PyMongo
from config import config

basedir = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)
logging.info("Starting web server:")

mongo = PyMongo()


def create_app(config_name):
    print('Creating Receiver')
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)


    # Set up extensions
    if not config_name == 'testing':
        try:
            mongo.init_app(app)
        except ServerSelectionTimeoutError as e:
            print("MongoDB Time Out")
            raise e
            pass
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        SSLify(app)

    # Create app blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
