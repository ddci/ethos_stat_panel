import re
from threading import Thread

from application.main_logic.parser import parse_json_to_dict
from application.models import LocationFieldPanel

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-12"
__app__ = "statswebapp"
__status__ = "Development"

import flask_pymongo
from config import Config
import datetime
import time
from application.main_logic.functions import curr_time_naive, curr_time_non_naive, is_panel_exist, \
    list_from_all_status_flags, days_hours_minutes, all_min_from_td, days_hours_minutes_from_sec
from .. import mongo, redis_store


class PanelInfo:
    def __init__(self, panel_name, crashed_gpus=False, offline_rigs=False, rig_name=None, under_attack=None):
        self.rigs_info = {}
        if crashed_gpus:
            list_of_hosts_with_crashed_gpus = redis_store.lrange(
                'panel_info:{}:list_of_hosts_with_crashed_gpus'.format(str(panel_name)), 0, -1)
            if list_of_hosts_with_crashed_gpus:
                for host in list_of_hosts_with_crashed_gpus:
                    rig_inf = RigInfoOptimized(hostname=host, panel_name=panel_name, rigs_info=self.rigs_info)
                    thread = Thread(target=rig_inf.call(), name="Thread_RigInfoOptimized{}".format(host))
                    thread.start()

        elif offline_rigs:

            list_of_offline_rigs = redis_store.lrange('panel_info:{}:list_of_offline_rigs'.format(str(panel_name)), 0,
                                                      -1)
            if list_of_offline_rigs:
                for host in list_of_offline_rigs:
                    rig_inf = RigInfoOptimized(hostname=host, panel_name=panel_name, rigs_info=self.rigs_info)
                    thread = Thread(target=rig_inf.call(), name="Thread_RigInfoOptimized{}".format(host))
                    thread.start()
        elif rig_name:
            collection = mongo.db[panel_name]
            # find_one returns dict, find  returns cursor
            unique_hostnames = collection.find({}).distinct('hostname')
            if rig_name in unique_hostnames:
                rig_inf = RigInfoOptimized(hostname=rig_name, panel_name=panel_name, rigs_info=self.rigs_info)
                thread = Thread(target=rig_inf.call(), name="Thread_RigInfoOptimized{}".format(rig_name))
                thread.start()

        elif under_attack:
            under_attack_rigs = redis_store.lrange('panel_info:{}:list_of_rigs_under_attack'.format(str(panel_name)), 0,
                                                   -1)
            if under_attack_rigs:
                for host in under_attack_rigs:
                    rig_inf = RigInfoOptimized(hostname=host, panel_name=panel_name, rigs_info=self.rigs_info)
                    thread = Thread(target=rig_inf.call(), name="Thread_RigInfoOptimized{}".format(host))
                    thread.start()
        else:
            alive_rigs = redis_store.lrange('panel_info:{}:alive_rigs'.format(str(panel_name)), 0, -1)
            for host in alive_rigs:
                # self.rigs_info[str(host)] = RigInfoOptimized(hostname=host, panel_name=panel_name)
                rig_inf = RigInfoOptimized(hostname=host, panel_name=panel_name, rigs_info=self.rigs_info)
                thread = Thread(target=rig_inf.call(), name="Thread_RigInfoOptimized{}".format(host))
                thread.start()


class RigInfoOptimized:
    def __init__(self, hostname, panel_name, rigs_info=None):
        self.hostname = hostname
        self.panel_name = panel_name
        self.rigs_info = rigs_info

    def call(self):
        self.res = retrieve_rig_stat_optimized(self.hostname, self.panel_name)
        self.miner = self.res['miner']  #
        self.status = self.res['status']  #
        # list
        self.flags_status = self.res['flags_status']
        # list
        self.gpu_temps = self.res['gpu_temps']
        self.gpus = self.res['gpus']  #
        self.gpus_alive = self.res['gpus_alive']  #
        # list
        self.miner_hashes = self.res['miner_hashes']
        self.last_request = self.res['last_request']
        self.is_off = self.res['is_off']
        self.ip_address = self.res['ip_address']

        self.uptime = self.res['uptime']

        self.rx_kbps = self.res['rx_kbps']
        self.tx_kbps = self.res['tx_kbps']
        self.total_hashrate = self.res['total_hashrate']
        self.cpu_temp = self.res['cpu_temp']
        self.powertune = self.res['powertune']

        self.fanrpm = self.res['fanrpm']

        self.zipfaninsfo = zip(self.res['fanrpm'], self.res['fanpercent'])
        # Core
        self.core = self.res['core']

        # Rig location Number
        if self.res['number'] is not None:
            self.number = str(self.res['number'])

        else:
            self.number = self.res['number']

        self.mem = self.res['mem']

        self.config_status = self.res['config_status']
        self.send_remote = self.res['send_remote']
        self.config_s = self.res['config_s']
        self.miner_version = self.res['miner_version']
        # self.models = self.res['models']

        self.rigs_info[self.hostname] = self


def retrieve_rig_stat_optimized(hostname, panel_name):
    """Retrieve info from DB to show in table
    """
    return_dict = {}
    return_dict['miner'] = ""
    return_dict['status'] = ""
    return_dict['flags_status'] = []
    return_dict['gpu_temps'] = []
    return_dict['gpus'] = 0
    return_dict['gpus_alive'] = 0
    return_dict['miner_hashes'] = []
    return_dict['last_request'] = 0
    return_dict['is_off'] = True
    return_dict['ip_address'] = ""
    return_dict['last_request'] = None
    return_dict['is_off'] = True
    return_dict['miner_hashes'] = []
    return_dict['uptime'] = None

    return_dict['cpu_temp'] = 0

    return_dict['rx_kbps'] = 0.0
    return_dict['tx_kbps'] = 0.0

    return_dict['total_hashrate'] = 0.0

    return_dict['powertune'] = []

    # Fans

    return_dict['fanrpm'] = []
    return_dict['fanpercent'] = []

    return_dict['core'] = []
    return_dict['default_core'] = []

    return_dict['mem'] = []

    return_dict['number'] = 0

    return_dict['config_status'] = ""
    return_dict['send_remote'] = ""
    return_dict['config_s'] = ""

    return_dict['mem_states'] = []

    return_dict['hash'] = 0.0

    # return_dict['models'] = []

    if LocationFieldPanel.query.filter_by(hostname=hostname).first() is not None:
        loc = LocationFieldPanel.query.filter_by(hostname=hostname).first()
        return_dict['number'] = loc.number

    collection = mongo.db[str(panel_name)]
    # find_one returns dict, find  returns cursor
    second_parameter = {'ip': 1, 'temp': 1, 'status': 1,
                        'miner': 1, 'gpus': 1,
                        'received_at': 1, 'miner_hashes': 1,
                        'defunct': 1, 'overheat': 1,
                        'adl_error': 1, 'autorebooted': 1,
                        'updating': 1, 'throttled': 1,
                        "uptime": 1, "cpu_temp": 1,
                        "rx_kbps": 1, "tx_kbps": 1,
                        "powertune": 1,
                        'fanpercent': 1, 'fanrpm': 1,
                        'default_core': 1, 'core': 1,
                        'mem': 1, "config_status": 1,
                        "send_remote": 1, 'memstates': 1,
                        'hash': 1, "miner_version": 1}
    cursor = collection.find({'hostname': str(hostname)}, second_parameter) \
        .sort('received_at', flask_pymongo.DESCENDING) \
        .limit(1)

    if cursor.count() > 0:
        res = list(cursor)
        mongo_dict = res[0]
        return_dict['miner'] = mongo_dict.get('miner')
        return_dict['status'] = mongo_dict.get('status')
        return_dict['ip_address'] = mongo_dict.get('ip')
        return_dict['miner_version'] = mongo_dict.get('miner_version')

        # if mongo_dict.get("models"):
        #     models_string = mongo_dict.get("models")
        #     if models_string:
        #         models_list = models_string.strip().split('\n')
        #         if models_list:
        #             return_dict['models'] = models_list

        return_dict['flags_status'] = list_from_all_status_flags(in_dict=mongo_dict)
        total_hash = re.findall(r"[-+]?\d*\.\d+|\d+", mongo_dict['hash'])
        if total_hash:
            if float(total_hash[0]) != 0.0:
                miner_hashes_list = re.findall(r"[-+]?\d*\.\d+|\d+", mongo_dict['miner_hashes'])
                return_dict['miner_hashes'] = [float(x) for x in miner_hashes_list]
                if return_dict['miner_hashes']:
                    for idx, hashrate in enumerate(return_dict['miner_hashes']):
                        if hashrate == 0.0:
                            if 'CRASHED GPU {}'.format(idx + 1) not in return_dict['flags_status']:
                                return_dict['flags_status'].append('CRASHED GPU {}'.format(idx + 1))
                        return_dict['total_hashrate'] += hashrate
                    return_dict['total_hashrate'] = round(return_dict['total_hashrate'], 3)
            #    mem_states_string = mongo_dict['memstates']
            #     res_list_mem_states = [int(s) for s in re.findall(r'\d+', mem_states_string)]
            #     if res_list_mem_states:
            #         for idx, mem_state in enumerate(res_list_mem_states):
            #             if mem_state == 0:
            #                 if 'CRASHED GPU {}'.format(idx + 1) not in return_dict['flags_status']:
            #                     return_dict['flags_status'].append('CRASHED GPU {}'.format(idx + 1))
            #
            else:
                return_dict['flags_status'].append('CRASHED RIG')
        mem_string = mongo_dict['mem']
        res_list = [int(s) for s in re.findall(r'\d+', mem_string)]
        if res_list:
            return_dict['mem'] = [int(x) for x in res_list]

        # CONFIG STATUS
        return_dict['config_status'] = mongo_dict.get('config_status')
        return_dict['send_remote'] = mongo_dict.get('send_remote')

        if not return_dict['send_remote'] and return_dict['config_status'] == 'singlerig':
            return_dict['config_s'] = "L"
        else:
            return_dict['config_s'] = "R"

        days, hours, minutes, sec = days_hours_minutes_from_sec(int(mongo_dict.get('uptime')))
        return_dict['uptime'] = "".join("{}D {}H {}M {}S").format(days, hours, minutes, sec)

        if mongo_dict.get('rx_kbps'):
            return_dict['rx_kbps'] = mongo_dict.get('rx_kbps')
        if mongo_dict.get('tx_kbps'):
            return_dict['tx_kbps'] = mongo_dict.get('tx_kbps')

        if float(return_dict['rx_kbps']) >= Config.APP_RX_BAD_VALUE or float(
                return_dict['tx_kbps']) >= Config.APP_TX_BAD_VALUE:
            return_dict['flags_status'].append('RX/TX TOO HIGH')

        res_list_cpu = [int(s) for s in re.findall(r'\d+', mongo_dict.get('cpu_temp'))]
        if res_list_cpu:
            return_dict['cpu_temp'] = int(res_list_cpu[0])

        # result_dict['temp'] = result_dict['temp'].replace("'","")
        gpu_temps = re.findall(r"[-+]?\d*\.\d+|\d+", mongo_dict['temp'])
        # gpu_temps = result_dict['temp'].strip().split(' ')
        if gpu_temps:
            return_dict['gpu_temps'] = [float(x) for x in gpu_temps]
        # if return_dict['gpu_temps']:
        #     for temp in return_dict['gpu_temps']:
        #         if temp > int(Config.APP_SETTINGS_OVERHEAT):
        #             if 'OVERHEAT' not in return_dict['flags_status']:
        #                 return_dict['flags_status'].append('OVERHEAT')

        # POWERTUNE
        pwrtune = re.findall(r"[-+]?\d*\.\d+|\d+", mongo_dict['powertune'])
        # gpu_temps = result_dict['temp'].strip().split(' ')
        if pwrtune:
            return_dict['powertune'] = [float(x) for x in pwrtune]

        gpus_string = mongo_dict['gpus']
        res_list = [int(s) for s in re.findall(r'\d+', gpus_string)]
        if res_list:
            return_dict['gpus'] = res_list[0]

        ##  FANS
        fanrpm_string = mongo_dict['fanrpm']
        res_list = [int(s) for s in re.findall(r'\d+', fanrpm_string)]
        if res_list:
            return_dict['fanrpm'] = [int(x) for x in res_list]

        fanrpm_string = mongo_dict['fanpercent']
        res_list = [int(s) for s in re.findall(r'\d+', fanrpm_string)]
        if res_list:
            return_dict['fanpercent'] = [int(x) for x in res_list]

        # Core
        core_string = mongo_dict['core']
        res_list = [int(s) for s in re.findall(r'\d+', core_string)]
        if res_list:
            return_dict['core'] = [int(x) for x in res_list]

        core_default_string = mongo_dict['default_core']
        res_list = [int(s) for s in re.findall(r'\d+', core_default_string)]
        if res_list:
            return_dict['default_core'] = [int(x) for x in res_list]

        received_at_utc = mongo_dict['received_at']
        received_at_utc_local = curr_time_non_naive(received_at_utc)
        now_local = curr_time_naive(datetime.datetime.utcnow())
        dif = now_local - received_at_utc_local
        return_dict['last_request'] = all_min_from_td(dif)

        if all_min_from_td(dif) <= int(Config.APP_SETTINGS_PERIOD_TO_LIVE):
            return_dict['is_off'] = False
            if mongo_dict['miner_hashes'] and mongo_dict['miner_hashes'] is not None:
                # hashes = result_dict['miner_hashes']
                miner_hashes_list = re.findall(r"[-+]?\d*\.\d+|\d+", mongo_dict['miner_hashes'])
                if miner_hashes_list:
                    for _hash in return_dict['miner_hashes']:
                        if _hash > 0.0:
                            return_dict['gpus_alive'] += 1

    return return_dict


def get_unique_hostnames(panel_name):
    if is_panel_exist(panel_name=panel_name):
        collection = mongo.db[panel_name]
        return collection.find({}).distinct('hostname')
    else:
        return []


def get_list_of_not_hidden_rigs(panel_name):
    """Get list of all rigs using APP_SETTINGS_PERIOD_TO_LIVE to define aliveness=)
    if poll_name is not give will count for all polls
    """
    alive_rigs_list = []
    all_coll_names = mongo.db.collection_names()
    if panel_name in all_coll_names:
        collection = mongo.db[str(panel_name)]
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
                if days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    alive_rigs_list.append(host)
    return alive_rigs_list


def get_list_of_hostnames_with_crashed_gpus(panel_name):
    hosts_list = []
    all_coll_names = mongo.db.collection_names()
    if panel_name in all_coll_names:
        collection = mongo.db[str(panel_name)]
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
                        if len(stripped) == 0:
                            gpu_hash = float(hashes)
                            if gpu_hash == 0.0:
                                hosts_list.append(host)
                        elif len(stripped) >= 2:
                            for _hash in stripped:
                                if (float(_hash)) == 0.0:
                                    hosts_list.append(host)
    return hosts_list


def get_list_of_offline_rigs(panel_name):
    offline_rigs_list = []
    all_coll_names = mongo.db.collection_names()
    if panel_name in all_coll_names:
        collection = mongo.db[str(panel_name)]
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
                if all_min_from_td(dif) > int(Config.APP_SETTINGS_PERIOD_TO_LIVE) and days < int(
                        Config.APP_SETTINGS_PERIOD_TO_HIDE_RIG):
                    offline_rigs_list.append(host)
                total_hash = re.findall(r"[-+]?\d*\.\d+|\d+", dict_res['hash'])
                if total_hash:
                    if float(total_hash[0]) == 0.0:
                        if host not in offline_rigs_list:
                            offline_rigs_list.append(host)

    a = 2
    return offline_rigs_list


def get_location_by_hostname(hostname):
    location = 0
    if LocationFieldPanel.query.filter_by(hostname=hostname).first() is not None:
        loc = LocationFieldPanel.query.filter_by(hostname=hostname).first()
        location = loc.number
    return location


# Attack Detection
def get_list_of_rigs_under_attack(panel_name):
    rigs_under_attack_list = []
    all_coll_names = mongo.db.collection_names()
    if panel_name in all_coll_names:
        collection = mongo.db[str(panel_name)]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'hash': 1, "rx_kbps": 1, "tx_kbps": 1}) \
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
                    rx_kbps = re.findall(r"[-+]?\d*\.\d+|\d+", dict_res['rx_kbps'])
                    tx_kbps = re.findall(r"[-+]?\d*\.\d+|\d+", dict_res['tx_kbps'])
                    if rx_kbps:
                        if float(rx_kbps[0]) >= Config.APP_RX_BAD_VALUE:
                            rigs_under_attack_list.append(host)
                    if tx_kbps:
                        if float(tx_kbps[0]) >= Config.APP_TX_BAD_VALUE:
                            if host not in rigs_under_attack_list:
                                rigs_under_attack_list.append(host)

    a = 2
    return rigs_under_attack_list


def get_num_of_rigs_under_attack(panel_name=None):
    num_of_rigs_under_attack = 0
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')  # Uniquie Hostnames = Rigs
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'hash': 1, "rx_kbps": 1, "tx_kbps": 1}) \
                .sort('received _at', flask_pymongo.DESCENDING) \
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
                    rx_kbps = re.findall(r"[-+]?\d*\.\d+|\d+", dict_res['rx_kbps'])
                    tx_kbps = re.findall(r"[-+]?\d*\.\d+|\d+", dict_res['tx_kbps'])
                    if rx_kbps:
                        if float(rx_kbps[0]) >= Config.APP_RX_BAD_VALUE or float(tx_kbps[0]) >= Config.APP_TX_BAD_VALUE:
                            num_of_rigs_under_attack += 1
    return num_of_rigs_under_attack
