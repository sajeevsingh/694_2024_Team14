from pymongo import MongoClient
from datetime import timedelta
from searchapp.config.config import mongodb_config
from searchapp.cache.lru_cache_ttl import LRUCacheWithTTL
import time
import logging

MAX_CACHE_SIZE = 2
DEFAULT_CACHE_TTL = 30

class tweet_model():

    def __init__(self):
        self.mongoClient = MongoClient(host=mongodb_config['host'], port=mongodb_config['port'], username=mongodb_config['username'], password=mongodb_config['password'], authSource=mongodb_config['authSource'])
        self.db = self.mongoClient["tweets"]
        self.tweet_collection = self.db["tweets"]
        self.cache = LRUCacheWithTTL(max_size=MAX_CACHE_SIZE, ttl=DEFAULT_CACHE_TTL)
        #self.cache.reload_from_checkpoint()

    def checkpoint_thread(self):
        while True:
            time.sleep(300)
            self.cache.periodically_checkpoint()

    def query_tweets_by_keyword(self, keyword, lang='en'):

        cache_key = f"{keyword}-{lang}"
        logging.info(f" cache key : {cache_key}")

        if self.cache.get(cache_key) is None:

            start_time = time.time()
            query = {
                "$text": {
                    "$search": keyword
                },
                "is_retweet": False,
                "lang": lang
            }
            projection = {"score": {"$meta": "textScore"}}
            sort_by = [("score", {"$meta": "textScore"}), ("created_at", -1)]

            result = list(self.tweet_collection.find(query, projection).sort(sort_by).limit(100))

            if len(result) > 0:
                self.cache.put(cache_key, result)

            end_time = time.time()
            delta = end_time - start_time
            logging.info(f"Time taken to retrieve from Database is {delta} seconds")

        else:

            start_time = time.time()
            result = self.cache.get(cache_key)
            end_time = time.time()
            delta = end_time - start_time
            logging.info(f"Time taken to retrieve from Cache is {delta} seconds")

        return result
    
    def query_tweets_by_user_id(self, user_id):
        query = {
            "user_id": user_id
        }    
        sort_by = [("created_at", -1)]
        result = self.tweet_collection.find(query).sort(sort_by).limit(100)
        return list(result)
    
    def query_tweets_by_user_screen_name(self, user_screen_name):
        query = {
            "user_screen_name": user_screen_name
        }    
        sort_by = [("created_at", -1)]
        result = self.tweet_collection.find(query).sort(sort_by).limit(100)
        return list(result)

    def most_active_users(self, max_timestamp):
        end_timestamp = max_timestamp
        start_timestamp = max_timestamp - timedelta(hours=1)

        pipeline = [
        { "$match": { "created_at": { "$gte": start_timestamp, "$lte": end_timestamp } } },
        { "$group": { "_id": { "user_id": "$user_id", "user_screen_name": "$user_screen_name" }, "count": { "$sum": 1 } } },
        { "$project": { "_id": 0, "user_id": "$_id.user_id", "user_screen_name": "$_id.user_screen_name", "count": 1 } },
        { "$sort": { "count": -1 } },
        { "$limit": 50 }
        ]    
        result = self.tweet_collection.aggregate(pipeline)    
        return list(result)
    
    def most_trending_hashtags(self, timestamp):
        end_timestamp = timestamp
        start_timestamp = timestamp - timedelta(hours=1)
        pipeline = [
            { "$match": { "created_at": { "$gte": start_timestamp, "$lte": end_timestamp } } },
            { "$unwind": "$hashtags" }, 
            { "$group": { "_id": "$hashtags", "count": { "$sum": 1 } } },
            { "$project": { "_id": 0, "hashtag": "$_id", "count": 1 } },
            { "$sort": { "count": -1 } } ,
            { "$limit": 50 } 
        ]
    
        result = self.tweet_collection.aggregate(pipeline)
    
        return list(result)
    
    def query_retweets_by_tweet_id(self,tweet_id):
    
        query = {
            "parent_id": tweet_id,  
            "is_retweet": True  
        }
        sort_by = [("created_at", -1)]
        result = self.tweet_collection.find(query).sort(sort_by).limit(100)
        return list(result)