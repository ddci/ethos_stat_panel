from application.main_logic.ajax_responses import get_status_panel_ajax
from application.main_logic.custom_logging import save_action
from application.main_logic.functions import is_panel_exist
from application.main_logic.nav_info import HeaderNavbarInfo
from application.models import LocationFieldPanel

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-10"
__app__ = "statswebapp"
__status__ = "Development"
from flask import flash, redirect, render_template, request, url_for, abort, jsonify
from flask_login import (current_user, login_required, login_user,
                         logout_user)

from . import ajax_requests
from application import db


@login_required
@ajax_requests.route('/status_table/<string:pool_name>', methods=['GET'])
def status_table(pool_name):
    """Log in an existing user."""
    if not is_panel_exist(panel_name=pool_name):
        abort(404)
    else:
        response = get_status_panel_ajax(pool_name)

        return jsonify(response)


@login_required
@ajax_requests.route('/change_location', methods=['POST', 'GET'])
def change_location():
    """Save location"""
    try:
        hostname = str(request.form.get('hostname'))
        location = str(request.form.get('location'))
        loc = LocationFieldPanel(
            hostname=hostname,
            number=location
        )
        if LocationFieldPanel.query.filter_by(hostname=hostname).first() is None \
                and LocationFieldPanel.query.filter_by(number=location).first() is None:
            # session.query(User).filter_by(id=123).update({"name": u"Bob Marley"})
            db.session.add(loc)
            db.session.commit()
            save_action(current_user, request, "Added location: {} for rig: {} ".format(loc.number, loc.hostname))
        else:
            loc = LocationFieldPanel.query.filter_by(hostname=hostname).first()
            if LocationFieldPanel.query.filter_by(number=location).first() is None:
                loc.hostname = hostname
                loc.number = location
                db.session.add(loc)
                db.session.commit()
                save_action(current_user, request, "Added location: {} for rig: {} ".format(loc.number, loc.hostname))
            else:
                loc = LocationFieldPanel.query.filter_by(number=location).first()
                loc.hostname = hostname
                loc.number = location
                db.session.add(loc)
                db.session.commit()
                save_action(current_user, request, "Changed location: {} for rig: {} ".format(loc.number, loc.hostname))
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(500)
        save_action(current_user, request, "Failed to add/change location")
        raise

    return "200"
