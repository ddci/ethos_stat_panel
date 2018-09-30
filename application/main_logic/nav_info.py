import time

from application.main_logic.panel_info import get_num_of_rigs_under_attack

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-11"
__app__ = "statswebapp"
__status__ = "Development"

from .. import mongo, redis_store
import requests


class SidebarInfo:

    def __init__(self):
        measure_time_start = time.time()
        # self.list_of_alive_panels = get_num_and_list_of_alive_panels()[1]
        self.num_of_alive_rigs = {}
        self.num_of_rigs = {}
        self.num_of_offline_gpus = {}

        self.list_of_alive_panels = redis_store.lrange('sidebar_info:list_of_alive_panels', 0, -1)

        num_of_rigs = redis_store.hgetall("sidebar_info:num_of_rigs")
        if num_of_rigs:
            self.num_of_rigs = num_of_rigs

        num_of_alive_rigs = redis_store.hgetall("sidebar_info:num_of_alive_rigs")
        if num_of_alive_rigs:
            self.num_of_alive_rigs = num_of_alive_rigs

        num_of_offline_gpus = redis_store.hgetall("sidebar_info:num_of_offline_gpus")
        if num_of_offline_gpus:
            self.num_of_offline_gpus = num_of_offline_gpus

        measure_time_end = time.time()
        self.execution_time = round((measure_time_end - measure_time_start), 2)


class HeaderNavbarInfo:
    def __init__(self):
        num_of_rigs_under_attack = redis_store.get("main_dashboard:num_of_rigs_under_attack")
        if num_of_rigs_under_attack:
            self.num_of_rigs_under_attack = int(num_of_rigs_under_attack)

        self.eth_btc, self.eth_usd, self.eth_eur = 22, 22, 22

# def get_eht_price():
#     url = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=BTC,USD,EUR"
#     response = requests.post(url)
#     json_dict = response.json()
#     return json_dict.get('BTC'), json_dict.get('USD'), json_dict.get('EUR')
