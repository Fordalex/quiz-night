import os
from flask import Flask, render_template, redirect, url_for, session, request
from os import path
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId

if path.exists("env.py"):
    import env

app = Flask(__name__)

DBURL = os.environ.get('DATABASE_URL')

app.config["MONGO_URI"] = DBURL


mongo = PyMongo(app)

@app.route('/', methods=["GET", "POST"])
def user():
    if request.method == "POST":
        session["username"] = request.form['username']

    if "username" in session:
        return redirect(url_for('index', username=session["username"]))

    return render_template('user.html')

@app.route('/index/<username>')
def index(username):
    alex_answers = mongo.db.alex.find()
    mum_answers = mongo.db.mum.find()
    joseph_answers = mongo.db.joseph.find()

    alex_count = 0
    for num in alex_answers:
        alex_count += 1
    
    joseph_count = 0
    for num in joseph_answers:
        joseph_count += 1
    
    mum_count = 0
    for num in mum_answers:
        mum_count += 1

    alex_answers = mongo.db.alex.find()
    alex_answers_two = mongo.db.alex.find()
    mum_answers = mongo.db.mum.find()
    mum_answers_two = mongo.db.mum.find()
    joseph_answers = mongo.db.joseph.find()
    joseph_answers_two = mongo.db.joseph.find()

    print(alex_count,joseph_count,mum_count)

    quizDoneButton = False
    if alex_count >= 20 and mum_count >= 20 and joseph_count >= 20:
        quizDoneButton = True
    else:
        quizSettings = mongo.db.quizSettings.update({'settings': 'one'},{
        'settings': 'one',
        'hidden': 'True'
    })

    answers_hidden = mongo.db.quizSettings.find_one({'settings': 'one'})


    return render_template('index.html', username=username,alex_count=alex_count, alex_answers=alex_answers, alex_answers_two=alex_answers_two, mum_answers=mum_answers, mum_answers_two=mum_answers_two,mum_count=mum_count, joseph_answers=joseph_answers,joseph_count=joseph_count, joseph_answers_two=joseph_answers_two, quizDoneButton=quizDoneButton, answers_hidden=answers_hidden  )


# save the users answers
@app.route('/save_alex', methods=['POST'])
def save_alex():
    answer = request.form['answer']
    quiz_database = mongo.db.alex
    quiz_answer = {
        'answer': answer
    }

    quiz_database.insert_one(quiz_answer)
    return redirect(url_for('index', username=session["username"]))

@app.route('/save_mum', methods=['POST'])
def save_mum():
    answer = request.form['answer']
    quiz_database = mongo.db.mum
    quiz_answer = {
        'answer': answer
    }

    quiz_database.insert_one(quiz_answer)
    return redirect(url_for('index', username=session["username"]))

@app.route('/save_joseph', methods=['POST'])
def save_joseph():
    answer = request.form['answer']
    quiz_database = mongo.db.joseph
    quiz_answer = {
        'answer': answer
    }

    quiz_database.insert_one(quiz_answer)
    return redirect(url_for('index', username=session["username"]))

# delete the users answers
@app.route('/delete_alex/<data_id>')
def delete_alex(data_id):
    mongo.db.alex.remove({'_id': ObjectId(data_id)})
    return redirect(url_for('index', username=session["username"]))

@app.route('/delete_mum/<data_id>')
def delete_mum(data_id):
    mongo.db.mum.remove({'_id': ObjectId(data_id)})
    return redirect(url_for('index', username=session["username"]))

@app.route('/delete_joseph/<data_id>')
def delete_joseph(data_id):
    mongo.db.joseph.remove({'_id': ObjectId(data_id)})
    return redirect(url_for('index', username=session["username"]))


#quiz done

@app.route('/quiz_done')
def quiz_done():
    quizSettings = mongo.db.quizSettings.update({'settings': 'one'},{
        'settings': 'one',
        'hidden': 'False'
    })

    return redirect(url_for('index', username=session["username"]))

# log out

@app.route('/log_out')
def log_out():
    session.clear()

    return redirect(url_for('user'))

# restart quiz
@app.route('/restart_quiz')
def restart_quiz():
    alex_answers = mongo.db.alex.remove()
    mum_answers = mongo.db.mum.remove()
    joseph_answers = mongo.db.joseph.remove()

    return redirect(url_for('user'))


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")), debug=True)