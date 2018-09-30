import datetime
import json

import flask_pymongo
import time

from application import mongo, redis_store
from application.main_logic.functions import curr_time_non_naive, curr_time_naive, days_hours_minutes
from application.main_logic.panel_info import get_location_by_hostname
from config import Config

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-02-06"
__app__ = "statswebapp"
__status__ = "Development"


class TechnicalInfoDashboard:
    def __init__(self):
        measure_time_start = time.time()
        self.dict_of_ip_info_panels = {}
        self.dict_of_bioses = redis_store.hgetall("technical_information:dict_of_bioses")
        self.dict_of_mobo = redis_store.hgetall("technical_information:dict_of_mobo")
        self.dict_of_drive_names = redis_store.hgetall("technical_information:dict_of_drive_names")
        num_of_rigs = redis_store.get('main_dashboard:num_of_rigs')
        if num_of_rigs:
            self.num_of_rigs = int(num_of_rigs)

        num_of_gpus = redis_store.get('main_dashboard:num_of_gpus')
        if num_of_gpus:
            self.num_of_gpus = int(num_of_gpus)

        num_of_alive_gpus = redis_store.get('main_dashboard:num_of_alive_gpus')
        if num_of_alive_gpus:
            self.num_of_alive_gpus = int(num_of_alive_gpus)

        dict_of_ip_info_all_packed = redis_store.get("technical_information:dict_of_ip_info_all")
        if dict_of_ip_info_all_packed:
            self.dict_of_ip_info_all = json.loads(dict_of_ip_info_all_packed)
        else:
            self.dict_of_ip_info_all = {}

        list_of_alive_panels = redis_store.lrange('sidebar_info:list_of_alive_panels', 0, -1)
        for panel_name in list_of_alive_panels:

            dict_of_ip_info_packed = redis_store.get("technical_information:{}:dict_of_ip_info".format(str(panel_name)))
            if dict_of_ip_info_packed:
                self.dict_of_ip_info_panels[panel_name] = json.loads(dict_of_ip_info_packed)
            else:
                self.dict_of_ip_info_panels[panel_name] = {}

        measure_time_end = time.time()
        self.execution_time = round((measure_time_end - measure_time_start), 2)


class BiosesRigDashboard:
    def __init__(self, bios_name):

        measure_time_start = time.time()
        self.dict_of_bioses = redis_store.hgetall("technical_information:dict_of_bioses")

        num_of_gpus = redis_store.get('main_dashboard:num_of_gpus')
        if num_of_gpus:
            self.num_of_gpus = int(num_of_gpus)
        num_of_rigs = redis_store.get('main_dashboard:num_of_rigs')
        if num_of_rigs:
            self.num_of_rigs = int(num_of_rigs)

        num_of_alive_gpus = redis_store.get('main_dashboard:num_of_alive_gpus')
        if num_of_alive_gpus:
            self.num_of_alive_gpus = int(num_of_alive_gpus)
        dict_of_rigs_packed = redis_store.get("technical_information:{}:dict_of_rigs_bioses".format(str(bios_name)))
        if dict_of_rigs_packed:
            self.dict_of_rigs = json.loads(dict_of_rigs_packed)
        else:
            self.dict_of_rigs = {}
        measure_time_end = time.time()
        self.execution_time = round((measure_time_end - measure_time_start), 2)


def get_dict_of_bioses(panel_name=None):
    dict_of_bioses = {}
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'bioses': 1}) \
                .sort('received_at', flask_pymongo.DESCENDING) \
                .limit(1)
            if cursor.count() > 0:
                res = list(cursor)
                dict_res = res[0]
                received_at_utc = dict_res['received_at']
                received_at_utc_local = curr_time_non_naive(received_at_utc)
                now_local = curr_time_naive(datetime.datetime.utcnow())
                dif = now_local - received_at_utc_local
                days, hours, minutes = days_hours_minutes(dif)
                if days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    if dict_res.get("bioses"):
                        bioses_info = dict_res.get("bioses")
                        bioses_list = bioses_info.strip().split(' ')
                        for bios in bioses_list:
                            if bios not in dict_of_bioses:
                                dict_of_bioses[bios] = 1
                            else:
                                dict_of_bioses[bios] += 1

    return dict_of_bioses


def get_list_of_bioses():
    list_of_bioses = []
    all_coll_names = mongo.db.collection_names()
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'bioses': 1}) \
                .sort('received_at', flask_pymongo.DESCENDING) \
                .limit(1)
            if cursor.count() > 0:
                res = list(cursor)
                dict_res = res[0]
                received_at_utc = dict_res['received_at']
                received_at_utc_local = curr_time_non_naive(received_at_utc)
                now_local = curr_time_naive(datetime.datetime.utcnow())
                dif = now_local - received_at_utc_local
                days, hours, minutes = days_hours_minutes(dif)
                if days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    if dict_res.get("bioses"):
                        bioses_info = dict_res.get("bioses")
                        bioses_list = bioses_info.strip().split(' ')
                        for bios in bioses_list:
                            if bios not in list_of_bioses:
                                list_of_bioses.append(bios)

    return list_of_bioses


def get_dict_of_rigs_for_bios(bios_name):
    dict_of_rigs = {}
    all_coll_names = mongo.db.collection_names()
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'bioses': 1}) \
                .sort('received_at', flask_pymongo.DESCENDING) \
                .limit(1)
            if cursor.count() > 0:
                res = list(cursor)
                dict_res = res[0]
                received_at_utc = dict_res['received_at']
                received_at_utc_local = curr_time_non_naive(received_at_utc)
                now_local = curr_time_naive(datetime.datetime.utcnow())
                dif = now_local - received_at_utc_local
                days, hours, minutes = days_hours_minutes(dif)
                if days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    if dict_res.get("bioses"):
                        bioses_info = dict_res.get("bioses")
                        bioses_list = bioses_info.strip().split(' ')
                        if bios_name in bioses_list:
                            dict_of_rigs[host] = {"panel_name": collection_name, "bioses": bioses_list,
                                                  "location": get_location_by_hostname(host)}
    return dict_of_rigs


def is_bios_exist(bios_name):
    bioses_list = redis_store.lrange("technical_information:list_of_bioses", 0, -1)
    if bios_name in bioses_list:
        return True
    else:
        return False


def get_dict_of_mobo(panel_name=None):
    dict_of_mobo = {}
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'mobo': 1}) \
                .sort('received_at', flask_pymongo.DESCENDING) \
                .limit(1)
            if cursor.count() > 0:
                res = list(cursor)
                dict_res = res[0]
                received_at_utc = dict_res['received_at']
                received_at_utc_local = curr_time_non_naive(received_at_utc)
                now_local = curr_time_naive(datetime.datetime.utcnow())
                dif = now_local - received_at_utc_local
                days, hours, minutes = days_hours_minutes(dif)
                if days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    if dict_res.get("mobo"):
                        mobo_str = dict_res.get("mobo")
                        if mobo_str not in dict_of_mobo:
                            dict_of_mobo[mobo_str] = 1
                        else:
                            dict_of_mobo[mobo_str] += 1

    return dict_of_mobo


def get_dict_of_drive_names(panel_name=None):
    dict_of_drives = {}
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'drive_name': 1}) \
                .sort('received_at', flask_pymongo.DESCENDING) \
                .limit(1)
            if cursor.count() > 0:
                res = list(cursor)
                dict_res = res[0]
                received_at_utc = dict_res['received_at']
                received_at_utc_local = curr_time_non_naive(received_at_utc)
                now_local = curr_time_naive(datetime.datetime.utcnow())
                dif = now_local - received_at_utc_local
                days, hours, minutes = days_hours_minutes(dif)
                if days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    if dict_res.get("drive_name"):
                        mobo_str = dict_res.get("drive_name")
                        if "INTEL" in mobo_str:
                            mobo_list = mobo_str.strip().split(' ')
                            if len(mobo_list) >= 3:
                                mobo_str = "SSD"
                        if "ADATA" in mobo_str:
                            mobo_str = "SSD"
                        if "SAMSUNG" in mobo_str:
                            mobo_str = "SSD"
                        if "SanDisk SDSSDA120G" in mobo_str:
                            mobo_str = "SSD"
                        if "PH4-CE120" in mobo_str:
                            mobo_str = "SSD"
                        # Flash Drives
                        if "Ultra" in mobo_str:
                            mobo_str = "Flash Drive"
                        if "x800m" in mobo_str:
                            mobo_str = "Flash Drive"
                        if "Cruzer" in mobo_str:
                            mobo_str = "Flash Drive"
                        if mobo_str not in dict_of_drives:
                            dict_of_drives[mobo_str] = 1
                        else:
                            dict_of_drives[mobo_str] += 1

    return dict_of_drives


def get_dict_of_ip_info_all():
    dict_of_ip_info = {'Working local configuration': []}
    all_coll_names = mongo.db.collection_names()
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'send_remote': 1, "config_status": 1}) \
                .sort('received_at', flask_pymongo.DESCENDING) \
                .limit(1)
            if cursor.count() > 0:
                res = list(cursor)
                dict_res = res[0]
                received_at_utc = dict_res['received_at']
                received_at_utc_local = curr_time_non_naive(received_at_utc)
                now_local = curr_time_naive(datetime.datetime.utcnow())
                dif = now_local - received_at_utc_local
                days, hours, minutes = days_hours_minutes(dif)
                if days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    config_status = dict_res.get('config_status')
                    send_remote = dict_res.get('send_remote')
                    if not send_remote and config_status == 'singlerig':
                        dict_of_ip_info['Working local configuration'].append(host)
                    else:
                        if not dict_of_ip_info.get(send_remote):
                            dict_of_ip_info[send_remote] = []
                            dict_of_ip_info[send_remote].append(host)
                        else:
                            dict_of_ip_info[send_remote].append(host)
    return dict_of_ip_info


def get_dict_of_ip_info(panel_name):
    dict_of_ip_info = {"Connected to Remote server": [], 'Working local configuration': []}

    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'send_remote': 1, "config_status": 1}) \
                .sort('received_at', flask_pymongo.DESCENDING) \
                .limit(1)
            if cursor.count() > 0:
                res = list(cursor)
                dict_res = res[0]
                received_at_utc = dict_res['received_at']
                received_at_utc_local = curr_time_non_naive(received_at_utc)
                now_local = curr_time_naive(datetime.datetime.utcnow())
                dif = now_local - received_at_utc_local
                days, hours, minutes = days_hours_minutes(dif)
                if days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    config_status = dict_res.get('config_status')
                    send_remote = dict_res.get('send_remote')
                    if not send_remote and config_status == 'singlerig':
                        dict_of_ip_info['Working local configuration'].append(host)
                    else:
                        dict_of_ip_info["Connected to Remote server"].append(host)
    return dict_of_ip_info
