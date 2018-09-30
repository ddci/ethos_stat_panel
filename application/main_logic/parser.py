__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-16"
__app__ = "statswebapp"
__status__ = "Development"


def parse_json_to_dict(dict_from_mongo):
    result_dict = {}
    if dict_from_mongo.get('defunct'):
        result_dict['defunct'] = bool(dict_from_mongo.get('defunct'))
    else:
        result_dict['defunct'] = False

    if dict_from_mongo.get('off'):
        result_dict['off'] = bool(int(dict_from_mongo.get('off')))
    else:
        result_dict['off'] = False

    if dict_from_mongo.get('allowed'):
        result_dict['allowed'] = bool(dict_from_mongo.get('allowed'))
    else:
        result_dict['allowed'] = False

    if dict_from_mongo.get('overheat'):
        result_dict['overheat'] = bool(dict_from_mongo.get('overheat'))
    else:
        result_dict['overheat'] = False

    if dict_from_mongo.get('pool_info'):
        result_dict['pool_info'] = dict_from_mongo.get('pool_info')
    else:
        result_dict['pool'] = ""

    if dict_from_mongo.get('pool'):
        result_dict['poll'] = dict_from_mongo.get('poll')
    else:
        result_dict['poll'] = ""

    if dict_from_mongo.get('miner_version'):
        result_dict['miner_version'] = dict_from_mongo.get('miner_version')
    else:
        result_dict['miner_version'] = ""

    if dict_from_mongo.get('rx_kbps'):
        result_dict['rx_kbps'] = float(dict_from_mongo.get('rx_kbps'))
    else:
        result_dict['rx_kbps'] = 0.0

    if dict_from_mongo.get('tx_kbps'):
        result_dict['tx_kbps'] = float(dict_from_mongo.get('tx_kbps'))
    else:
        result_dict['tx_kbps'] = 0.0

    if dict_from_mongo.get('kernel'):
        result_dict['kernel'] = dict_from_mongo.get('kernel')
    else:
        result_dict['kernel'] = ""

    if dict_from_mongo.get('boot_mode'):
        result_dict['boot_mode'] = dict_from_mongo.get('boot_mode')
    else:
        result_dict['boot_mode'] = ""

    if dict_from_mongo.get('uptime'):
        result_dict['uptime'] = int(dict_from_mongo.get('uptime'))
    else:
        result_dict['uptime'] = 0

    if dict_from_mongo.get('mac'):
        result_dict['mac'] = dict_from_mongo.get('mac')
    else:
        result_dict['mac'] = ""

    if dict_from_mongo.get('hostname'):
        result_dict['hostname'] = dict_from_mongo.get('hostname')
    else:
        result_dict['hostname'] = ""

    if dict_from_mongo.get('rack_loc'):
        result_dict['rack_loc'] = dict_from_mongo.get('rack_loc')
    else:
        result_dict['rack_loc'] = ""

    if dict_from_mongo.get('ip'):
        result_dict['ip'] = dict_from_mongo.get('ip')
    else:
        result_dict['ip'] = ""

    if dict_from_mongo.get('manu'):
        result_dict['manu'] = dict_from_mongo.get('manu')
    else:
        result_dict['manu'] = ""

    if dict_from_mongo.get('mobo'):
        result_dict['mobo'] = dict_from_mongo.get('mobo')
    else:
        result_dict['mobo'] = ""

    if dict_from_mongo.get('lan_chip'):
        result_dict['lan_chip'] = dict_from_mongo.get('lan_chip')
    else:
        result_dict['lan_chip'] = ""

    if dict_from_mongo.get('load'):
        result_dict['load'] = float(dict_from_mongo.get('load'))
    else:
        result_dict['load'] = 0.0

    if dict_from_mongo.get('cpu_temp'):
        result_dict['cpu_temp'] = int(dict_from_mongo.get('cpu_temp'))
    else:
        result_dict['cpu_temp'] = 0

    if dict_from_mongo.get('cpu_name'):
        result_dict['cpu_name'] = dict_from_mongo.get('cpu_name')
    else:
        result_dict['cpu_name'] = ""





