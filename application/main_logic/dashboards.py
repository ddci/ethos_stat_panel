import json
import traceback

import re

from application.main_logic.panel_info import PanelInfo, get_list_of_rigs_under_attack

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-09"
__app__ = "statswebapp"
__status__ = "Development"

import flask_pymongo
from config import Config
import datetime
import time
from application.main_logic.functions import curr_time_naive, curr_time_non_naive, days_hours_minutes, all_min_from_td
from .. import mongo, redis_store


class MainDashboard:

    def __init__(self):
        measure_time_start = time.time()
        self.num_of_panels, self.list_of_panels = get_num_and_list_of_panels()
        # self.num_of_gpus = get_num_of_gpus()
        # self.num_of_alive_gpus = get_num_of_alive_gpus()
        # self.total_hashrate = get_total_hashrate()
        # self.num_of_rigs = get_num_of_all_rigs()
        # self.num_of_alive_rigs = get_num_of_alive_rigs()
        # self.average_gpu_temperature = get_average_gpu_temperature()

        num_of_rigs_under_attack = redis_store.get("main_dashboard:num_of_rigs_under_attack")
        if num_of_rigs_under_attack:
            self.num_of_rigs_under_attack = int(num_of_rigs_under_attack)

        num_of_gpus = redis_store.get('main_dashboard:num_of_gpus')
        if num_of_gpus:
            self.num_of_gpus = int(num_of_gpus)

        num_of_alive_gpus = redis_store.get('main_dashboard:num_of_alive_gpus')
        if num_of_alive_gpus:
            self.num_of_alive_gpus = int(num_of_alive_gpus)

        total_hashrate = redis_store.get('main_dashboard:total_hashrate')
        if total_hashrate:
            self.total_hashrate = float(total_hashrate)

        num_of_rigs = redis_store.get('main_dashboard:num_of_rigs')
        if num_of_rigs:
            self.num_of_rigs = int(num_of_rigs)

        num_of_alive_rigs = redis_store.get('main_dashboard:num_of_alive_rigs')
        if num_of_alive_rigs:
            self.num_of_alive_rigs = int(num_of_alive_rigs)

        average_gpu_temperature = redis_store.get('main_dashboard:average_gpu_temperature')
        if average_gpu_temperature:
            self.average_gpu_temperature = float(average_gpu_temperature)

        # Careful multiple values return
        self.list_of_alive_panels = redis_store.lrange('main_dashboard:list_of_alive_panels', 0, -1)

        num_of_alive_panels = redis_store.get('main_dashboard:num_of_alive_panels')
        if num_of_alive_panels:
            self.num_of_alive_panels = int(num_of_alive_panels)

        self.panels_info = {}
        if self.list_of_alive_panels:
            for panel_name in self.list_of_alive_panels:
                self.panels_info[panel_name] = {}

                redis_res_dict = redis_store.hgetall("panel_dashboard:{}".format(str(panel_name)))

                # TOOOO REDISS!!!
                self.panels_info[panel_name]['miners_list'] = get_list_of_miners(panel_name)

                total_hashrate = redis_res_dict.get('total_hashrate')

                if total_hashrate:
                    self.panels_info[panel_name]['total_hashrate'] = float(total_hashrate)

                num_of_gpus = redis_res_dict.get('num_of_gpus')
                if num_of_gpus:
                    self.panels_info[panel_name]['num_of_gpus'] = int(num_of_gpus)
                else:
                    self.panels_info[panel_name]['num_of_gpus'] = 0

                num_of_alive_gpus = redis_res_dict.get('num_of_alive_gpus')
                if num_of_alive_gpus:
                    self.panels_info[panel_name]['num_of_alive_gpus'] = int(num_of_alive_gpus)

                num_of_rigs = redis_res_dict.get('num_of_rigs')
                if num_of_rigs:
                    self.panels_info[panel_name]['num_of_rigs'] = int(num_of_rigs)

                num_of_alive_rigs = redis_res_dict.get('num_of_alive_rigs')
                if num_of_alive_rigs:
                    self.panels_info[panel_name]['num_of_alive_rigs'] = int(num_of_alive_rigs)

                average_gpu_temperature = redis_res_dict.get('average_gpu_temperature')
                if average_gpu_temperature:
                    self.panels_info[panel_name]['average_gpu_temperature'] = float(average_gpu_temperature)

                num_of_crashed_gpus = redis_res_dict.get('num_of_crashed_gpus')
                if num_of_crashed_gpus:
                    self.panels_info[panel_name]['num_of_crashed_gpus'] = int(num_of_crashed_gpus)

                # self.panels_info[panel_name]['dual_miners_list'] = redis_store.lrange(
                #     "panel_dashboard:{}:dual_miners_list".format(str(panel_name)), 0, -1)

        measure_time_end = time.time()
        self.execution_time = round((measure_time_end - measure_time_start), 2)


class PanelDashboard:
    def __init__(self, panel_name, crashed_gpus=False, offline_rigs=False, rig_name=None, under_attack=None):
        measure_time_start = time.time()
        all_coll_names = mongo.db.collection_names()
        if panel_name in all_coll_names:
            redis_res_dict = redis_store.hgetall("panel_dashboard:{}".format(str(panel_name)))

            total_hashrate = redis_res_dict.get('total_hashrate')

            if total_hashrate:
                self.total_hashrate = float(total_hashrate)

            num_of_gpus = redis_res_dict.get('num_of_gpus')
            if num_of_gpus:
                self.num_of_gpus = int(num_of_gpus)
            else:
                self.num_of_gpus = 0

            num_of_alive_gpus = redis_res_dict.get('num_of_alive_gpus')
            if num_of_alive_gpus:
                self.num_of_alive_gpus = int(num_of_alive_gpus)

            num_of_rigs = redis_res_dict.get('num_of_rigs')
            if num_of_rigs:
                self.num_of_rigs = int(num_of_rigs)

            num_of_alive_rigs = redis_res_dict.get('num_of_alive_rigs')
            if num_of_alive_rigs:
                self.num_of_alive_rigs = int(num_of_alive_rigs)

            average_gpu_temperature = redis_res_dict.get('average_gpu_temperature')
            if average_gpu_temperature:
                self.average_gpu_temperature = float(average_gpu_temperature)

            num_of_crashed_gpus = redis_res_dict.get('num_of_crashed_gpus')
            if num_of_crashed_gpus:
                self.num_of_crashed_gpus = int(num_of_crashed_gpus)

            if num_of_rigs:
                if self.num_of_rigs > 0:
                    self.offline_rigs = self.num_of_rigs - self.num_of_alive_rigs
                else:
                    self.offline_rigs = 0
            # self.total_hashrate = get_total_hashrate(panel_name=panel_name)
            #
            # self.num_of_gpus = get_num_of_gpus(panel_name=panel_name)
            # self.num_of_alive_gpus = get_num_of_alive_gpus(panel_name=panel_name)
            #
            # self.num_of_rigs = get_num_of_all_rigs(panel_name=panel_name)
            # self.num_of_alive_rigs = get_num_of_alive_rigs(panel_name=panel_name)
            #
            # self.average_gpu_temperature = get_average_gpu_temperature(panel_name=panel_name)

            list_of_rigs_under_attack = redis_store.lrange(
                "panel_info:{}:list_of_rigs_under_attack".format(str(panel_name)), 0, -1)
            if list_of_rigs_under_attack:
                self.list_of_rigs_under_attack = list_of_rigs_under_attack
            else:
                self.list_of_rigs_under_attack = []

            # Careful here to complicated=)
            self.panel_info = PanelInfo(panel_name=panel_name, crashed_gpus=crashed_gpus, offline_rigs=offline_rigs,
                                        rig_name=rig_name, under_attack=under_attack)
            measure_time_end = time.time()
            self.execution_time = round((measure_time_end - measure_time_start), 2)
        else:
            raise Exception


def get_num_of_alive_gpus(panel_name=None):
    alive_gpus = 0
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'gpus': 1, 'received_at': 1, 'miner_hashes': 1}) \
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
                if all_min_from_td(dif) <= int(Config.APP_SETTINGS_PERIOD_TO_LIVE) and days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    if dict_res['miner_hashes'] and dict_res['miner_hashes'] is not None:
                        hashes = dict_res['miner_hashes']
                        stripped = hashes.strip().split(' ')
                        if len(stripped) == 1:
                            gpu_hash = float(hashes)
                            if gpu_hash > 0.0:
                                alive_gpus += 1
                        elif len(stripped) >= 2:
                            for _hash in stripped:
                                if (float(_hash)) > 0.0:
                                    alive_gpus += 1

    return alive_gpus


def get_num_and_list_of_panels():
    """Number of pools"""
    all_coll_names = mongo.db.collection_names()
    num = len(all_coll_names)
    return num, all_coll_names


def get_num_of_gpus(panel_name=None):
    """Number of GPUs
    if poll_name is not give will count for all polls
    """
    all_gpus = 0
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'gpus': 1, 'received_at': 1}) \
                .sort('received_at', flask_pymongo.DESCENDING) \
                .limit(1)
            if cursor.count() > 0:
                res = list(cursor)
                dict_res = res[0]
                gpus_string = dict_res['gpus']
                received_at_utc = dict_res['received_at']
                received_at_utc_local = curr_time_non_naive(received_at_utc)
                now_local = curr_time_naive(datetime.datetime.utcnow())
                dif = now_local - received_at_utc_local
                days, hours, minutes = days_hours_minutes(dif)
                if days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    res_list = [int(s) for s in re.findall(r'\d+', gpus_string)]
                    if res_list:
                        num_of_gpus = res_list[0]
                        all_gpus += num_of_gpus

    return all_gpus


def get_total_hashrate(panel_name=None):
    """Get total hashrate
    if poll_name is not given will count for all polls
    """
    total_hashrate = 0
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'hash': 1, 'received_at': 1}) \
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
                if all_min_from_td(dif) <= int(Config.APP_SETTINGS_PERIOD_TO_LIVE) and days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    if dict_res['hash'] and dict_res['hash'] is not None:
                        total_hashrate += float(dict_res['hash'])
                    total_hashrate = round(total_hashrate, 3)
    return total_hashrate


def get_num_and_list_of_alive_panels():
    """Get alive """
    alive_pools = 0
    list_of_alive_polls = []
    all_coll_names = mongo.db.collection_names()
    is_found_for_this_pool = {}
    for host in all_coll_names:
        is_found_for_this_pool[str(host)] = False
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            if not is_found_for_this_pool[str(collection_name)]:
                cursor = collection.find({'hostname': str(host)}, {'hash': 1, 'received_at': 1}) \
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
                    if days <= int(Config.APP_SETTINGS_PERIOD_TO_HIDE_PANEL):
                        alive_pools += 1
                        list_of_alive_polls.append(str(collection_name))
                        is_found_for_this_pool[str(collection_name)] = True

    return alive_pools, list_of_alive_polls


def get_num_of_all_rigs(panel_name=None):
    """Get number of all available rigs
    if poll_name is not give will count for all polls
    """
    all_rigs = 0
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1}) \
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
                if days < int(Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    all_rigs += 1
    return all_rigs


def get_num_of_alive_rigs(panel_name=None):
    """Get number of all rigs using APP_SETTINGS_PERIOD_TO_LIVE to define aliveness=)
    if poll_name is notFd= give will count for all polls
    """
    alive_rigs = 0
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'hash': 1}) \
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
                if all_min_from_td(dif) <= int(Config.APP_SETTINGS_PERIOD_TO_LIVE) and days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    total_hash = re.findall(r"[-+]?\d*\.\d+|\d+", dict_res['hash'])
                    if total_hash:
                        if float(total_hash[0]) != 0.0:
                            alive_rigs += 1
                            a = 2
    return alive_rigs


def get_average_gpu_temperature(panel_name=None):
    """Get average temp of GPUs
    if poll_name is not give will count for all polls
    """
    all_temp = 0
    number_of_gpus = 0
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'temp': 1, 'received_at': 1, 'miner_hashes': 1}) \
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
                if all_min_from_td(dif) <= int(Config.APP_SETTINGS_PERIOD_TO_LIVE) \
                        and days < int(Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    if dict_res['temp'] and dict_res['temp'] is not None:
                        temps = dict_res['temp']
                        stripped = temps.strip().split(' ')
                        if len(stripped) == 1:
                            gpu_temp = float(temps)
                            if gpu_temp > 0.0 and gpu_temp < 120.00:
                                all_temp += gpu_temp
                                number_of_gpus += 1
                        elif len(stripped) >= 2:
                            for temp in stripped:
                                if (float(temp)) > 0.0 and (float(temp)) < 120.00:
                                    all_temp += float(temp)
                                    number_of_gpus += 1
    if all_temp == 0 or number_of_gpus == 0:
        return 0
    else:
        av_temp = all_temp / number_of_gpus
        import math
        av_temp = math.ceil(av_temp * 100) / 100
        return av_temp


def get_list_of_miners(panel_name):
    miners_list = []
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        greater_than_date = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        unique_miners = collection.find({"received_at": {"$gt": greater_than_date}}).distinct('miner')
        miners_list = unique_miners

    return miners_list


def get_dual_miners_list(panel_name=None):
    dual_miners_rigs = []
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'dualminer_status': 1}) \
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
                    if dict_res.get("dualminer_status"):
                        dual_miner_status = dict_res.get("dualminer_status")
                        if dual_miner_status == "enabled":
                            dual_miners_rigs.append(host)

    return dual_miners_rigs


def get_num_of_crashed_gpus(panel_name=None):
    crashed_gpus = 0
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'gpus': 1, 'received_at': 1, 'miner_hashes': 1}) \
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
                if all_min_from_td(dif) <= int(Config.APP_SETTINGS_PERIOD_TO_LIVE) and days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    if dict_res['miner_hashes'] and dict_res['miner_hashes'] is not None:
                        hashes = dict_res['miner_hashes']
                        stripped = hashes.strip().split(' ')
                        if len(stripped) == 1:
                            gpu_hash = float(hashes)
                            if gpu_hash == 0.0:
                                crashed_gpus += 1
                        elif len(stripped) >= 2:
                            for _hash in stripped:
                                if (float(_hash)) == 0.0:
                                    crashed_gpus += 1
    return crashed_gpus
