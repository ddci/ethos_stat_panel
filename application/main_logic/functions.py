import datetime

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-10"
__app__ = "statswebapp"
__status__ = "Development"

from dateutil import tz
from .. import mongo

from_zone = tz.tzutc()
to_zone = tz.tzlocal()


def curr_time_naive(time_naive):
    utc = time_naive.replace(tzinfo=from_zone)
    now_local = utc.astimezone(to_zone)
    return now_local


def curr_time_non_naive(time):
    local = time.astimezone(to_zone)
    return local


def is_panel_exist(panel_name):
    all_coll_names = mongo.db.collection_names()
    if panel_name is None:
        return False
    elif panel_name in all_coll_names:
        return True
    else:
        return False


def list_from_all_status_flags(in_dict):
    # Chek this twice NOT all data provided
    result_list = []
    if in_dict['defunct'] and in_dict['defunct'] is not None and in_dict['defunct'] == 1:
        result_list.append('DEFUNCT')
    if in_dict['overheat'] and in_dict['overheat'] is not None and in_dict['overheat'] == 1:
        result_list.append('OVERHEAT')
    if in_dict['adl_error'] and in_dict['adl_error'] is not None:
        result_list.append('ADL')
    if in_dict['autorebooted'] and in_dict['autorebooted'] is not None and in_dict['autorebooted'] == str(1):
        result_list.append('REBOOTED')
    if in_dict['updating'] and in_dict['updating'] is not None and in_dict['updating'] == str(1):
        result_list.append('UPDATING')
    if in_dict['throttled'] and in_dict['throttled'] is not None:
        result_list.append('LOW HASHRATE &nbsp <br> &nbsp CAUSED BY HEAT')
    return result_list


def days_hours_minutes(td):
    return td.days, td.seconds // 3600, (td.seconds // 60) % 60


def days_hours_minutes_from_sec(time):
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    return day, hour, minutes, seconds


def all_min_from_td(td):
    days, hours, minutes = days_hours_minutes(td)
    minutes = (days * 24 * 60) + hours * 60 + minutes
    return minutes
