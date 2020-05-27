import os
from flask import Flask, render_template, redirect, url_for
from os import path
from flask_pymongo import PyMongo, pymongo, request
from bson.objectid import ObjectId

if path.exists("env.py"):
    import env

app = Flask(__name__)

DBURL = os.environ.get('DBURL')

app.config["MONGO_DBNAME"] = 'quiz'
app.config["MONGO_URI"] = DBURL


mongo = PyMongo(app)

@app.route('/')
def index():


    return 'working'


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")), debug=False)