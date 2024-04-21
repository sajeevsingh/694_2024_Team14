import requests
import flask
from flask import request, jsonify
from model.tweet_model import tweet_model
tweet_obj = tweet_model()

app = flask.Flask(__name__)

try:
    from controllers import *
except Exception as e:
    print(e)

app.config["DEBUG"] = True

@app.route("/tweet/keyword")
def all_tweets():
    key_word = request.args.get('keyword')
    return jsonify(tweet_obj.query_tweets_by_keyword(key_word))

@app.route("/universities")
def get_universities():
    API_URL = "http://universities.hipolabs.com/search?country="
    search = request.args.get('country')

    # get it from external source
    r = requests.get(f"{API_URL}{search}")

    return jsonify(r.json())

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Covid19 Twitter Search App</h1>
                <p>A flask api implementation for Covid19 information.   </p>'''

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)