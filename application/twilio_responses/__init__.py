from application import csrf

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-02-21"
__app__ = "statswebapp"
__status__ = "Development"


from flask import Blueprint

twilio_responses = Blueprint('twilio_responses', __name__)
csrf.exempt(twilio_responses)

from . import views


