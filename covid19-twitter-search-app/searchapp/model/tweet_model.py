
import time
pymongo
from pymongo import MongoClient
import json
from datetime import datetime, timedelta
from config.config import mongodb_config
from collections import OrderedDict


def get_timestamp():
    return int(datetime.utcnow().timestamp())

class tweet_model():

    def __init__(self):
        self.mongoClient = MongoClient(host=mongodb_config['mongodb'], port=mongodb_config['port'], username=mongodb_config['username'], password=mongodb_config['password'], authSource=mongodb_config['authSource'])
        self.db = self.mongoClient["final_project_latest"]
        self.tweet_collection = self.db["tweet_collection"]
        self.cache = OrderedDict()
        self.MAX_CACHE_SIZE = 1000
        self.DEFAULT_CACHE_TTL = 3600
