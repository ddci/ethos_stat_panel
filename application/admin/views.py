import json

import pyqrcode as pyqrcode
from flask import abort, flash, redirect, render_template, url_for, request, session
from flask_login import current_user, login_required
from flask_paginate import get_page_parameter, Pagination
from io import BytesIO

from application.main_logic.admin_dashboard import AdminMainDashboard
from application.main_logic.custom_logging import save_accessing, save_action
from application.main_logic.nanopool_dash import NanopoolDashboardMain, NanopoolDashboardWallet, \
    is_nanopool_wallet_exists, NanopoolDashboardWalletPaymentsForDate
from application.main_logic.nav_info import HeaderNavbarInfo, SidebarInfo
from . import admin
from .forms import (ChangeAccountTypeForm, NewUserForm)
from .. import db, redis_store
from ..decorators import admin_required, supervisor_required
# from ..email import send_email
from ..models import Role, User

from application.celery_tasks.tasks import is_otp_seen_set


@admin.before_request
def before_request():
    save_accessing(current_user, request)
    session.permanent = True


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            username=form.username.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'form-success')
        save_action(current_user, request, "Added new user" + form.username.data + "with "
                    + form.role.data.name + " role.")
    return render_template('admin/new_user.html', form=form, sidebar_info=SidebarInfo(),
                           header_nav_info=HeaderNavbarInfo())


@admin.route('/dashboard_main', methods=['GET', 'POST'])
@login_required
@supervisor_required
def admin_dashboard():
    return render_template(
        'admin/admin_main_dashboard.html', sidebar_info=SidebarInfo(), admin_dash=AdminMainDashboard(),
        header_nav_info=HeaderNavbarInfo())


@admin.route('/nanopool_wallets_dash', methods=['GET'])
@login_required
@supervisor_required
def nanopool_wallets_dash():
    return render_template(
        'admin/nanopool_wallets.html', nano_pool_main=NanopoolDashboardMain(), sidebar_info=SidebarInfo(),
        header_nav_info=HeaderNavbarInfo())


@admin.route('/nanopool_wallet_info/<string:proxywallet>', methods=['GET'])
@login_required
@supervisor_required
def nanopool_wallet_info(proxywallet):
    if not is_nanopool_wallet_exists(proxywallet):
        abort(404)
    return render_template(
        'admin/nanopool_wallet_info.html', nanopool_wallet_info=NanopoolDashboardWallet(proxywallet=proxywallet),
        sidebar_info=SidebarInfo(),
        header_nav_info=HeaderNavbarInfo())


@admin.route('/nanopool_wallet_info/<string:proxywallet>/transactions_for_day/<string:date>', methods=['GET'])
@login_required
@supervisor_required
def transactions_for_day(proxywallet, date):
    json_str_all_payments = redis_store.get("nanopool_wallet_info:{}:all_payments"
                                            .format(str(proxywallet)))
    all_payments = json.loads(json_str_all_payments)
    if not is_nanopool_wallet_exists(proxywallet):
        abort(404)
    if date not in all_payments:
        abort(404)
    return render_template(
        'admin/nanopool_transactions_for_day.html',
        nanopool_wallet_info=NanopoolDashboardWalletPaymentsForDate(proxywallet=proxywallet, date=date),
        sidebar_info=SidebarInfo(),
        header_nav_info=HeaderNavbarInfo())


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles, sidebar_info=SidebarInfo(),
        header_nav_info=HeaderNavbarInfo())


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user, sidebar_info=SidebarInfo(),
                           header_nav_info=HeaderNavbarInfo())


@admin.route('/setup_two_factor/<int:user_id>')
@login_required
@admin_required
def two_factor_setup(user_id):
    """Setup two factor authentication"""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    if user.is_otp_seen:
        abort(403)
    is_otp_seen_set.apply_async(args=[user_id], expires=600, countdown=120)
    return render_template('admin/two_factor.html', user=user, sidebar_info=SidebarInfo(),
                           header_nav_info=HeaderNavbarInfo())


@admin.route('/qrcode/<string:user_id>')
@login_required
@admin_required
def qrcode(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    if user.is_otp_seen:
        abort(403)
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


# @admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def change_user_email(user_id):
#     """Change a user's email."""
#     user = User.query.filter_by(id=user_id).first()
#     if user is None:
#         abort(404)
#     form = ChangeUserEmailForm()
#     if form.validate_on_submit():
#         user.email = form.email.data
#         db.session.add(user)
#         db.session.commit()
#         flash('Email for user {} successfully changed to {}.'
#               .format(user.full_name(), user.email), 'form-success')
#     return render_template('admin/manage_user.html', user=user, form=form)
#
#

@admin.route(
    '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        save_action(current_user, request, "Tried to change Account type of Own Account.")
        return redirect(url_for('admin.user_info', user_id=user_id, sidebar_info=SidebarInfo(),
                                header_nav_info=HeaderNavbarInfo()))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'
              .format(user.full_name(), user.role.name), 'form-success')
        flash('Role for user {} successfully changed to {}.'
              .format(user.full_name(), user.role.name), 'success')
        save_action(current_user, request, 'Role for user {} successfully changed to {}.'
                    .format(user.full_name(), user.role.name))
    return render_template('admin/manage_user_change_account_type.html', user=user, form=form,
                           sidebar_info=SidebarInfo(),
                           header_nav_info=HeaderNavbarInfo())


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user_delete_user_request.html', user=user, sidebar_info=SidebarInfo(),
                           header_nav_info=HeaderNavbarInfo())


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
        save_action(current_user, request, "Tried to delete own account.")
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
        save_action(current_user, request, 'Successfully deleted user %s.' % user.full_name())
    return redirect(url_for('admin.registered_users'))


#
#
# @admin.route('/_update_editor_contents', methods=['POST'])
# @login_required
# @admin_required
# def update_editor_contents():
#     """Update the contents of an editor."""
#
#     edit_data = request.form.get('edit_data')
#     editor_name = request.form.get('editor_name')
#
#     editor_contents = EditableHTML.query.filter_by(
#         editor_name=editor_name).first()
#     if editor_contents is None:
#         editor_contents = EditableHTML(editor_name=editor_name)
#     editor_contents.value = edit_data
#
#     db.session.add(editor_contents)
#     db.session.commit()
#
#     return 'OK', 200


@admin.route('/log')
@login_required
@admin_required
def log_page():
    """View log"""
    try:
        search = False
        q = request.args.get('q')
        if q:
            search = True
        page = request.args.get(get_page_parameter(), type=int, default=1)
        rev = []
        length = 0
        log_text = ""
        with open("log/pow_log.txt", "r") as custom_log:
            lines = custom_log.readlines()
            lines.reverse()
            length = (len(lines) // 100) + 1
        if lines:
            for x, line in enumerate(lines):
                if page == 1:
                    if x <= 100:
                        log_text += line.replace('\n', '<br>')
                else:
                    line_a = (100 * (page - 1))
                    line_b = (page * 100)
                    if x >= line_a and x <= line_b:
                        log_text += line.replace('\n', '<br>')

        if length != 0:
            pagination = Pagination(page=page, total=length, search=search, record_name='Logging information',
                                    css_framework='foundation', per_page=1)

            return render_template('admin/log_page.html', log_text=log_text, sidebar_info=SidebarInfo(),
                                   header_nav_info=HeaderNavbarInfo(), pagination=pagination)
    except Exception as e:
        print(e)
        print("Exception occurred loading this page")

        return render_template('admin/log_page.html', sidebar_info=SidebarInfo(),
                               header_nav_info=HeaderNavbarInfo())
        pass
