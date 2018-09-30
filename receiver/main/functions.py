import logging
import os
import random

from pymongo.errors import ServerSelectionTimeoutError

__author__ = 'Daniil Nikulin'
__copyright__ = "Copyright 2017"
__license__ = "Apache License 2.0"
__version__ = "1.0"
__maintainer__ = "Daniil Nikulin"
__email__ = "danil.nikulin@gmail.com"
__status__ = "Development"


# ---------
# IMPORTS
# ---------

def is_connected(client):
    try:
        client.server_info()  # force connection on a request as the
        # connect=True parameter of MongoClient seems
        # to be useless here
    except ServerSelectionTimeoutError as err:
        logging.warning("Connections refused:")
        print(err)
        return False
    else:
        return True


def print_received_data(decoded_json, hostname, hash_fromdata):
    print("||||||||||||||||||||||||||||")
    print("HOSTNAME :" + hostname + "\n")
    print("HASH: " + hash_fromdata + "\n")
    for key, value in decoded_json.items():
        print(str(key) + " : " + str(value))
    # print(json_data)
    print("||||||||||||||||||||||||||||")


def save_in_file(json_data):
    path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(path)
    file = open(''.join(random.choice('0123456789ABCDEF') for i in range(16)), 'w+')
    file.write("{}".format(json_data))
