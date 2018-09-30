__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-16"
__app__ = "statswebapp"
__status__ = "Development"

from flask import Blueprint

ajax_requests = Blueprint('ajax_requests', __name__)

from . import views
