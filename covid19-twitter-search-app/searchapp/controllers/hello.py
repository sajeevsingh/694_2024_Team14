import requests
from flask import Flask, jsonify, request
from app import app

@app.route("/api/v1/universities", methods=['GET'])
def get_all_universities():
    API_URL = "http://universities.hipolabs.com/search?country="
    search = request.args.get('country')

    # get it from external source
    r = requests.get(f"{API_URL}{search}")

    return jsonify(r.json())