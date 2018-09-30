__author__ = 'Daniil Nikulin'
__copyright__ = "Copyright 2017"
__license__ = "Apache License 2.0"
__version__ = "1.0"
__maintainer__ = "Daniil Nikulin"
__email__ = "danil.nikulin@gmail.com"
__status__ = "Development"

from flask import Blueprint

account = Blueprint('account', __name__)

from . import views
