

import json
from datetime import datetime
import pymongo


myclient = pymongo.MongoClient("mongodb://root:pass@localhost:27017/")
db = myclient["tweets"]
col = db["tweets"]

tweets = {}
users = {}

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
        transformed['user_name'] = transformed['user'].get('name') ##
        transformed['is_user_verified'] = transformed['user'].get('verified')
        
    user_info = transformed.pop('user', None)
    if user_info:
        user_id_str = user_info.get('id_str')
        users[user_id_str] = user_info
   
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
        retweet_user_info = transformed['retweeted_status'].get('user',None)
        if retweet_user_info:
            retweet_user_id_str = retweet_user_info.get('id_str')
            if retweet_user_id_str not in users:
                users[retweet_user_id_str] = retweet_user_info
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
        retweet_user_info = transformed['quoted_status'].get('user',None)
        if retweet_user_info:
            retweet_user_id_str = retweet_user_info.get('id_str')
            if retweet_user_id_str not in users:
                users[retweet_user_id_str] = retweet_user_info
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
   
    return transformed

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

import psycopg2
from psycopg2 import extras
from datetime import datetime

date_format = "%a %b %d %H:%M:%S %z %Y"

user_records = [
    (
        user_details["id_str"],
        user_details.get("name"),
        user_details.get("screen_name"),
        user_details.get("location", None),
        user_details.get("description", None),
        user_details.get("verified", False),
        user_details.get("followers_count", 0),
        user_details.get("friends_count", 0),
        user_details.get("listed_count", 0),
        user_details.get("favourites_count", 0),
        user_details.get("statuses_count", 0),
        datetime.strptime(user_details["created_at"], date_format) if user_details.get("created_at") else None,
        user_details.get("lang")
    )
    for user_details in users.values()
]


db_config = {"database" : 'users',
"user" : 'postgres',
"password" : 'postgres',  
"host" : 'localhost', 
"port" : '5432' 
} 


conn = psycopg2.connect(**db_config)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS users;")
cur.execute( """
CREATE TABLE IF NOT EXISTS users( id_str VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    screen_name VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    verified BOOLEAN,
    followers_count INTEGER,
    friends_count INTEGER,
    listed_count INTEGER,
    favourites_count INTEGER,
    statuses_count INTEGER,
    created_at TIMESTAMP,
    lang VARCHAR(10)
);""")

conn.commit()

try:
    insert_query = """INSERT INTO users (id_str,name,screen_name,location,description,verified,followers_count,friends_count,listed_count,favourites_count,statuses_count,created_at,lang) 
    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id_str) DO NOTHING; """
    extras.execute_batch(cur,insert_query,user_records,page_size = 100)
    conn.commit()
    
    

except Exception as e:
    print("Failed")
    conn.rollback()
    

cur.close()
conn.close()