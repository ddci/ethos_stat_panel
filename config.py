import datetime
import os
import sys

# from raygun4py.middleware import flask as flask_raygun

PYTHON_VERSION = sys.version_info[0]
if PYTHON_VERSION == 3:
    import urllib.parse
else:
    import urlparse

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('config.env'):
    print('Importing environment from .env file')
    for line in open('config.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[str(var[0])] = str(var[1].replace("\"", ""))


class Config:
    APP_NAME = os.environ.get('APP_NAME') or 'statswebapp'

    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME') or 'http'

    # SERVER_NAME = os.environ.get('SERVER_NAME') or ''

    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'password'

    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=30)
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)

    # REDIS_HOST = os.getenv('REDIS_HOST') or 'localhost'
    # REDIS_PORT = os.getenv('REDIS_PORT') or '6379'
    # REDIS_DB = os.getenv('REDIS_DB') or '1'

    REDIS_URL = os.environ.get("REDIS_URL")

    # MONGO CONNECTION
    MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
    MONGO_HOST = os.environ.get("MONGO_HOST")
    MONGO_PORT = os.environ.get("MONGO_PORT") or "27017"
    MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
    MONGO_AUTH_MECHANISM = os.environ.get('MONGO_AUTH_MECHANISM')
    MONGO_CONNECT = bool(os.environ.get('MONGO_CONNECT'))
    # MONGO_CONNECT = False

    # CELERY CONNECTION
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    CELERYD_TASK_SOFT_TIME_LIMIT = os.environ.get("CELERYD_TASK_SOFT_TIME_LIMIT")
    CELERYD_TASK_TIME_LIMIT = os.environ.get("CELERYD_TASK_TIME_LIMIT")

    CELERY_ONCE_BROKER_DB_URL = os.environ.get("CELERY_ONCE_BROKER_DB_URL")
    # ONLY DEBUG MODE
    # CELERY_ALWAYS_EAGER = True
    # CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

    # MAIN APP SETTINGS
    APP_SETTINGS_PERIOD_TO_LIVE = os.environ.get('APP_SETTINGS_PERIOD_TO_LIVE') or '10'
    APP_SETTINGS_PERIOD_TO_HIDE_RIG = os.environ.get('APP_SETTINGS_PERIOD_TO_HIDE_RIG') or '5'
    APP_SETTINGS_PERIOD_TO_HIDE_PANEL = os.environ.get('APP_SETTINGS_PERIOD_TO_HIDE_PANEL') or '10'
    APP_RX_BAD_VALUE = float(os.environ.get('APP_RX_BAD_VALUE')) or 2.0
    APP_TX_BAD_VALUE = float(os.environ.get('APP_TX_BAD_VALUE')) or 2.0

    # TWILIO  AUTH
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER_SERVER = os.environ.get('TWILIO_PHONE_NUMBER_SERVER')

    TWILIO_PHONE_NUMBER_1 = os.environ.get('TWILIO_PHONE_NUMBER_1')
    TWILIO_PHONE_NUMBER_2 = os.environ.get('TWILIO_PHONE_NUMBER_2')
    TWILIO_PHONE_NUMBER_3 = os.environ.get('TWILIO_PHONE_NUMBER_3')
    TWILIO_PHONE_NUMBER_4 = os.environ.get('TWILIO_PHONE_NUMBER_4')
    TWILIO_PHONE_NUMBER_5 = os.environ.get('TWILIO_PHONE_NUMBER_5')

    # APP_SETTINGS_OVERHEAT = os.environ.get('APP_SETTINGS_OVERHEAT') or '85'
    # APP_GPU_CRASHED_MEM_VALUE_MAX = os.environ.get('APP_GPU_CRASHED_MEM_VALUE_MAX') or '2200'
    # APP_GPU_CRASHED_MEM_VALUE_MIN = os.environ.get('APP_GPU_CRASHED_MEM_VALUE_MIN') or '1000'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SSL_DISABLE = (os.environ.get('SSL_DISABLE') or 'True') == 'True'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY IS NOT SET!'

        # flask_raygun.Provider(app, app.config['RAYGUN_APIKEY']).attach()


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'unix': UnixConfig
}
