from datetime import datetime

from application import db
from application.main_logic.custom_logging import save_accessing, save_action
from application.main_logic.nav_info import HeaderNavbarInfo, SidebarInfo

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-10"
__app__ = "statswebapp"
__status__ = "Development"
#####
# IMPORTS
#####
from flask import flash, redirect, render_template, request, url_for, session
from flask_login import (current_user, login_required, login_user,
                         logout_user)

from . import account
from ..models import User
from .forms import (ChangeEmailForm, ChangePasswordForm, CreatePasswordForm,
                    LoginForm, RegistrationForm, RequestResetPasswordForm,
                    ResetPasswordForm)


@account.before_request
def before_request():
    save_accessing(current_user, request)
    session.permanent = True


@account.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('dashboard.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.password_hash is not None and \
                user.verify_password(form.password.data) \
                and user.verify_totp(form.token.data):
            login_user(user, form.remember_me.data)
            flash('You are now logged in. Welcome back!', 'success')
            save_action(current_user, request, " Successfully  authenticated")
            return redirect(request.args.get('next') or url_for('dashboard.index'))
        else:
            save_action(current_user, request, "Inserted wrong username or password")
            flash('Invalid username,password or token.', 'error')
            flash('Invalid username,password or token.', 'form-error')
    return render_template('account/login.html', form=form, header_nav_info=HeaderNavbarInfo(),
                           sidebar_info=SidebarInfo())


@account.route('/logout')
@login_required
def logout():
    logout_user()
    save_action(current_user, request, "Logged out")
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@account.route('/manage', methods=['GET', 'POST'])
@account.route('/manage/info', methods=['GET', 'POST'])
@login_required
def manage():
    """Display a user's account information."""
    return render_template('account/manage.html', user=current_user, form=None, header_nav_info=HeaderNavbarInfo(),
                           sidebar_info=SidebarInfo())


@account.route('/manage/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change an existing user's password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            flash('Your password has been updated.', 'form-success')
            save_action(current_user, request, "Changed Password")
            return redirect(url_for('main.index'))
        else:
            save_action(current_user, request, "Inserted wrong password while trying to change password")
            flash('Original password is invalid.', 'error')
            flash('Original password is invalid.', 'form-error')
    return render_template('account/change_password.html', form=form, user=current_user,
                           header_nav_info=HeaderNavbarInfo(),
                           sidebar_info=SidebarInfo())
