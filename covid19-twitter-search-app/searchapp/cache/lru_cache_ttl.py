import os
import pickle
from collections import OrderedDict
import time
from datetime import datetime, timedelta
import logging

CHECKPOINT_DIR = os.environ.get("CHECKPOINT_DIR", "/src/app")

class LRUCacheWithTTL:

    def __init__(self, max_size, ttl):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.last_checkpoint_time = datetime.now()
        #self.reload_from_checkpoint()

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

        # Create the pickle file if it doesn't exist
        if not os.path.exists(checkpoint_file):
            with open(checkpoint_file, "wb") as f:
                pickle.dump({}, f)

        with open(checkpoint_file, "rb+") as f:
            # Load the existing data from the file
            existing_data = pickle.load(f)
            # Update the data with the current cache
            existing_data.update(self.cache)
            # Move the file pointer to the beginning
            f.seek(0)
            # Write the updated data back to the file
            pickle.dump(existing_data, f)
            # Truncate any remaining data after the updated data
            f.truncate()


    def reload_from_checkpoint(self):
        logging.info("Reloading cache at the start of the application.")
        checkpoint_file = os.path.join(CHECKPOINT_DIR, "cache_checkpoint.pkl")
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, "rb") as f:
                self.cache = OrderedDict(pickle.load(f))

    def periodically_checkpoint(self, interval = 300):
        if datetime.now() - self.last_checkpoint_time > timedelta(seconds=interval):
            self.checkpoint_to_disk()
            self.last_checkpoint_time = datetime.now()

    def __str__(self):
        return str(self.cache)