from flask import request
from app import app
from model.tweet_model import tweet_model
obj = tweet_model()

@app.route("/tweet/all")
def all_tweets():
    return obj.all_tweets()

@app.route("/hashtag")
def hashtag_dates():
    hashtag = request.args['hashtag']
    start = request.args['start']
    end = request.args['end']
    print(start, end)
    return obj.hashtag_dates(hashtag,start,end)

@app.route("/wordfind/<name>")
def find_word(name):
    return obj.word_find(name)