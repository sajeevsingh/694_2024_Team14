import requests
from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint("universities", __name__, description="Operations on universiy resource")

@blp.route("/api/v1/universities/country/<string:country_name>")
class University(MethodView):

    def get(self, country_name):

        try:
            API_URL = "http://universities.hipolabs.com/search?country="
            #search = request.args.get('country')
            # get it from external source
            r = requests.get(f"{API_URL}{country_name}")
            return jsonify(r.json()), 200
        except KeyError:
            abort(500, message="error invoking api endpoint.")