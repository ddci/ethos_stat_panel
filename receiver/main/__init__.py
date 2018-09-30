__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-18"
__app__ = "mdbreceiver"
__status__ = "Development"


from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
