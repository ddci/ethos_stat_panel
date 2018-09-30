import os

from celery import Celery
from flask import Flask
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from flask_assets import Environment
from flask_wtf import CSRFProtect
from flask_compress import Compress
from flask_rq import RQ
from flask_bcrypt import Bcrypt
from pymongo.errors import ServerSelectionTimeoutError
from flask_redis import FlaskRedis

from config import config

# from .assets import app_css, app_js, vendor_css, vendor_js

basedir = os.path.abspath(os.path.dirname(__file__))

mail = Mail()
db = SQLAlchemy()
csrf = CSRFProtect()
compress = Compress()
mongo = PyMongo()
bcrypt = Bcrypt()
redis_store = FlaskRedis()
celery = Celery()

# Set up Flask-Login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'account.login'


def create_app(config_name):
    if config_name == "development":
        print('THIS APP IS IN DEBUG MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.')
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # not using sqlalchemy event system, hence disabling it

    config[config_name].init_app(app)

    # Set up extensions
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    csrf.init_app(app)
    compress.init_app(app)
    redis_store.init_app(app, decode_responses=True)
    celery.config_from_object(app.config)
    celery.conf.ONCE = {
        'backend': 'celery_once.backends.Redis',
        'settings': {
            'url': config[config_name].CELERY_ONCE_BROKER_DB_URL,
            'default_timeout': 60 * 60
        }
    }

    # RQ(app)
    if not config_name == 'testing':
        try:
            mongo.init_app(app)
        except ServerSelectionTimeoutError as e:
            print("MongoDB Time Out")
            raise e
            pass
    bcrypt.init_app(app)

    # Register Jinja template functions
    from .utils import register_template_utils
    register_template_utils(app)

    # Set up asset pipeline
    # assets_env = Environment(app)
    # dirs = ['assets/styles', 'assets/scripts']
    # for path in dirs:
    #     assets_env.append_path(os.path.join(basedir, path))
    # assets_env.url_expire = True
    #
    # assets_env.register('app_css', app_css)
    # assets_env.register('app_js', app_js)
    # assets_env.register('vendor_css', vendor_css)
    # assets_env.register('vendor_js', vendor_js)

    # Configure SSL if platform supports it
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        SSLify(app)

    # Create app blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')

    from .account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')

    from .ajax_requests import ajax_requests as ajax_requests_blueprint
    app.register_blueprint(ajax_requests_blueprint, url_prefix='/ajax_requests')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .twilio_responses import twilio_responses as twilio_responses_blueprint
    app.register_blueprint(twilio_responses_blueprint, url_prefix='/twilio_responses')

    # from .admin import admin as admin_blueprint
    # app.register_blueprint(admin_blueprint, url_prefix='/admin')
    #
    # for name in find_modules('application'):
    #     mod = import_string(name)
    #     if hasattr(mod, 'bp'):
    #         app.register_blueprint(mod.bp)
    # return None
    return app
