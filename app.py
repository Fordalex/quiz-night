import os
from flask import Flask, render_template, redirect, url_for
from os import path
from flask_pymongo import PyMongo, pymongo, request
from bson.objectid import ObjectId

if path.exists("env.py"):
    import env

app = Flask(__name__)

DBURL = os.environ.get('DATABASE_URL')

app.config["MONGO_DBNAME"] = 'quiz'
app.config["MONGO_URI"] = DBURL


mongo = PyMongo(app)

@app.route('/')
def index():
    alex_answers = mongo.db.alex.find()
    mum_answers = mongo.db.mum.find()
    joseph_answers = mongo.db.joseph.find()

    return render_template('index.html', alex_answers=alex_answers,mum_answers=mum_answers ,joseph_answers=joseph_answers  )


# save the users answers
@app.route('/save_alex', methods=['POST'])
def save_alex():
    answer = request.form['answer']
    quiz_database = mongo.db.alex
    quiz_answer = {
        'answer': answer
    }

    quiz_database.insert_one(quiz_answer)
    return redirect(url_for('index'))

@app.route('/save_mum', methods=['POST'])
def save_mum():
    answer = request.form['answer']
    quiz_database = mongo.db.mum
    quiz_answer = {
        'answer': answer
    }

    quiz_database.insert_one(quiz_answer)
    return redirect(url_for('index'))

@app.route('/save_joseph', methods=['POST'])
def save_joseph():
    answer = request.form['answer']
    quiz_database = mongo.db.joseph
    quiz_answer = {
        'answer': answer
    }

    quiz_database.insert_one(quiz_answer)
    return redirect(url_for('index'))

# delete the users answers
@app.route('/delete_alex/<data_id>')
def delete_alex(data_id):
    mongo.db.alex.remove({'_id': ObjectId(data_id)})
    return redirect(url_for('index'))

@app.route('/delete_mum/<data_id>')
def delete_mum(data_id):
    mongo.db.mum.remove({'_id': ObjectId(data_id)})
    return redirect(url_for('index'))

@app.route('/delete_joseph/<data_id>')
def delete_joseph(data_id):
    mongo.db.joseph.remove({'_id': ObjectId(data_id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")), debug=False)