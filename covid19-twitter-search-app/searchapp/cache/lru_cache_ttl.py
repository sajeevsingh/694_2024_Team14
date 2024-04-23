import os
import pickle
from collections import OrderedDict
import time
from datetime import datetime, timedelta
import logging

CHECKPOINT_DIR = os.environ.get("CHECKPOINT_DIR", "/usr/src/app")

class LRUCacheWithTTL:

    def __init__(self, max_size, ttl):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.last_checkpoint_time = datetime.now()

    def get(self, key):
        if key not in self.cache:
            return None
        value, timestamp = self.cache[key]
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            return None
        # Update timestamp of the accessed key
        self.cache[key] = (value, time.time())
        # Move the accessed key to the end to maintain LRU order
        self.cache.move_to_end(key)
        return value

    def put(self, key, value):
        if len(self.cache) >= self.max_size:
            # Evict the least recently used item
            self.cache.popitem(last=False)
        self.cache[key] = (value, time.time())

    def purge_stale_entries(self):
        now = datetime.now()
        for key, (value, timestamp) in list(self.cache.items()):
            if now - timestamp > self.ttl:
                del self.cache[key]

    def checkpoint_to_disk(self):
        logging.info("Periodically saving cache to disk.")
        checkpoint_file = os.path.join(CHECKPOINT_DIR, "cache_checkpoint.pkl")
        with open(checkpoint_file, "wb") as f:
            pickle.dump(self.cache, f)

    def reload_from_checkpoint(self):
        logging.info("Reloading cache at the start of the application.")
        checkpoint_file = os.path.join(CHECKPOINT_DIR, "cache_checkpoint.pkl")
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, "rb") as f:
                self.cache = pickle.load(f)

    def periodically_checkpoint(self, interval = 300):
        if datetime.now() - self.last_checkpoint_time > timedelta(seconds=interval):
            self.checkpoint_to_disk()
            self.last_checkpoint_time = datetime.now()

    def __str__(self):
        return str(self.cache)