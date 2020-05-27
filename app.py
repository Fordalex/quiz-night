import os
from flask import Flask, render_template, redirect, url_for, request
from os import path
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId

if path.exists("env.py"):
    import env

app = Flask(__name__)

DBURL = os.environ.get('DBURL')

app.config["MONGO_DBNAME"] = 'task_manager'
app.config["MONGO_URI"] = DBURL


mongo = PyMongo(app)

@app.route('/')
def index():
    alex_answers = mongo.db.alex.find()

    return render_template('index.html', alex_answers=alex_answers)


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")), debug=False)