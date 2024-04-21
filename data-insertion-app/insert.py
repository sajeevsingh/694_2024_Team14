

import json
from datetime import datetime
import pymongo


myclient = pymongo.MongoClient("mongodb://root:pass@localhost:27017/")
db = myclient["tweets"]
col = db["tweets"]

tweets = {}


def transform_data(data):

    required_keys = ['id', 'id_str', 'created_at', 'text', 'source', 'in_reply_to_status_id', 'in_reply_to_user_id', 
                 'in_reply_to_screen_name', 'quote_count', 'reply_count', 'retweet_count', 'favorite_count', 'entities',
                 'possibly_sensitive', 'lang', 'user','quoted_status', 'retweeted_status']
    transformed = {key: data.get(key) for key in required_keys if key in data}
   
    if 'created_at' in transformed:
        transformed['created_at'] = datetime.strptime(transformed['created_at'], "%a %b %d %H:%M:%S %z %Y")
   
    # transformed['is_this_a_retweet'] = "yes" if transformed['text'].startswith('RT') else "no"
   
    if 'user' in transformed:
        transformed['user_id'] = transformed['user'].get('id_str')
        transformed['user_screen_name'] = transformed['user'].get('screen_name')
   
    # transformed.pop('user', None)
    hashtags = []
    if 'hashtags' in transformed['entities']:
        hashtags_list = transformed['entities']['hashtags']
        for hashtag_obj in hashtags_list:
            if 'text' in hashtag_obj:
                hashtags.append(hashtag_obj['text'])
    user_mentions = []
    if 'user_mentions' in transformed['entities']:
        user_mentions_list = transformed['entities']['user_mentions']
        for user_mention_obj in user_mentions_list:
            if 'id_str' in user_mention_obj:
                user_mentions.append(user_mention_obj['id_str'])
    
    transformed['user_mention'] = user_mentions
    transformed['hashtags'] = hashtags
    
    if 'retweeted_status' in transformed and transformed['retweeted_status']:
        parent_id = transformed['retweeted_status']['id_str']
        transformed['parent_id'] = parent_id
        transformed['is_retweet'] = True
        transformed['is_quote'] = False
        if parent_id not in tweets:
            transform_data(transformed['retweeted_status'])
        elif tweets[parent_id]['quote_count']+tweets[parent_id]['reply_count']+tweets[parent_id]['retweet_count']+tweets[parent_id]['favorite_count']\
            <transformed['retweeted_status']['quote_count']+transformed['retweeted_status']['reply_count']+transformed['retweeted_status']['retweet_count']+transformed['retweeted_status']['favorite_count']:
                tweets[parent_id]['quote_count'] = transformed['retweeted_status']['quote_count']
                tweets[parent_id]['reply_count'] = transformed['retweeted_status']['reply_count']
                tweets[parent_id]['retweet_count'] = transformed['retweeted_status']['retweet_count']
                tweets[parent_id]['favorite_count'] = transformed['retweeted_status']['favorite_count']
    
    elif 'quoted_status' in transformed and transformed['quoted_status']:
        parent_id = transformed['quoted_status']['id_str']
        transformed['parent_id'] = parent_id
        transformed['is_retweet'] = False
        transformed['is_quote'] = True
        if parent_id not in tweets:
            transform_data(transformed['quoted_status'])
        elif tweets[parent_id]['quote_count']+tweets[parent_id]['reply_count']+tweets[parent_id]['retweet_count']+tweets[parent_id]['favorite_count']\
            <transformed['quoted_status']['quote_count']+transformed['quoted_status']['reply_count']+transformed['quoted_status']['retweet_count']+transformed['quoted_status']['favorite_count']:
                tweets[parent_id]['quote_count'] = transformed['quoted_status']['quote_count']
                tweets[parent_id]['reply_count'] = transformed['quoted_status']['reply_count']
                tweets[parent_id]['retweet_count'] = transformed['quoted_status']['retweet_count']
                tweets[parent_id]['favorite_count'] = transformed['quoted_status']['favorite_count']
    
    
    
        
    transformed = {key: transformed[key] for key in transformed.keys() if key not in ['retweeted_status', 'quoted_status', 'user', 'entities']}
    # transformed.pop('entities', None)
    # transformed.pop('quoted_status', None)
    # transformed.pop('retweeted_status', None)
    
    transformed['_id'] = transformed['id_str']
    if transformed['_id'] not in tweets:
        tweets[transformed['_id']] = transformed
        # col.insert_one(transformed)
   
    return None

with open("./data/corona-out-3", "r") as f1:
    for line in f1:
        try:
            tweet = json.loads(line)
            transform_data(tweet)
        except Exception as e:
            # print(e)
            continue

ids = col.insert_many(list(tweets.values()))

print("Processing complete. Tweets and retweets have been stored in MongoDB.")

col.create_index([("text", pymongo.TEXT)])

col.create_index("user_id")

print("creating index completed")