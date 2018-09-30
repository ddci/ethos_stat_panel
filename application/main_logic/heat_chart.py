import re

from application.main_logic.dashboards import get_average_gpu_temperature, get_num_and_list_of_alive_panels, \
    get_num_of_gpus, get_num_of_alive_gpus, get_num_of_all_rigs

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-31"
__app__ = "statswebapp"
__status__ = "Development"

import flask_pymongo
from config import Config
import datetime
import time
from application.main_logic.functions import curr_time_naive, curr_time_non_naive, days_hours_minutes, all_min_from_td
from .. import mongo, redis_store


class HeatDashboard:

    def __init__(self):
        measure_time_start = time.time()

        num_of_gpus = redis_store.get('main_dashboard:num_of_gpus')
        if num_of_gpus:
            self.num_of_gpus = int(num_of_gpus)

        num_of_alive_gpus = redis_store.get('main_dashboard:num_of_alive_gpus')
        if num_of_alive_gpus:
            self.num_of_alive_gpus = int(num_of_alive_gpus)

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

        redis_res_dict = redis_store.hgetall("heat_chart:all_temp_info_dict")

        self.ok_gpus = redis_res_dict.get('OK')
        self.yellow_gpus = redis_res_dict.get('YELLOW')
        self.red_gpus = redis_res_dict.get('RED')
        self.cold_gpus = redis_res_dict.get('COLD')

        self.list_of_alive_panels = redis_store.lrange('sidebar_info:list_of_alive_panels', 0, -1)
        self.panels_temp_info_dict = {}
        for panel_name in self.list_of_alive_panels:
            self.panels_temp_info_dict[str(panel_name)] = redis_store.hgetall("heat_chart:{}:temp_info_dict"
                                                                              .format(str(panel_name)))

        measure_time_end = time.time()
        self.execution_time = round((measure_time_end - measure_time_start), 2)


def get_gpus_temp_info_dict(panel_name=None):
    gpu_temp_info = {}
    gpu_temp_info["COLD"] = 0
    gpu_temp_info["OK"] = 0
    gpu_temp_info["YELLOW"] = 0
    gpu_temp_info["RED"] = 0
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
                        split = re.findall(r"[-+]?\d*\.\d+|\d+", temps)
                        temps_list = [float(x) for x in split]
                        if temps_list:
                            for temp in temps_list:
                                if temp > 0.00 and temp <= 40.00:
                                    gpu_temp_info["COLD"] += 1
                                if temp > 40.00 and temp < 60.00:
                                    gpu_temp_info["OK"] += 1
                                if temp >= 60.00 and temp < 80.00:
                                    gpu_temp_info["YELLOW"] += 1
                                if temp >= 80.00 and temp < 120.00:
                                    gpu_temp_info["RED"] += 1

    return gpu_temp_info
