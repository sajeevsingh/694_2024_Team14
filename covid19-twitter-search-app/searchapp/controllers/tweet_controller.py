import requests
from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from model.tweet_model import tweet_model
from datetime import datetime
obj = tweet_model()


blp = Blueprint("tweets", __name__, description="Operations on tweets resource")

@blp.route("/api/v1/tweets")
class GetAllTweets(MethodView):

    def get(self):
        try:
            return jsonify(obj.all_tweets()), 200
        except KeyError:
            abort(404, message="Tweet Not Found.")

@blp.route("/api/v1/trending_hashtags")
class GetTopHashtags(MethodView):

    def get(self):
        try:
            time_stamp_str = request.args.get('time_stamp')
            time_stamp = datetime.fromisoformat(time_stamp_str)
            return jsonify(obj.most_trending_hashtags(time_stamp)),200
        except KeyError:
            abort(404, message="No Hashtags Found.")

@blp.route("/api/v1/tweets/<string:tweet_text>")
class FindTweets(MethodView):

    def get(self, user_name):
        try:
            return jsonify(obj.word_find(tweet_text)), 200
        except KeyError:
            abort(404, message="Tweet Not Found.")
