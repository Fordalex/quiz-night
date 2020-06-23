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

# The setting page
@app.route('/', methods=["GET", "POST"])
def settings():
    if request.method == 'POST':
        quizName = request.form['quizName']
        userCount = request.form['userCount']
        arrayOfUsers = {}
        arrayOfNames = []

        for user in range(int(userCount)):
            userKey = 'user' + str(user + 1)
            usersName = request.form[userKey]

            aUser = {usersName : { 'answers': [], 'categories': []} }

            arrayOfUsers.update(aUser)
            arrayOfNames.append(usersName)

        quiz = {
            'quizName': quizName,
            'pin': request.form['pin'],
            'categories': int(request.form['categories']),
            'questionsCount': int(request.form['questionsCount']),
            'userCount': int(userCount),
            'usersData': arrayOfUsers,
            'usersNames': arrayOfNames,
            'showAnswers': 'False',
        }

        mongo.db.quizzes.insert_one(quiz)
        return redirect(url_for('user', quizName=quizName))


    return render_template('settings.html')

# find the quiz of your choose
@app.route('/menu', methods=["GET","POST"])
def menu():
    if request.method == 'POST':
        quizName = request.form['quizName']
        pin = request.form['pin']
        if mongo.db.quizzes.find_one({'quizName': quizName, 'pin': pin}):
            return redirect(url_for('user', quizName=quizName))

    return render_template('menu.html')



# Select the username or return to the quiz
@app.route('/user/<quizName>', methods=["GET", "POST"])
def user(quizName):
    if request.method == "POST":
        session["username"] = request.form['username']

    if "username" in session:
        return redirect(url_for('categories', username=session["username"], quizName=quizName))

    quizName = mongo.db.quizzes.find_one({'quizName': quizName})

    return render_template('user.html', quiz=quizName)


# Add the categories for the quiz
@app.route('/categories/<username>/<quizName>', methods=["GET", "POST"])
def categories(username, quizName):
    quiz = mongo.db.quizzes.find_one({'quizName': quizName})
    if request.method == "POST":
        usersCats = quiz['usersData'][username]['categories']
        catNumber = 0
        while True:
            catNumber += 1
            print(catNumber)
            formName = 'cat' + str(catNumber)
            try:
                cat = request.form[formName]
                usersCats.append(cat)
                print(cat)
                continue
            except:
                cat = False
                break

        mongo.db.quizzes.update({'quizName': quizName},quiz)
        
        return redirect(url_for('index', username=session["username"], quizName=quizName))

    return render_template('addcategories.html', username=username, quiz=quiz)


# The quiz page with the user selected
@app.route('/index/<username>/<quizName>')
def index(username, quizName):
    quizNameMongo = mongo.db.quizzes.find_one({'quizName': quizName})
    session['quizName'] = quizName

    # find out the total amount of questions going to be asked.
    userCountMinusOne = quizNameMongo['userCount'] - 1
    totalQuestionsPerPerson = quizNameMongo['categories'] * quizNameMongo['questionsCount'] * userCountMinusOne
    totalQuestions = totalQuestionsPerPerson * quizNameMongo['userCount']
    # How many questions have been answered
    totalAnswers = 0
    usersName = quizNameMongo['usersNames']

    for user in usersName:
        usersAnswersLength = len(quizNameMongo['usersData'][user]['answers'])
        totalAnswers += usersAnswersLength

    # if the total questions is the same as the questions answered
    if totalAnswers == totalQuestions:
        quizFinished = True
    else:
        quizFinished = False

    print(totalQuestions)
    print(totalAnswers)


    return render_template('quiz.html', quiz=quizNameMongo, username=username, quizFinished=quizFinished)


# save the users answers
@app.route('/save', methods=['POST'])
def save():
    username = session['username']
    quizName = session['quizName']
    answer = request.form['answer']

    quiz = mongo.db.quizzes.find_one({'quizName': quizName})
    usersAnswers = quiz['usersData'][username]['answers']
    usersAnswers.append(answer)

    mongo.db.quizzes.update({'quizName': quizName},quiz)

    print(quiz['usersData'][username])

    return redirect(url_for('index',username=username, quizName=quizName))


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

# quiz_finished
@app.route('/quiz_finished')
def quiz_finished():
    # get the current quiz
    quizName = session["quizName"]
    quiz = mongo.db.quizzes.find_one({'quizName': quizName})

    # change the show answers to true
    quiz["showAnswers"] = "True"
    mongo.db.quizzes.update({'quizName': quizName},quiz)

    return redirect(url_for('index', username=session["username"], quizName=quizName))

# log out
@app.route('/log_out')
def log_out():
    session.clear()

    return redirect(url_for('menu'))

# restart quiz
@app.route('/quiz_ended')
def quiz_ended():
    # get the current quiz
    quizName = session["quizName"]
    quiz = mongo.db.quizzes.remove({'quizName': quizName})

    session.clear()
    return redirect(url_for('menu'))

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")), debug=True)