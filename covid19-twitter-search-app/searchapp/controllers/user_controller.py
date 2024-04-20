import imp
import flask
from flask import request
from app import app
from model.user_model import user_model
obj = user_model()

@app.route("/user/all")
def all_user_model():
    return obj.all_user_model()

@app.route("/user/<name>")
def specific_user(name):
    return obj.get_specific_user(name)

@app.route("/search")
def get_search_user():
    arg1 = request.args['arg1']
    arg2 = request.args['arg2']
    return obj.get_user_search(arg1,arg2)

@app.route("/wildsearch/<name>")
def wild(name):
    return obj.wild_search(name)

@app.route("/usercount/<name>")
def usercount(name):
    return obj.user_count(name)

@app.route("/top10")
def top10_users():
    return obj.top10_users()