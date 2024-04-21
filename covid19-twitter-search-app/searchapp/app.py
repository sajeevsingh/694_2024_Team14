import requests
import flask
from flask_smorest import Api
from flask import request, jsonify

from controllers.university_controller import blp as UniversityBlueprint
from controllers.tweet_controller import blp as TweetBlueprint
from controllers.user_controller import blp as UserBlueprint
from model.tweet_model import tweet_model
tweet_obj = tweet_model()

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Covid19 Twitter Search App"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)
api.register_blueprint(UniversityBlueprint)
api.register_blueprint(TweetBlueprint)
api.register_blueprint(UserBlueprint)

@app.route("/tweet/keyword")
def all_tweets():
    key_word = request.args.get('keyword')
    return jsonify(tweet_obj.query_tweets_by_keyword(key_word))

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Covid19 Twitter Search App</h1>
                <p>A flask api implementation for Covid19 information.   </p>'''

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)