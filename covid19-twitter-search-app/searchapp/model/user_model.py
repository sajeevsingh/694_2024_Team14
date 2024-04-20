import psycopg2
import json
from datetime import datetime, timedelta
from config.config import postgresdb_config
from collections import OrderedDict
import time

#cache = OrderedDict()
#MAX_CACHE_SIZE = 1000
#DEFAULT_CACHE_TTL = 3600

def get_timestamp():
    return int(datetime.utcnow().timestamp())

class user_model():

    def __init__(self):
        self.conn = psycopg2.connect(database=postgresdb_config['database'], user=postgresdb_config['username'], password=postgresdb_config['password'], host=postgresdb_config['host'], port=postgresdb_config['port'])
        self.conn.autocommit = True
        self.cur = self.conn.cursor(dictionary=True)
        self.cache = OrderedDict()
        self.MAX_CACHE_SIZE = 1000
        self.DEFAULT_CACHE_TTL = 3600