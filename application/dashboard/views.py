import ast

from flask import flash, redirect, render_template, request, url_for, g, abort, session

from application.dashboard.forms import ManagementRigsForm
from application.main_logic.custom_logging import save_accessing, save_action
from application.main_logic.technical_information import TechnicalInfoDashboard, is_bios_exist, BiosesRigDashboard
from application.main_logic.dashboards import MainDashboard, PanelDashboard
from application.main_logic.functions import is_panel_exist
from application.main_logic.heat_chart import HeatDashboard
from application.main_logic.nav_info import SidebarInfo, HeaderNavbarInfo
from application.models import User
from . import dashboard
from flask_login import login_required, current_user
from application.celery_tasks.tasks import execute_commands_on_multiple_rigs


@dashboard.before_request
def before_request():
    save_accessing(current_user, request)
    session.permanent = True


@dashboard.route('/', methods=['GET'])
@login_required
def index():
    return render_template('dashboard/dashboard_index.html', main_dash=MainDashboard(), sidebar_info=SidebarInfo(),
                           header_nav_info=HeaderNavbarInfo())


@dashboard.route('/panel/<string:panel_name>/', methods=['GET', 'POST'])
@login_required
def panel_dash(panel_name):
    form = ManagementRigsForm()
    if not is_panel_exist(panel_name=panel_name):
        abort(404)
    else:
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.password_hash is not None and \
                    user.verify_password(form.password.data):
                hosts = request.form.get('selectedHosts[]')
                hosts = ast.literal_eval(hosts)
                hosts = [n.strip() for n in hosts]
                commands = {'clear_thermals': form.clear_thermals.data, 'put_conf': form.put_conf.data,
                            'reboot': form.reboot_task.data, "update_miners": form.update_miners.data,
                            "allow_command": form.allow_command.data,
                            "update_miner_with_name": form.update_miner_with_name.data,
                            "change_password": form.change_password.data,
                            "execute_custom_command":form.execute_custom_command.data}

                # hostnames = request.form.get('selectedHostnames[]')
                if hosts and form.ssh_username.data and form.ssh_password.data \
                        and (
                        form.clear_thermals.data or form.put_conf.data
                        or form.reboot_task.data or form.update_miners.data
                        or form.allow_command.data or form.update_miner_with_name.data
                        or form.change_password.data or form.execute_custom_command.data):

                    results = execute_commands_on_multiple_rigs.apply_async(args=[],
                                                                            kwargs={"panel_name": panel_name,
                                                                                    "hosts": hosts,
                                                                                    "commands": commands,
                                                                                    "username": form.ssh_username.data,
                                                                                    "password":
                                                                                        form.ssh_password.data,
                                                                                    "miner_name": form.miner_name.data,
                                                                                    "new_password": form.new_password.data,
                                                                                    "custom_command": form.custom_command.data},
                                                                            expires=60)

                    # task = execute_rig_reboot.apply_async(args=[hosts[0], form.ssh_username.data,
                    # form.ssh_password.data])
                    flash('Commands have been sent to selected rigs.', 'success')
                    act_list = ([str(k) for k, v in commands.items() if v == True])
                    act_str = ""
                    if act_list:
                        for s in act_list:
                            act_str += " " + s

                    action = "Sent " + act_str + " to " + str(hosts)
                    save_action(current_user, request, action)
                else:
                    flash('No hosts selected,or ssh fields are empty.', 'error')
                return render_template('dashboard/dashboard_panel.html',
                                       panel_dash=PanelDashboard(panel_name), sidebar_info=SidebarInfo(),
                                       header_nav_info=HeaderNavbarInfo(), form=form)
                # return redirect(request.args.get('next') or url_for('dashboard.index'))
            else:
                flash('Invalid username or password.', 'form-error')
                flash('Invalid username or password.', 'error')
                return render_template('dashboard/dashboard_panel.html',
                                       panel_dash=PanelDashboard(panel_name), sidebar_info=SidebarInfo(),
                                       header_nav_info=HeaderNavbarInfo(), form=form)
        else:
            return render_template('dashboard/dashboard_panel.html',
                                   panel_dash=PanelDashboard(panel_name), sidebar_info=SidebarInfo(),
                                   header_nav_info=HeaderNavbarInfo(), form=form)


# @dashboard.route('/poll/ajax/<string:panel_name>/', methods=['GET'])
# @login_required
# def pool_dash_ajax(panel_name):
#     if not is_panel_exist(panel_name=panel_name):
#         abort(404)
#     else:
#         return render_template('dashboard/dashboard_pool_ajax.html',
#                                panel_dash=PanelDashboard(panel_name), sidebar_info=SidebarInfo(),
#                                header_nav_info=HeaderNavbarInfo())


@dashboard.route('/panel/<string:panel_name>/crashed_gpus', methods=['GET', 'POST'])
@login_required
def panel_dash_crashed_gpus(panel_name):
    form = ManagementRigsForm()
    if not is_panel_exist(panel_name=panel_name):
        abort(404)
    else:
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.password_hash is not None and \
                    user.verify_password(form.password.data):
                hosts = request.form.get('selectedHosts[]')
                hosts = ast.literal_eval(hosts)
                hosts = [n.strip() for n in hosts]
                commands = {'clear_thermals': form.clear_thermals.data, 'put_conf': form.put_conf.data,
                            'reboot': form.reboot_task.data, "update_miners": form.update_miners.data,
                            "allow_command": form.allow_command.data,
                            "update_miner_with_name": form.update_miner_with_name.data,
                            "change_password": form.change_password.data,
                            "execute_custom_command": form.execute_custom_command.data}

                # hostnames = request.form.get('selectedHostnames[]')
                if hosts and form.ssh_username.data and form.ssh_password.data \
                        and (
                        form.clear_thermals.data or form.put_conf.data
                        or form.reboot_task.data or form.update_miners.data
                        or form.allow_command.data or form.update_miner_with_name.data
                        or form.change_password.data or form.execute_custom_command.data):
                    results = execute_commands_on_multiple_rigs.apply_async(args=[],
                                                                            kwargs={"panel_name": panel_name,
                                                                                    "hosts": hosts,
                                                                                    "commands": commands,
                                                                                    "username": form.ssh_username.data,
                                                                                    "password":
                                                                                        form.ssh_password.data,
                                                                                    "miner_name": form.miner_name.data,
                                                                                    "new_password": form.new_password.data,
                                                                                    "custom_command": form.custom_command.data},
                                                                            expires=60)

                    # task = execute_rig_reboot.apply_async(args=[hosts[0], form.ssh_username.data,
                    # form.ssh_password.data])
                    flash('Commands have been sent to selected rigs.', 'success')
                    act_list = ([str(k) for k, v in commands.items() if v == True])
                    act_str = ""
                    if act_list:
                        for s in act_list:
                            act_str += " " + s

                    action = "Sent " + act_str + " to " + str(hosts)
                    save_action(current_user, request, action)
                else:
                    flash('No hosts selected,or ssh fields are empty.', 'error')
                return render_template('dashboard/dashboard_panel.html',
                                       panel_dash=PanelDashboard(panel_name, crashed_gpus=True),
                                       sidebar_info=SidebarInfo(),
                                       header_nav_info=HeaderNavbarInfo(), form=form)
                # return redirect(request.args.get('next') or url_for('dashboard.index'))
            else:
                flash('Invalid username or password.', 'form-error')
                flash('Invalid username or password.', 'error')
                return render_template('dashboard/dashboard_panel.html',
                                       panel_dash=PanelDashboard(panel_name, crashed_gpus=True),
                                       sidebar_info=SidebarInfo(),
                                       header_nav_info=HeaderNavbarInfo(), form=form)
        else:
            return render_template('dashboard/dashboard_panel.html',
                                   panel_dash=PanelDashboard(panel_name, crashed_gpus=True), sidebar_info=SidebarInfo(),
                                   header_nav_info=HeaderNavbarInfo(), form=form)


@dashboard.route('/panel/<string:panel_name>/offline_rigs', methods=['GET', 'POST'])
@login_required
def panel_dash_offline_rigs(panel_name):
    form = ManagementRigsForm()
    if not is_panel_exist(panel_name=panel_name):
        abort(404)
    else:
        if form.validate_on_submit():

            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.password_hash is not None and \
                    user.verify_password(form.password.data):
                hosts = request.form.get('selectedHosts[]')
                hosts = ast.literal_eval(hosts)
                hosts = [n.strip() for n in hosts]
                commands = {'clear_thermals': form.clear_thermals.data, 'put_conf': form.put_conf.data,
                            'reboot': form.reboot_task.data, "update_miners": form.update_miners.data,
                            "allow_command": form.allow_command.data,
                            "update_miner_with_name": form.update_miner_with_name.data,
                            "change_password": form.change_password.data,
                            "execute_custom_command": form.execute_custom_command.data}

                # hostnames = request.form.get('selectedHostnames[]')
                if hosts and form.ssh_username.data and form.ssh_password.data \
                        and (
                        form.clear_thermals.data or form.put_conf.data
                        or form.reboot_task.data or form.update_miners.data
                        or form.allow_command.data or form.update_miner_with_name.data
                        or form.change_password.data or form.execute_custom_command.data):

                    results = execute_commands_on_multiple_rigs.apply_async(args=[],
                                                                            kwargs={"panel_name": panel_name,
                                                                                    "hosts": hosts,
                                                                                    "commands": commands,
                                                                                    "username": form.ssh_username.data,
                                                                                    "password":
                                                                                        form.ssh_password.data,
                                                                                    "miner_name": form.miner_name.data,
                                                                                    "new_password": form.new_password.data,
                                                                                    "custom_command": form.custom_command.data},
                                                                            expires=60)

                    # task = execute_rig_reboot.apply_async(args=[hosts[0], form.ssh_username.data,
                    # form.ssh_password.data])
                    flash('Commands have been sent to selected rigs.', 'success')
                    act_list = ([str(k) for k, v in commands.items() if v == True])
                    act_str = ""
                    if act_list:
                        for s in act_list:
                            act_str += " " + s

                    action = "Sent " + act_str + " to " + str(hosts)
                    save_action(current_user, request, action)
                else:
                    flash('No hosts selected,or ssh fields are empty.', 'error')
                return render_template('dashboard/dashboard_panel.html',
                                       panel_dash=PanelDashboard(panel_name, offline_rigs=True),
                                       sidebar_info=SidebarInfo(),
                                       header_nav_info=HeaderNavbarInfo(), form=form)
                # return redirect(request.args.get('next') or url_for('dashboard.index'))
            else:
                flash('Invalid username or password.', 'form-error')
                flash('Invalid username or password.', 'error')
                return render_template('dashboard/dashboard_panel.html',
                                       panel_dash=PanelDashboard(panel_name, offline_rigs=True),
                                       sidebar_info=SidebarInfo(),
                                       header_nav_info=HeaderNavbarInfo(), form=form)
        else:
            return render_template('dashboard/dashboard_panel.html',
                                   panel_dash=PanelDashboard(panel_name, offline_rigs=True), sidebar_info=SidebarInfo(),
                                   header_nav_info=HeaderNavbarInfo(), form=form)


@dashboard.route('/panel/<string:panel_name>/under_attack', methods=['GET', 'POST'])
@login_required
def panel_dash_under_attack_rigs(panel_name):
    form = ManagementRigsForm()
    if not is_panel_exist(panel_name=panel_name):
        abort(404)
    else:
        if form.validate_on_submit():

            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.password_hash is not None and \
                    user.verify_password(form.password.data):
                hosts = request.form.get('selectedHosts[]')
                hosts = ast.literal_eval(hosts)
                hosts = [n.strip() for n in hosts]
                commands = {'clear_thermals': form.clear_thermals.data, 'put_conf': form.put_conf.data,
                            'reboot': form.reboot_task.data, "update_miners": form.update_miners.data,
                            "allow_command": form.allow_command.data,
                            "update_miner_with_name": form.update_miner_with_name.data,
                            "change_password": form.change_password.data,
                            "execute_custom_command": form.execute_custom_command.data}

                # hostnames = request.form.get('selectedHostnames[]')
                if hosts and form.ssh_username.data and form.ssh_password.data \
                        and (
                        form.clear_thermals.data or form.put_conf.data
                        or form.reboot_task.data or form.update_miners.data
                        or form.allow_command.data or form.update_miner_with_name.data
                        or form.change_password.data or form.execute_custom_command.data):

                    results = execute_commands_on_multiple_rigs.apply_async(args=[],
                                                                            kwargs={"panel_name": panel_name,
                                                                                    "hosts": hosts,
                                                                                    "commands": commands,
                                                                                    "username": form.ssh_username.data,
                                                                                    "password":
                                                                                        form.ssh_password.data,
                                                                                    "miner_name": form.miner_name.data,
                                                                                    "new_password": form.new_password.data,
                                                                                    "custom_command": form.custom_command.data},
                                                                            expires=60)

                    # task = execute_rig_reboot.apply_async(args=[hosts[0], form.ssh_username.data,
                    # form.ssh_password.data])
                    flash('Commands have been sent to selected rigs.', 'success')
                    act_list = ([str(k) for k, v in commands.items() if v == True])
                    act_str = ""
                    if act_list:
                        for s in act_list:
                            act_str += " " + s

                    action = "Sent " + act_str + " to " + str(hosts)
                    save_action(current_user, request, action)
                else:
                    flash('No hosts selected,or ssh fields are empty.', 'error')
                return render_template('dashboard/dashboard_panel.html',
                                       panel_dash=PanelDashboard(panel_name, under_attack=True),
                                       sidebar_info=SidebarInfo(),
                                       header_nav_info=HeaderNavbarInfo(), form=form)
                # return redirect(request.args.get('next') or url_for('dashboard.index'))
            else:
                flash('Invalid username or password.', 'form-error')
                flash('Invalid username or password.', 'error')
                return render_template('dashboard/dashboard_panel.html',
                                       panel_dash=PanelDashboard(panel_name, under_attack=True),
                                       sidebar_info=SidebarInfo(),
                                       header_nav_info=HeaderNavbarInfo(), form=form)
        else:
            return render_template('dashboard/dashboard_panel.html',
                                   panel_dash=PanelDashboard(panel_name, under_attack=True), sidebar_info=SidebarInfo(),
                                   header_nav_info=HeaderNavbarInfo(), form=form)


@dashboard.route('/heat_chart', methods=['GET', 'POST'])
@login_required
def heat_chart():
    return render_template('dashboard/dashboard_heat_chart.html', heat_dash=HeatDashboard(),
                           sidebar_info=SidebarInfo(), header_nav_info=HeaderNavbarInfo())


@dashboard.route('/panel/<string:panel_name>/rig/<string:rig_name>', methods=['GET', 'POST'])
@login_required
def panel_dash_rig(panel_name, rig_name):
    form = ManagementRigsForm()
    if not is_panel_exist(panel_name=panel_name):
        abort(404)
    else:
        if form.validate_on_submit():

            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.password_hash is not None and \
                    user.verify_password(form.password.data):
                hosts = request.form.get('selectedHosts[]')
                hosts = ast.literal_eval(hosts)
                hosts = [n.strip() for n in hosts]
                commands = {'clear_thermals': form.clear_thermals.data, 'put_conf': form.put_conf.data,
                            'reboot': form.reboot_task.data, "update_miners": form.update_miners.data,
                            "allow_command": form.allow_command.data,
                            "update_miner_with_name": form.update_miner_with_name.data,
                            "change_password": form.change_password.data,
                            "execute_custom_command": form.execute_custom_command.data}

                # hostnames = request.form.get('selectedHostnames[]')
                if hosts and form.ssh_username.data and form.ssh_password.data \
                        and (
                        form.clear_thermals.data or form.put_conf.data
                        or form.reboot_task.data or form.update_miners.data
                        or form.allow_command.data or form.update_miner_with_name.data
                        or form.change_password.data or form.execute_custom_command.data):

                    results = execute_commands_on_multiple_rigs.apply_async(args=[],
                                                                            kwargs={"panel_name": panel_name,
                                                                                    "hosts": hosts,
                                                                                    "commands": commands,
                                                                                    "username": form.ssh_username.data,
                                                                                    "password":
                                                                                        form.ssh_password.data,
                                                                                    "miner_name": form.miner_name.data,
                                                                                    "new_password": form.new_password.data,
                                                                                    "custom_command": form.custom_command.data},
                                                                            expires=60)

                    # task = execute_rig_reboot.apply_async(args=[hosts[0], form.ssh_username.data,
                    # form.ssh_password.data])
                    flash('Commands have been sent to selected rigs.', 'success')
                    act_list = ([str(k) for k, v in commands.items() if v == True])
                    act_str = ""
                    if act_list:
                        for s in act_list:
                            act_str += " " + s

                    action = "Sent " + act_str + " to " + str(hosts)
                    save_action(current_user, request, action)
                else:
                    flash('No hosts selected,or ssh fields are empty.', 'error')
                return render_template('dashboard/dashboard_panel.html',
                                       panel_dash=PanelDashboard(panel_name, rig_name=rig_name),
                                       sidebar_info=SidebarInfo(),
                                       header_nav_info=HeaderNavbarInfo(), form=form)
                # return redirect(request.args.get('next') or url_for('dashboard.index'))
            else:
                flash('Invalid username or password.', 'form-error')
                flash('Invalid username or password.', 'error')
                return render_template('dashboard/dashboard_panel.html',
                                       panel_dash=PanelDashboard(panel_name, rig_name=rig_name),
                                       sidebar_info=SidebarInfo(),
                                       header_nav_info=HeaderNavbarInfo(), form=form)
        else:
            return render_template('dashboard/dashboard_panel.html',
                                   panel_dash=PanelDashboard(panel_name, rig_name=rig_name), sidebar_info=SidebarInfo(),
                                   header_nav_info=HeaderNavbarInfo(), form=form)


@dashboard.route('/technical_information', methods=['GET', 'POST'])
@login_required
def technical_information():
    return render_template('dashboard/dashboard_technical_info.html', tech_dash=TechnicalInfoDashboard(),
                           sidebar_info=SidebarInfo(), header_nav_info=HeaderNavbarInfo())


@dashboard.route('/technical_information/bioses/<string:bios_name>', methods=['GET', 'POST'])
@login_required
def bioses_rigs(bios_name):
    if not is_bios_exist(bios_name):
        abort(404)
    return render_template('dashboard/dashboard_technical_info.html', tech_dash=BiosesRigDashboard(bios_name),
                           sidebar_info=SidebarInfo(), header_nav_info=HeaderNavbarInfo())
