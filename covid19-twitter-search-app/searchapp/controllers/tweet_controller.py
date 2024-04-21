import requests
from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from model.tweet_model import tweet_model
obj = tweet_model()

blp = Blueprint("tweets", __name__, description="Operations on tweets resource")

@blp.route("/api/v1/tweets")
class GetAllTweets(MethodView):

    def get(self):
        try:
            return jsonify(obj.all_tweets()), 200
        except KeyError:
            abort(404, message="Tweet Not Found.")

@blp.route("/api/v1/tweets")
class GetHashtagsByDate(MethodView):

    def get(self, user_name):
        try:
            hashtag = request.args['hashtag']
            start = request.args['start']
            end = request.args['end']
            print(start, end)
            return jsonify(obj.hashtag_dates(hashtag, start, end)), 200
        except KeyError:
            abort(404, message="Hashtags Not Found.")

@blp.route("/api/v1/tweets/<string:tweet_text>")
class FindTweets(MethodView):

    def get(self, user_name):
        try:
            return jsonify(obj.word_find(tweet_text)), 200
        except KeyError:
            abort(404, message="Tweet Not Found.")
