import datetime
import json
import random
import time

import copy
import flask_pymongo
import os
import paramiko
import requests
from celery.utils.log import get_task_logger

from application import celery, redis_store, mongo, db
from application.main_logic.admin_dashboard import get_unique_poll_info_list
from application.main_logic.nanopool_dash import dict_with_datetime_keys_to_str
from application.main_logic.technical_information import get_dict_of_bioses, get_list_of_bioses, \
    get_dict_of_rigs_for_bios, get_dict_of_drive_names, get_dict_of_ip_info_all, get_dict_of_ip_info
from application.main_logic.dashboards import get_num_of_gpus, get_num_of_alive_gpus, get_total_hashrate, \
    get_num_of_all_rigs, get_average_gpu_temperature, get_num_and_list_of_alive_panels, \
    get_num_of_alive_rigs, get_dual_miners_list, get_num_of_crashed_gpus
from application.main_logic.functions import curr_time_non_naive, curr_time_naive, days_hours_minutes
from application.main_logic.heat_chart import get_gpus_temp_info_dict
from application.main_logic.panel_info import get_list_of_hostnames_with_crashed_gpus, get_list_of_offline_rigs, \
    get_list_of_not_hidden_rigs, get_list_of_rigs_under_attack, get_num_of_rigs_under_attack
from application.main_logic.technical_information import get_dict_of_mobo

import pandas as pd

from application.models import User

logger = get_task_logger(__name__)


# @celery.task(bind=True)
# def long_task(self):
#     """Background task that runs a long function with progress reports."""
#     verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
#     adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
#     noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
#     message = ''
#     total = random.randint(10, 50)
#     for i in range(total):
#         if not message or random.random() < 0.25:
#             message = '{0} {1} {2}...'.format(random.choice(verb),
#                                               random.choice(adjective),
#                                               random.choice(noun))
#         self.update_state(state='PROGRESS',
#                           meta={'current': i, 'total': total,
#                                 'status': message})
#         time.sleep(1)
#     return {'current': 100, 'total': 100, 'status': 'Task completed!',
#             'result': 42}


# @celery.task
# def log(message):
#     """Print some log messages"""
#     logger.debug(message)
#     logger.info(message)
#     logger.warning(message)
#     logger.error(message)
#     logger.critical(message)


@celery.task
def main_dashboard_update():
    redis_store.set('main_dashboard:num_of_gpus', get_num_of_gpus())
    redis_store.set('main_dashboard:num_of_alive_gpus', get_num_of_alive_gpus())
    redis_store.set('main_dashboard:total_hashrate', get_total_hashrate())
    redis_store.set('main_dashboard:num_of_rigs', get_num_of_all_rigs())
    redis_store.set('main_dashboard:num_of_alive_rigs', get_num_of_alive_rigs())
    redis_store.set('main_dashboard:average_gpu_temperature', get_average_gpu_temperature())
    redis_store.set('main_dashboard:num_of_rigs_under_attack', get_num_of_rigs_under_attack())
    redis_store.set('main_dashboard:num_of_crashed_gpus', get_num_of_crashed_gpus())

    num_of_alive_panels, list_of_alive_panels = get_num_and_list_of_alive_panels()
    redis_store.delete('main_dashboard:list_of_alive_panels')  # IMPORTANT!!!!!!!
    if list_of_alive_panels:
        redis_store.lpush('main_dashboard:list_of_alive_panels', *list_of_alive_panels)
    redis_store.set('main_dashboard:num_of_alive_panels', num_of_alive_panels)


@celery.task
def panel_dashboards_update():
    alive_panels = get_num_and_list_of_alive_panels()[1]
    for panel_name in alive_panels:
        returnHashDict = {}
        returnHashDict['total_hashrate'] = str(get_total_hashrate(panel_name=panel_name))
        returnHashDict['num_of_gpus'] = str(get_num_of_gpus(panel_name=panel_name))
        returnHashDict['num_of_alive_gpus'] = str(get_num_of_alive_gpus(panel_name=panel_name))
        returnHashDict['num_of_crashed_gpus'] = str(get_num_of_crashed_gpus(panel_name=panel_name))
        returnHashDict['num_of_rigs'] = str(get_num_of_all_rigs(panel_name=panel_name))
        returnHashDict['num_of_alive_rigs'] = str(get_num_of_alive_rigs(panel_name=panel_name))
        returnHashDict['average_gpu_temperature'] = str(get_average_gpu_temperature(panel_name=panel_name))

        redis_store.delete("panel_dashboard:{}".format(str(panel_name)))
        if returnHashDict:
            redis_store.hmset("panel_dashboard:{}".format(str(panel_name)), returnHashDict)


@celery.task
def sidebar_info_update():
    num_of_rigs = {}
    num_of_alive_rigs = {}
    num_of_offline_gpus = {}
    list_of_alive_panels = get_num_and_list_of_alive_panels()[1]
    redis_store.delete('sidebar_info:list_of_alive_panels')  # IMPORTANT!!!!!!!
    if list_of_alive_panels:
        redis_store.lpush('sidebar_info:list_of_alive_panels', *list_of_alive_panels)
    all_coll_names = mongo.db.collection_names()
    for panel_name in all_coll_names:
        num_of_rigs[panel_name] = get_num_of_all_rigs(panel_name)
        num_of_alive_rigs[panel_name] = get_num_of_alive_rigs(panel_name)
        num_of_offline_gpus[panel_name] = get_num_of_crashed_gpus(panel_name)

    redis_store.delete("sidebar_info:num_of_rigs")
    if num_of_rigs:
        redis_store.hmset("sidebar_info:num_of_rigs", num_of_rigs)

    redis_store.delete("sidebar_info:num_of_alive_rigs")
    if num_of_alive_rigs:
        redis_store.hmset("sidebar_info:num_of_alive_rigs", num_of_alive_rigs)

    redis_store.delete("sidebar_info:num_of_offline_gpus")
    if num_of_offline_gpus:
        redis_store.hmset("sidebar_info:num_of_offline_gpus", num_of_offline_gpus)


@celery.task
def panels_info_update():
    alive_panels = get_num_and_list_of_alive_panels()[1]
    for panel_name in alive_panels:

        list_of_hosts_with_crashed_gpus = get_list_of_hostnames_with_crashed_gpus(panel_name)
        redis_store.delete('panel_info:{}:list_of_hosts_with_crashed_gpus'.format(str(panel_name)))
        if list_of_hosts_with_crashed_gpus:
            redis_store.lpush('panel_info:{}:list_of_hosts_with_crashed_gpus'.format(str(panel_name)),
                              *list_of_hosts_with_crashed_gpus)

        list_of_offline_rigs = get_list_of_offline_rigs(panel_name)
        redis_store.delete('panel_info:{}:list_of_offline_rigs'.format(str(panel_name)))
        if list_of_offline_rigs:
            redis_store.lpush('panel_info:{}:list_of_offline_rigs'.format(str(panel_name)), *list_of_offline_rigs)

        list_of_rigs_under_attack = get_list_of_rigs_under_attack(panel_name)
        redis_store.delete('panel_info:{}:list_of_rigs_under_attack'.format(str(panel_name)))
        if list_of_rigs_under_attack:
            redis_store.lpush('panel_info:{}:list_of_rigs_under_attack'.format(str(panel_name)),
                              *list_of_rigs_under_attack)

        alive_rigs = get_list_of_not_hidden_rigs(panel_name)
        redis_store.delete('panel_info:{}:alive_rigs'.format(str(panel_name)))
        if alive_rigs:
            redis_store.lpush('panel_info:{}:alive_rigs'.format(str(panel_name)), *alive_rigs)


@celery.task
def heat_chart_dashboard_update():
    gpu_temp_info_dict = get_gpus_temp_info_dict()
    redis_store.delete("heat_chart:all_temp_info_dict")
    if gpu_temp_info_dict:
        redis_store.hmset("heat_chart:all_temp_info_dict", get_gpus_temp_info_dict())

    alive_panels = get_num_and_list_of_alive_panels()[1]

    redis_store.delete('heat_chart:list_of_alive_panels')  # IMPORTANT!!!!!!!
    if alive_panels:
        redis_store.lpush('heat_chart:list_of_alive_panels', *alive_panels)

    for panel_name in alive_panels:
        gpus_temps_info_dict = get_gpus_temp_info_dict(str(panel_name))
        gpus_temps_info_dict['average_temp'] = get_average_gpu_temperature(panel_name=panel_name)
        gpus_temps_info_dict['num_of_gpus'] = get_num_of_gpus(panel_name=panel_name)
        gpus_temps_info_dict['num_of_alive_gpus'] = get_num_of_alive_gpus(panel_name=panel_name)
        gpus_temps_info_dict['num_of_rigs'] = get_num_of_all_rigs(panel_name=panel_name)
        gpus_temps_info_dict['num_of_alive_rigs'] = get_num_of_alive_rigs(panel_name=panel_name)

        redis_store.delete("heat_chart:{}:temp_info_dict".format(str(panel_name)))
        if gpus_temps_info_dict:
            redis_store.hmset("heat_chart:{}:temp_info_dict".format(str(panel_name)),
                              gpus_temps_info_dict)


@celery.task
def delete_old_data_from_mongodb(hours=None):
    if hours is None:
        hours = 25
    less_than_date = datetime.datetime.utcnow() - datetime.timedelta(hours=25)
    all_coll_names = mongo.db.collection_names()
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            collection.delete_one({"hostname": host, "received_at": {"$lt": less_than_date}})


@celery.task(bind=True, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=220)  # 5,10
def execute_rig_reboot(self, hostname, username, password):
    ssh_client = None
    try:
        print("TRYING TO REBOOT HOST {}".format(hostname))
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("TRYING TO CONNECT TO  HOST {}".format(hostname))
        ssh_client.connect(hostname=hostname, username=username, password=password, timeout=100)
        stdin, stdout, stderr = ssh_client.exec_command('r > /dev/null 2>&1 &')
        print("COMMAND 'r' was sent to {}".format(hostname))
        # print(stdout.readlines())
        # return stdout
    except Exception as e:
        print("Failed to execute commands on rig with ip {}".format(hostname))
        print(e)
    finally:
        if ssh_client:
            ssh_client.close()


@celery.task(bind=True, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=220)  # 5,10
def execute_rig_putconf_and_reboot(self, hostname, username, password):
    ssh_client = None
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("TRYING TO CONNECT TO  HOST {}".format(hostname))
        ssh_client.connect(hostname=hostname, username=username, password=password, timeout=100)
        print("TRYING TO EXECUTE PUTCONF ON HOST {}".format(hostname))
        stdin, stdout, stderr = ssh_client.exec_command('putconf')
        print(stdout.readlines())
        print("TRYING TO REBOOT HOST {}".format(hostname))
        stdin, stdout, stderr = ssh_client.exec_command('r > /dev/null 2>&1 &')
        print("COMMAND 'r' was sent to {}".format(hostname))
        # print(stdout.readlines())
        # return stdout
    except Exception as e:
        print("Failed to execute commands on rig with ip {}".format(hostname))
        print(e)
    finally:
        if ssh_client:
            ssh_client.close()


@celery.task(bind=True, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=220)  # 5,10
def execute_rig_clear_thermals_and_reboot(self, hostname, username, password):
    ssh_client = None
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("TRYING TO CONNECT TO  HOST {}".format(hostname))
        ssh_client.connect(hostname=hostname, username=username, password=password, timeout=100)
        print("TRYING TO REBOOT HOST {}".format(hostname))
        stdin, stdout, stderr = ssh_client.exec_command('clear-thermals')
        print(stdout.readlines())
        stdin, stdout, stderr = ssh_client.exec_command('r > /dev/null 2>&1 &')
        print("COMMAND 'r' was sent to {}".format(hostname))
        # print(stdout.readlines())
        # return stdout
    except Exception as e:
        print("Failed to execute commands on rig with ip {}".format(hostname))
        print(e)
    finally:
        if ssh_client:
            ssh_client.close()


@celery.task(bind=True, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=220)  # 5,10
def execute_rig_update_miners(self, hostname, username, password):
    ssh_client = None
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("TRYING TO CONNECT TO  HOST {}".format(hostname))
        ssh_client.connect(hostname=hostname, username=username, password=password, timeout=100)
        stdin, stdout, stderr = ssh_client.exec_command('sudo update-miners > /dev/null 2>&1')
        print("COMMAND UPDATE-MINERS".format(hostname))
        # print(stdout.readlines())
        # return stdout
    except Exception as e:
        print("Failed to execute commands on rig with ip {}".format(hostname))
        print(e)
    finally:
        if ssh_client:
            ssh_client.close()


@celery.task(bind=True, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=220)  # 5,10
def execute_rig_allow_command(self, hostname, username, password):
    ssh_client = None
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("TRYING TO CONNECT TO  HOST {}".format(hostname))
        ssh_client.connect(hostname=hostname, username=username, password=password, timeout=100)
        stdin, stdout, stderr = ssh_client.exec_command('allow > /dev/null 2>&1 &')
        print("COMMAND ALLOW TO {}".format(hostname))
        # print(stdout.readlines())
        # return stdout
    except Exception as e:
        print("Failed to execute commands on rig with ip {}".format(hostname))
        print(e)
    finally:
        if ssh_client:
            ssh_client.close()


@celery.task(bind=True, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=220)  # 5,10
def execute_rig_update_miner_with_name(self, hostname, username, password, miner_name):
    ssh_client = None
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("TRYING TO CONNECT TO  HOST {}".format(hostname))
        ssh_client.connect(hostname=hostname, username=username, password=password, timeout=100)
        stdin, stdout, stderr = ssh_client.exec_command('sudo update-miner {} > /dev/null 2>&1'.format(miner_name))
        print("COMMAND UPDATE-MINER {} ON HOST {}".format(miner_name, hostname))
        # print(stdout.readlines())
        # return stdout
    except Exception as e:
        print("Failed to execute commands on rig with ip {}".format(hostname))
        print(e)
    finally:
        if ssh_client:
            ssh_client.close()

@celery.task(bind=True, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=220)  # 5,10
def execute_custom_command(self, hostname, username, password, custom_command):
    ssh_client = None
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("TRYING TO CONNECT TO  HOST {}".format(hostname))
        ssh_client.connect(hostname=hostname, username=username, password=password, timeout=100)
        stdin, stdout, stderr = ssh_client.exec_command('{} > /dev/null 2>&1'.format(custom_command))
        print("CUSTOM COMMAND {} WAS SENT TO HOST {}".format(custom_command, hostname))
        # print(stdout.readlines())
        # return stdout
    except Exception as e:
        print("Failed to execute commands on rig with ip {}".format(hostname))
        print(e)
    finally:
        if ssh_client:
            ssh_client.close()

@celery.task(bind=True, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=300)  # 5,10
def execute_change_password(self, hostname, username, password, new_password):
    ssh_client = None
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("TRYING TO CONNECT TO  HOST {}".format(hostname))
        ssh_client.connect(hostname=hostname, username=username, password=password, timeout=100)
        print("TRYING TO CHANGE PASSWORD ON  HOST {}".format(hostname))
        stdin, stdout, stderr = ssh_client.exec_command('passwd')
        stdin.write(password + '\n')
        stdin.write(new_password + '\n')
        stdin.write(new_password + '\n')
        print((stdout.readlines()))
        print("PASSWORD CHANGED FOR HOST {}".format(hostname))

    except OSError as e:
        print("Seems like you have entered wrong password for host {}".format(hostname))
        print(e)

    except Exception as e:
        print("Failed to change password {}".format(hostname))
        print(e)
    finally:
        if ssh_client:
            ssh_client.close()


@celery.task(bind=True, expires=180, max_retries=0, soft_time_limit=480)
def execute_commands_on_multiple_rigs(self, panel_name=None, hosts=None, commands=None, username=None, password=None,
                                      miner_name=None, new_password=None, custom_command=None):
    all_coll_names = mongo.db.collection_names()
    ips_to_execute = {}
    if panel_name in all_coll_names:
        collection = mongo.db[panel_name]
        unique_hostnames = collection.find({}).distinct('hostname')
        for host in hosts:
            if host in unique_hostnames:
                cursor = collection.find({'hostname': str(host)}, {'ip': 1, 'received_at': 1}) \
                    .sort('received_at', flask_pymongo.DESCENDING) \
                    .limit(1)
                if cursor.count() > 0:
                    res = list(cursor)
                    dict_res = res[0]
                    ip = dict_res.get("ip")
                    received_at_utc = dict_res['received_at']
                    received_at_utc_local = curr_time_non_naive(received_at_utc)
                    now_local = curr_time_naive(datetime.datetime.utcnow())
                    dif = now_local - received_at_utc_local
                    days, hours, minutes = days_hours_minutes(dif)
                    if days == 0 and hours == 0 and minutes <= 2:
                        ips_to_execute[host] = ip
        if ips_to_execute:
            executing_tasks = {}
            ips = 0
            for host in ips_to_execute:
                # REBOOT
                if commands.get("clear_thermals"):
                    task = execute_rig_clear_thermals_and_reboot.apply_async(
                        args=[ips_to_execute[host], username, password],
                        expire=240, queue="ssh_tasks")
                    # reboot = execute_rig_reboot.apply_async(countdown=5,
                    #                                         args=[ips_to_execute[host], username, password],
                    #                                         expire=60)
                    # executing_tasks[host] = task
                elif commands.get("put_conf"):
                    task = execute_rig_putconf_and_reboot.apply_async(
                        args=[ips_to_execute[host], username, password], expire=240, queue="ssh_tasks")
                    # reboot = execute_rig_reboot.apply_async(countdown=5,
                    #                                         args=[ips_to_execute[host], username, password],
                    #                                         expire=60)
                elif commands["reboot"]:
                    reboot = execute_rig_reboot.apply_async(countdown=2,
                                                            args=[ips_to_execute[host], username, password],
                                                            expire=240, queue="ssh_tasks")
                elif commands["update_miners"]:
                    update_miners = execute_rig_update_miners.apply_async(countdown=2,
                                                                          args=[ips_to_execute[host],
                                                                                username, password],
                                                                          expire=240, queue="ssh_tasks")
                elif commands["allow_command"]:
                    allow_command = execute_rig_allow_command.apply_async(countdown=2,
                                                                          args=[ips_to_execute[host],
                                                                                username, password],
                                                                          expire=240, queue="ssh_tasks")
                elif commands["update_miner_with_name"]:
                    update_miner_with_name = execute_rig_update_miner_with_name.apply_async(countdown=2,
                                                                                            args=[ips_to_execute[host],
                                                                                                  username, password,
                                                                                                  miner_name],
                                                                                            expire=240,
                                                                                            queue="ssh_tasks")
                elif commands["change_password"]:
                    change_pass = execute_change_password.apply_async(countdown=2,
                                                                      args=[ips_to_execute[host],
                                                                            username, password,
                                                                            new_password],
                                                                      expire=300,
                                                                      queue="ssh_tasks")
                elif commands["execute_custom_command"]:
                    execute_custom  = execute_custom_command.apply_async(countdown=2,
                                                                      args=[ips_to_execute[host],
                                                                            username,password,
                                                                            custom_command],
                                                                      expire=300,
                                                                      queue="ssh_tasks")


@celery.task
def technical_information_update():
    dict_of_bioses = {}
    dict_of_bioses = get_dict_of_bioses()
    redis_store.delete("technical_information:dict_of_bioses")
    if dict_of_bioses:
        redis_store.hmset("technical_information:dict_of_bioses", dict_of_bioses)

    list_of_bioses = get_list_of_bioses()
    redis_store.delete('technical_information:list_of_bioses')
    if list_of_bioses:
        redis_store.lpush('technical_information:list_of_bioses', *list_of_bioses)

    dict_of_rigs = {}
    if list_of_bioses:
        for bios_name_loop in list_of_bioses:
            dict_of_rigs = get_dict_of_rigs_for_bios(bios_name_loop)
            redis_store.delete("technical_information:{}:dict_of_rigs_bioses".format(str(bios_name_loop)))
            if dict_of_rigs:
                json_str = json.dumps(dict_of_rigs)
                redis_store.set("technical_information:{}:dict_of_rigs_bioses".format(str(bios_name_loop))
                                , json_str)

    dict_of_mobo = get_dict_of_mobo()
    redis_store.delete("technical_information:dict_of_mobo")
    if dict_of_mobo:
        redis_store.hmset("technical_information:dict_of_mobo", dict_of_mobo)

    dict_of_drive_names = get_dict_of_drive_names()
    redis_store.delete("technical_information:dict_of_drive_names")
    if dict_of_drive_names:
        redis_store.hmset("technical_information:dict_of_drive_names", dict_of_drive_names)

    ret_dict_all = get_dict_of_ip_info_all()
    redis_store.delete("technical_information:dict_of_ip_info_all")
    if ret_dict_all:
        json_str_all = json.dumps(ret_dict_all)
        redis_store.set("technical_information:dict_of_ip_info_all", json_str_all)

    list_of_alive_panels = redis_store.lrange('sidebar_info:list_of_alive_panels', 0, -1)
    for panel_name in list_of_alive_panels:
        ret_dict = get_dict_of_ip_info(panel_name=panel_name)
        redis_store.delete("technical_information:{}:dict_of_ip_info".format(str(panel_name)))
        if ret_dict:
            json_str = json.dumps(ret_dict)
            redis_store.set("technical_information:{}:dict_of_ip_info".format(str(panel_name))
                            , json_str)


@celery.task
def admin_main_dashboard_update():
    list_of_alive_panels = redis_store.lrange('sidebar_info:list_of_alive_panels', 0, -1)
    for panel_name in list_of_alive_panels:
        ret_list = get_unique_poll_info_list(panel_name=panel_name)
        redis_store.delete("admin_main_dashboard:{}:unique_poll_info_list".format(str(panel_name)))
        if ret_list:
            json_str = json.dumps(ret_list)
            redis_store.set("admin_main_dashboard:{}:unique_poll_info_list".format(str(panel_name))
                            , json_str)

        dual_miners_list = get_dual_miners_list(panel_name)
        redis_store.delete("admin_main_dashboard:{}:dual_miners_list".format(str(panel_name)))
        if dual_miners_list:
            redis_store.lpush("admin_main_dashboard:{}:dual_miners_list".format(str(panel_name)), *dual_miners_list)


@celery.task(expires=180, max_retries=0, soft_time_limit=480)
def set_list_of_nanopool_wallets():
    list_of_nanopool_wallets_dict = []
    list_of_nanopool_wallets = []
    list_of_alive_panels = redis_store.lrange('sidebar_info:list_of_alive_panels', 0, -1)
    panels_info = {}
    for panel_name in list_of_alive_panels:
        panels_info[panel_name] = {}
        list_of_pool_info_packed = redis_store.get(
            "admin_main_dashboard:{}:unique_poll_info_list".format(str(panel_name)))
        if list_of_pool_info_packed:

            panels_info[panel_name]["list_of_pool_info"] = json.loads(list_of_pool_info_packed)
        else:
            panels_info[panel_name]["list_of_pool_info"] = []
    if panels_info:
        for panel_name in panels_info:
            if panels_info[panel_name]["list_of_pool_info"]:
                for pool_info in panels_info[panel_name]["list_of_pool_info"]:
                    if pool_info.get("proxypool1"):
                        if "nanopool" in pool_info.get("proxypool1"):
                            list_of_nanopool_wallets_dict.append(pool_info)
                            if pool_info.get("proxywallet"):
                                list_of_nanopool_wallets.append(pool_info.get("proxywallet"))
    redis_store.delete("nanopool_dash:list_of_nanopool_wallets_dict")
    if list_of_nanopool_wallets_dict:
        json_str = json.dumps(list_of_nanopool_wallets_dict)
        redis_store.set("nanopool_dash:list_of_nanopool_wallets_dict", json_str)

    redis_store.delete("nanopool_dash:list_of_nanopool_wallets")
    if list_of_nanopool_wallets:
        redis_store.lpush("nanopool_dash:list_of_nanopool_wallets", *list_of_nanopool_wallets)


@celery.task(expires=180, max_retries=0, soft_time_limit=480)
def nanopool_info_update():
    # FOR Ethereum
    nanopool_eth_url = "https://api.nanopool.org/v1/eth/"
    list_of_nanopool_wallets = redis_store.lrange('nanopool_dash:list_of_nanopool_wallets', 0, -1)
    for nanopool_wallet in list_of_nanopool_wallets:

        response_hb = requests.get(nanopool_eth_url + "balance_hashrate/{}".format(str(nanopool_wallet)),
                                   timeout=20)
        json_dict_balance_hashrate = response_hb.json()

        if json_dict_balance_hashrate and json_dict_balance_hashrate.get("status") == True \
                and json_dict_balance_hashrate.get("data"):
            if json_dict_balance_hashrate["data"].get("hashrate") and json_dict_balance_hashrate["data"].get(
                    "balance"):
                redis_store.set("nanopool_wallet_info:{}:balance".format(str(nanopool_wallet)),
                                json_dict_balance_hashrate["data"].get("balance"))
                redis_store.set("nanopool_wallet_info:{}:hashrate".format(str(nanopool_wallet)),
                                json_dict_balance_hashrate["data"].get("hashrate"))

        response_24p = requests.get(nanopool_eth_url + "paymentsday/{}".format(str(nanopool_wallet)), timeout=20)
        json_dict_24_pay = response_24p.json()

        if json_dict_24_pay and json_dict_24_pay.get("status") == True:
            payments_24_table = []
            all_paid = 0.0
            for payment in json_dict_24_pay['data']:
                # payment["date"] = time.strftime('%Y-%m-%d', time.gmtime(payment["date"])) # UTC TIME
                payment["date"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payment["date"]))
                payments_24_table.append(payment)
                # utc_now = datetime.datetime.utcnow() #UTC NOW
                now = datetime.datetime.now()
                today = now.strftime('%Y-%m-%d')
                if today in payment['date']:
                    if payment.get("confirmed"):
                        all_paid += payment.get("amount")

            json_str_payments_24_table = json.dumps(payments_24_table)
            redis_store.set("nanopool_wallet_info:{}:payments_24_table".format(str(nanopool_wallet))
                            , json_str_payments_24_table)

            redis_store.set("nanopool_wallet_info:{}:all_paid_today".format(str(nanopool_wallet)), all_paid)

        response_shares = requests.get(nanopool_eth_url + "/shareratehistory/{}".format(str(nanopool_wallet)),
                                       timeout=20)

        dict_shares = response_shares.json()
        if dict_shares and dict_shares.get("status") == True:
            df = pd.DataFrame(dict_shares["data"])
            # df['date'] = pd.to_datetime(df['date'], unit='s',utc=True)
            # Localized time
            df['date'] = pd.to_datetime(df['date'], unit='s')
            df['date'] = df['date'].dt.tz_localize('UTC')
            df['date'] = df['date'].dt.tz_convert('Asia/Istanbul')
            df['date'] = df['date'].dt.date
            data_frame_obj = df.groupby(df.date).sum()
            dict_of_dates = data_frame_obj.to_dict()
            shares_table_dict_d = dict_of_dates.get("shares")
            shares_table_dict = {}
            for key in shares_table_dict_d.keys():
                if type(key) is not str:
                    try:
                        shares_table_dict[str(key.strftime("%Y-%m-%d"))] = shares_table_dict_d[key]
                    except Exception as e:
                        print(e)
                        print("nanopool_info_update Exception")
                        pass
            shares_table_json_srt = json.dumps(shares_table_dict)
            redis_store.set("nanopool_wallet_info:{}:shares_table".format(str(nanopool_wallet))
                            , shares_table_json_srt)


@celery.task(expires=180, max_retries=0, soft_time_limit=480)
def nanopool_payments_history_update():
    # FOR Ethereum
    nanopool_eth_url = "https://api.nanopool.org/v1/eth/"
    list_of_nanopool_wallets = redis_store.lrange('nanopool_dash:list_of_nanopool_wallets', 0, -1)
    for nanopool_wallet in list_of_nanopool_wallets:
        try:
            response_pay = requests.get(nanopool_eth_url + "payments/{}".format(str(nanopool_wallet)),
                                        timeout=20)
            json_dict_payments = response_pay.json()
            if os.path.exists("payments/{}.txt".format(str(nanopool_wallet))):
                os.remove("payments/{}.txt".format(str(nanopool_wallet)))
            with open("payments/{}.txt".format(str(nanopool_wallet)), "w") as payments_file:
                payments_file.write(json.dumps(json_dict_payments))
        except Exception as e:
            print("Failed to get payments from Nanopool")
            with open("payments/{}.txt".format(str(nanopool_wallet)), "r+") as payments_information:
                content = payments_information.read()
                json_dict_payments = json.loads(content)
            pass

        if json_dict_payments and json_dict_payments.get("status") == True:
            ret_dict = {}
            payments_list = copy.deepcopy(json_dict_payments["data"])
            for payment in payments_list:
                # payment['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(payment['date']))
                payment['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payment['date']))

            df = pd.DataFrame(json_dict_payments["data"])
            # df['date'] = pd.to_datetime(df['date'], unit='s',utc=True)
            # Localized time
            df['date'] = pd.to_datetime(df['date'], unit='s')
            df['date'] = df['date'].dt.tz_localize('UTC')
            df['date'] = df['date'].dt.tz_convert('Asia/Istanbul')
            df['date'] = df['date'].dt.date

            data_frame_obj = df.groupby(df.date)['amount'].sum()
            dict_of_total = dict_with_datetime_keys_to_str(data_frame_obj.to_dict())

            data_frame_obj = df.groupby(df.date)['amount'].count()
            dict_of_amount_tx = dict_with_datetime_keys_to_str(data_frame_obj.to_dict())

            for key, value in dict_of_total.items():
                if not ret_dict.get(key):
                    ret_dict[key] = {}
                ret_dict[key]["total"] = value
            for key, value in dict_of_amount_tx.items():
                if not ret_dict.get(key):
                    ret_dict[key] = {}
                ret_dict[key]["amount"] = value

            for key, value in ret_dict.items():
                if not ret_dict.get(key):
                    ret_dict[key] = {}
                for tx in payments_list:
                    if key in tx['date']:
                        if not ret_dict[key].get('tx_list'):
                            ret_dict[key]['tx_list'] = []
                        ret_dict[key]['tx_list'].append(tx)

            if ret_dict:
                json_srt = json.dumps(ret_dict)
                redis_store.set("nanopool_wallet_info:{}:all_payments".format(str(nanopool_wallet))
                                , json_srt)


@celery.task(bind=True, expires=120, max_retries=4, soft_time_limit=480)
def is_otp_seen_set(self, user_id):
    user = User.query.filter_by(id=user_id).first()
    user.is_otp_seen = True
    db.session.add(user)
    db.session.commit()


@celery.task(expires=180, max_retries=0, soft_time_limit=480)
def nanopool_report_update():
    # FOR Ethereum
    nanopool_eth_url = "https://api.nanopool.org/v1/eth/"
    list_of_nanopool_wallets = redis_store.lrange('nanopool_dash:list_of_nanopool_wallets', 0, -1)
    for nanopool_wallet in list_of_nanopool_wallets:
        try:
            response_pay = requests.get(nanopool_eth_url + "payments/{}".format(str(nanopool_wallet)),
                                        timeout=20)
            json_dict_payments = response_pay.json()
            if os.path.exists("payments/{}.txt".format(str(nanopool_wallet))):
                os.remove("payments/{}.txt".format(str(nanopool_wallet)))
            with open("payments/{}.txt".format(str(nanopool_wallet)), "w") as payments_file:
                payments_file.write(json.dumps(json_dict_payments))
        except Exception as e:
            print("Failed to get payments from Nanopool")
            with open("payments/{}.txt".format(str(nanopool_wallet)), "r+") as payments_information:
                content = payments_information.read()
                json_dict_payments = json.loads(content)
            pass

        if json_dict_payments and json_dict_payments.get("status") == True:
            ret_dict = {}
            payments_list = copy.deepcopy(json_dict_payments["data"])
            for payment in payments_list:
                # payment['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(payment['date']))
                payment['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payment['date']))

            df = pd.DataFrame(json_dict_payments["data"])
            # df['date'] = pd.to_datetime(df['date'], unit='s',utc=True)
            # Localized time
            df['date'] = pd.to_datetime(df['date'], unit='s')
            df['date'] = df['date'].dt.tz_localize('UTC')
            df['date'] = df['date'].dt.tz_convert('Asia/Istanbul')
            df['date'] = df['date'].dt.date

            data_frame_obj = df.groupby(df.date)['amount'].sum()
            dict_of_total = dict_with_datetime_keys_to_str(data_frame_obj.to_dict())

            response_pay = requests.get(nanopool_eth_url + "history/{}".format(str(nanopool_wallet)),
                                        timeout=20)
            json_dict_hashrate_chart = response_pay.json()

            if json_dict_hashrate_chart and json_dict_hashrate_chart.get("status"):

                df = pd.DataFrame(json_dict_hashrate_chart["data"])
                # df['date'] = pd.to_datetime(df['date'], unit='s',utc=True)
                # Localized time
                df['date'] = pd.to_datetime(df['date'], unit='s')
                df['date'] = df['date'].dt.tz_localize('UTC')
                df['date'] = df['date'].dt.tz_convert('Asia/Istanbul')
                df['date'] = df['date'].dt.date

                data_frame_obj = df.groupby(df.date)['hashrate'].mean()
                dict_of_average_hashrate = dict_with_datetime_keys_to_str(data_frame_obj.to_dict())

                for key, value in dict_of_average_hashrate.items():
                    if not ret_dict.get(key):
                        ret_dict[key] = {}
                    if value != 0.0:
                        ret_dict[key]["average_hashrate"] = round((float(value) / 1000.0), 3)
                    else:
                        ret_dict[key]["average_hashrate"] = value

                for key, value in dict_of_total.items():
                    if ret_dict.get(key):
                        ret_dict[key]["total"] = value

                response_shares = requests.get(
                    nanopool_eth_url + "/shareratehistory/{}".format(str(nanopool_wallet)),
                    timeout=20)

                dict_shares = response_shares.json()
                if dict_shares and dict_shares.get("status") == True:
                    df = pd.DataFrame(dict_shares["data"])
                    # df['date'] = pd.to_datetime(df['date'], unit='s',utc=True)
                    # Localized time
                    df['date'] = pd.to_datetime(df['date'], unit='s')
                    df['date'] = df['date'].dt.tz_localize('UTC')
                    df['date'] = df['date'].dt.tz_convert('Asia/Istanbul')
                    df['date'] = df['date'].dt.date
                    data_frame_obj = df.groupby(df.date).sum()
                    dict_of_dates = data_frame_obj.to_dict()
                    shares_table_dict_d = dict_of_dates.get("shares")
                    shares_table_dict = {}
                    for key in shares_table_dict_d.keys():
                        if type(key) is not str:
                            try:
                                shares_table_dict[str(key.strftime("%Y-%m-%d"))] = shares_table_dict_d[key]
                            except Exception as e:
                                print(e)
                                print("nanopool_info_update Exception")
                                pass

                    for key, value in shares_table_dict.items():
                        if ret_dict.get(key):
                            ret_dict[key]["shares"] = value
            if ret_dict:
                json_srt = json.dumps(ret_dict)
                redis_store.set("nanopool_wallet_info:{}:report_by_days".format(str(nanopool_wallet))
                                , json_srt)
