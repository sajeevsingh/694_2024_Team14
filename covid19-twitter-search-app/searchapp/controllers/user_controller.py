import requests
from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from model.user_model import user_model
from model.tweet_model import tweet_model
from datetime import datetime
obj = user_model()
tweet_obj = tweet_model()

blp = Blueprint("users", __name__, description="Operations on User resource")

@blp.route("/api/v1/user/<string:user_name>")
class GetUserByName(MethodView):

    def get(self, user_name):
        try:
            return jsonify(obj.get_specific_user(user_name)), 200
        except KeyError:
            abort(404, message="User Not Found.")

@blp.route("/api/v1/users")
class GetAllUsers(MethodView):

    def get(self):
        try:
            return jsonify(obj.all_user_model()), 200
        except KeyError:
            abort(404, message="User Not Found.")

@blp.route("/api/v1/users/max_time_stamp")
class GetAllUsers(MethodView):

    def get(self):
        try:
            max_time_stamp_str = request.args.get('max_time_stamp')
            max_time_stamp = datetime.fromisoformat(max_time_stamp_str)
            return jsonify(tweet_obj.most_active_users(max_time_stamp)),200
        except KeyError:
            abort(404, message="No Tweets Found.")
