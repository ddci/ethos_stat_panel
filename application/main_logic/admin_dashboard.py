import datetime
import json
import time

import flask_pymongo

from application import redis_store, mongo
from application.main_logic.dashboards import get_dual_miners_list
from application.main_logic.functions import curr_time_non_naive, curr_time_naive, days_hours_minutes
from config import Config

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-02-08"
__app__ = "statswebapp"
__status__ = "Development"


class AdminMainDashboard:
    def __init__(self):
        measure_time_start = time.time()
        list_of_alive_panels = redis_store.lrange('sidebar_info:list_of_alive_panels', 0, -1)
        num_of_gpus = redis_store.get('main_dashboard:num_of_gpus')
        if num_of_gpus:
            self.num_of_gpus = int(num_of_gpus)

        num_of_alive_gpus = redis_store.get('main_dashboard:num_of_alive_gpus')
        if num_of_alive_gpus:
            self.num_of_alive_gpus = int(num_of_alive_gpus)
        measure_time_end = time.time()
        self.execution_time = round((measure_time_end - measure_time_start), 2)

        self.panels_info = {}
        for panel_name in list_of_alive_panels:
            self.panels_info[panel_name] = {}
            list_of_pool_info_packed = redis_store.get(
                "admin_main_dashboard:{}:unique_poll_info_list".format(str(panel_name)))
            if list_of_pool_info_packed:

                self.panels_info[panel_name]["list_of_pool_info"] = json.loads(list_of_pool_info_packed)
            else:
                self.panels_info[panel_name]["list_of_pool_info"] = []

            self.panels_info[panel_name]['dual_miners_list'] = redis_store.lrange(
                "admin_main_dashboard:{}:dual_miners_list".format(str(panel_name)), 0, -1)


def get_unique_poll_info_list(panel_name=None):
    ret_list = []
    unique_pool_info_fields = []
    dict_of_rigs_with_unique_pool_info = {}
    if panel_name is None:
        all_coll_names = mongo.db.collection_names()
    else:
        all_coll_names = [str(panel_name)]
    for collection_name in all_coll_names:
        collection = mongo.db[collection_name]
        # find_one returns dict, find  returns cursor
        unique_hostnames = collection.find({}).distinct('hostname')
        for host in unique_hostnames:
            cursor = collection.find({'hostname': str(host)}, {'received_at': 1, 'pool_info': 1}) \
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
                    if dict_res.get("pool_info"):
                        pool_info_str = dict_res.get("pool_info")
                        if dict_of_rigs_with_unique_pool_info.get(pool_info_str) is None:
                            dict_of_rigs_with_unique_pool_info[pool_info_str] = []
                            dict_of_rigs_with_unique_pool_info[pool_info_str].append(host)
                        else:
                            dict_of_rigs_with_unique_pool_info[pool_info_str].append(host)
                        if pool_info_str not in unique_pool_info_fields:
                            unique_pool_info_fields.append(pool_info_str)
                        # pool_info_str_split = pool_info_str.strip().split('\n')

    try:
        if unique_pool_info_fields:
            for pool_info_string in unique_pool_info_fields:
                pool_info_str_split = pool_info_string.strip().split('\n')
                res_dict = {}
                if dict_of_rigs_with_unique_pool_info.get(pool_info_string):
                    res_dict["hosts"] = dict_of_rigs_with_unique_pool_info[pool_info_string]
                    res_dict["amount"] = len(dict_of_rigs_with_unique_pool_info[pool_info_string])
                for _str in pool_info_str_split:
                    two_str = _str.strip().split(' ')
                    res_dict[two_str[0]] = two_str[1]
                ret_list.append(res_dict)
    except Exception as e:
        print(e)
        print("Exception get_list_of_dict_pool_info")
        return []
    return ret_list
