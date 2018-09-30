import logging
import urllib
import datetime
import json
import urllib.parse

import pymongo
from flask import request
from .. import mongo
from . import main

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-18"
__app__ = "mdbreceiver"
__status__ = "Development"


@main.route('/send')
def receive_data():
    try:
        hostname = request.args.get('hostname')
        if not hostname:
            logging.exception("No hostname given.")
            raise Exception
        url_style = request.args.get('url_style')
        hash_from_request = request.args.get('hash')
        logging.info("Received data from {} rig {}".format(hash_from_request[:6], hostname))
        if hash_from_request == "":
            logging.info("Received data from rig {} with no hash(info for separating rigs) provided.".format(hostname))
            logging.info("Possibly new or rebooted rig.")
        json_data = urllib.parse.unquote_plus(url_style)
        json_decoded_from_str = json.loads(json_data)
        all_coll_names = mongo.db.collection_names()
        if hash_from_request[:6] in all_coll_names:
            collection = mongo.db[hash_from_request[:6]]
            json_decoded_from_str['received_at'] = datetime.datetime.utcnow()

            collection.replace_one({"hostname": str(hostname)}, json_decoded_from_str, upsert=True)
        else:
            collection = mongo.db[hash_from_request[:6]]
            json_decoded_from_str['received_at'] = datetime.datetime.utcnow()

            collection.replace_one({"hostname": str(hostname)}, json_decoded_from_str, upsert=True)
            collection.create_index([("received_at", pymongo.DESCENDING)], background=True)
            collection.create_index([("hostname", pymongo.DESCENDING)], background=True)
            collection.create_index([("hostname", pymongo.ASCENDING)], background=True)

        # collection.delete_many({"hostname": hostname})
        # collection.insert_one(json_decoded_from_str)

        logging.info("Inserted data in MongoDB into collection {}".format(hash_from_request[:6]))
        return 'Received data from group {} machine {}'.format(hash_from_request,hostname)
    except Exception as e:
        logging.exception("Failed to parse or to add to Mongo")
        print(e)
        return 'Failed'
