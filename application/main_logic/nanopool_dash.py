import datetime
import json
import time

import copy

import os
import pandas as pd
import requests
from twilio.rest import Client

from application import redis_store
from application.main_logic.panel_info import get_num_of_rigs_under_attack
from config import Config

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-02-19"
__app__ = "statswebapp"
__status__ = "Development"


class NanopoolDashboardMain:

    def __init__(self):
        measure_time_start = time.time()
        self.list_of_nanopool_wallets = redis_store.lrange('nanopool_dash:list_of_nanopool_wallets', 0, -1)
        measure_time_end = time.time()
        self.execution_time = round((measure_time_end - measure_time_start), 2)


class NanopoolDashboardWallet:

    def __init__(self, proxywallet):
        measure_time_start = time.time()
        # 12345678
        self.proxywallet = proxywallet
        self.hashrate = redis_store.get("nanopool_wallet_info:{}:hashrate".format(str(proxywallet)))
        self.balance = redis_store.get("nanopool_wallet_info:{}:balance".format(str(proxywallet)))
        self.all_paid_today = redis_store.get("nanopool_wallet_info:{}:all_paid_today".format(str(proxywallet)))

        json_str_payments_24_table = redis_store.get("nanopool_wallet_info:{}:payments_24_table"
                                                     .format(str(proxywallet)))
        self.payments_24_table_list = json.loads(json_str_payments_24_table)

        json_str_shares_table = redis_store.get("nanopool_wallet_info:{}:shares_table"
                                                .format(str(proxywallet)))
        self.shares_table = json.loads(json_str_shares_table)

        json_str_report_by_days = redis_store.get("nanopool_wallet_info:{}:all_payments"
                                                .format(str(proxywallet)))
        self.all_payments = json.loads(json_str_report_by_days)

        json_str_report_by_days = redis_store.get("nanopool_wallet_info:{}:report_by_days"
                                                .format(str(proxywallet)))
        self.report_by_days = json.loads(json_str_report_by_days)

        measure_time_end = time.time()
        self.execution_time = round((measure_time_end - measure_time_start), 2)


class NanopoolDashboardWalletPaymentsForDate:

    def __init__(self, proxywallet, date):
        measure_time_start = time.time()
        self.hashrate = redis_store.get("nanopool_wallet_info:{}:hashrate".format(str(proxywallet)))
        self.balance = redis_store.get("nanopool_wallet_info:{}:balance".format(str(proxywallet)))

        json_str_all_payments = redis_store.get("nanopool_wallet_info:{}:all_payments"
                                                .format(str(proxywallet)))
        self.all_payments = {}
        self.all_paid = 0.0
        all_payments = json.loads(json_str_all_payments)
        if date in all_payments:
            if all_payments[date].get("tx_list"):
                self.all_payments = all_payments[date]['tx_list']
                for payment in self.all_payments:
                    if payment.get("amount"):
                        self.all_paid += float(payment['amount'])

        measure_time_end = time.time()
        self.execution_time = round((measure_time_end - measure_time_start), 2)


def is_nanopool_wallet_exists(proxywallet):
    list_of_nanopool_wallets = redis_store.lrange('nanopool_dash:list_of_nanopool_wallets', 0, -1)
    if proxywallet in list_of_nanopool_wallets:
        return True
    else:
        return False


def dict_with_datetime_keys_to_str(input_dict):
    output_dict = {}
    for key in input_dict.keys():
        if type(key) is not str:
            try:
                output_dict[str(key.strftime("%Y-%m-%d"))] = input_dict[key]
            except:
                pass
    return output_dict
