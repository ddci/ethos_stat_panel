from application.main_logic.panel_info import PanelInfo

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-16"
__app__ = "statswebapp"
__status__ = "Development"


def get_status_panel_ajax(pool_name):
    pool_info = PanelInfo(pool_name)
    response = {'data': []}
    if pool_info:
        for rigvalue in pool_info.rigs_info.values():
            response['data'].append([rigvalue.is_off, rigvalue.hostname, rigvalue.miner,
                                     str(rigvalue.gpus_alive) + "/" + str(rigvalue.gpus),
                                     rigvalue.flags_status, '000000000000000000000000000000<span class="badge bg-red">'
                                     + str(rigvalue.gpu_temps[0]) + '<sup style="">°</sup></span>',
                                     rigvalue.miner_hashes,
                                     rigvalue.ip_address, rigvalue.status])
        # response['data']
    return response
