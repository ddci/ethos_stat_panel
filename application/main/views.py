from flask import render_template, request, redirect, url_for, session
from flask_login import current_user

from application.main_logic.custom_logging import save_accessing
from application.main_logic.nav_info import SidebarInfo, HeaderNavbarInfo
from . import main


@main.before_request
def before_request():
    save_accessing(current_user, request)
    session.permanent = True


@main.route('/')
def index():
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('dashboard.index'))
    return render_template('main/index.html', sidebar_info=SidebarInfo(), header_nav_info=HeaderNavbarInfo())
