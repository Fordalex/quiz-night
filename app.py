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


# The settings page where a user can create a quiz.
@app.route('/settings', methods=["GET", "POST"])
def settings():
    # If user has tried to loggin to a quiz using the 'quiz name' and the 'pin'.
    if request.method == 'POST':
        quizName = request.form['quizName']
        userCount = request.form['userCount']
        arrayOfUsers = {}
        arrayOfNames = []

        # Count the amount of users and sort them into arrayOfUsers.
        for user in range(int(userCount)):
            userKey = 'user' + str(user + 1)
            usersName = request.form[userKey]

            aUser = {usersName : { 'answers': [], 'categories': []} }
            arrayOfUsers.update(aUser)
            arrayOfNames.append(usersName)

        # Sorting the quiz data and sending it to the database.
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
        session['quizName'] = quizName

        return redirect(url_for('lobby'))

    # If viewing the page render this template.
    return render_template('settings.html')


# Search for the users request quiz and return the page or return back to the menu with an error.
@app.route('/', methods=["GET","POST"])
def menu():
    error = False
    # If user is looking for a quiz search the database or return an error.
    if request.method == 'POST':
        quizName = request.form['quizName']
        pin = request.form['pin']

        if mongo.db.quizzes.find_one({'quizName': quizName, 'pin': pin}):
            session['quizName'] = quizName
            return redirect(url_for('lobby'))

        else:
            error = "The quiz you were looking for wasn't found, check the quiz name and the pin."

    return render_template('menu.html', error=error)


# Select the username or return to the quiz.
@app.route('/lobby', methods=["GET", "POST"])
def lobby():
    quizName = session['quizName']

    if request.method == "POST":
        session["username"] = request.form['username']

    if "username" in session:
        return redirect(url_for('categories'))

    quizName = mongo.db.quizzes.find_one({'quizName': quizName})

    return render_template('lobby.html', quiz=quizName)


# Add the categories for the quiz.
@app.route('/categories', methods=["GET", "POST"])
def categories():
    # Find the current quiz
    quizName = session['quizName']
    username = session['username']
    quiz = mongo.db.quizzes.find_one({'quizName': quizName})

    usersCats = quiz['usersData'][username]['categories']

    # If categories already in database go straight back to quiz.
    if usersCats:
        return redirect(url_for('index'))

    # Save the categories to the database and join the quiz.
    if request.method == "POST":
        catNumber = 0
        while True:
            catNumber += 1
            formName = 'cat' + str(catNumber)
            try:
                cat = request.form[formName]
                usersCats.append(cat)
                continue
            except:
                cat = False
                break

        mongo.db.quizzes.update({'quizName': quizName},quiz)
        return redirect(url_for('index'))

    return render_template('addcategories.html', quiz=quiz)


# The quiz page with the user selected
@app.route('/index')
def index():
    username = session['username']
    quizName = session['quizName']
    quizNameMongo = mongo.db.quizzes.find_one({'quizName': quizName})

    # Find out the total amount of questions going to be asked.
    userCountMinusOne = quizNameMongo['userCount'] - 1
    totalQuestionsPerPerson = quizNameMongo['categories'] * quizNameMongo['questionsCount'] * userCountMinusOne
    totalQuestions = totalQuestionsPerPerson * quizNameMongo['userCount']
    # How many questions have been answered.
    totalAnswers = 0
    usersName = quizNameMongo['usersNames']

    for user in usersName:
        usersAnswersLength = len(quizNameMongo['usersData'][user]['answers'])
        totalAnswers += usersAnswersLength

    # If the total questions is the same as the questions answered.
    if totalAnswers == totalQuestions:
        quizFinished = True
    else:
        quizFinished = False

    return render_template('quiz.html', quiz=quizNameMongo, username=username, quizFinished=quizFinished)


# save the users answers
@app.route('/save', methods=['POST'])
def save():
    # Get the current quiz, user and the answer submitted.
    username = session['username']
    quizName = session['quizName']
    answer = request.form['answer']

    # Find the current quiz from the database and add the answer.
    quiz = mongo.db.quizzes.find_one({'quizName': quizName})
    usersAnswers = quiz['usersData'][username]['answers']
    usersAnswers.append({'answer': answer, 'correct': 'False'})
    mongo.db.quizzes.update({'quizName': quizName},quiz)

    return redirect(url_for('index',username=username, quizName=quizName))


# quiz_finished
@app.route('/quiz_finished')
def quiz_finished():
    # get the current quiz
    quizName = session["quizName"]
    quiz = mongo.db.quizzes.find_one({'quizName': quizName})

    return redirect(url_for('index'))


# Mark the answers
@app.route('/mark_answers', methods=['POST', 'GET'])
def mark_answers():
    # Get the current user and the quiz from the database.
    quizName = session['quizName']
    username = session['username']
    quiz = mongo.db.quizzes.find_one({'quizName': quizName})

    # Change the show answers to true.
    quiz["showAnswers"] = "True"
    mongo.db.quizzes.update({'quizName': quizName},quiz)

    # If user has sent the marked answers and update the database and redirect to the review page.
    if request.method == 'POST':

        # Get them marked answers from the form sent
        selected = request.form.getlist('answer')

        # Find the answers that have been stored, and update to true if they have been checked.
        for checkedAnswerIndex in selected:
            # Get the users name that is being marked first
            locationOfTheAnswer = checkedAnswerIndex.split('-')
            # locationOfTheAnswer, [0] user, [1] category, [2] answer,

            usersName = quiz['usersNames'][int(locationOfTheAnswer[0])]
            # The location of the answer in the database
            catNumberFromForm = int(locationOfTheAnswer[1])
            answerNumberFromForm = int(locationOfTheAnswer[2])
            answerIndex = 0

            # Finding the index on the answer in the array inside the database
            for catIndex in range(catNumberFromForm):
                amountOfQuestions = int(quiz['questionsCount'])
                answerIndex = answerIndex + amountOfQuestions

            for num in range(answerNumberFromForm):
                answerIndex = answerIndex + 1

            quizMaster = quiz['usersNames'].index(username)
            totalQuestionsPerRound = quiz['categories'] * quiz['questionsCount']

            if quizMaster < int(locationOfTheAnswer[0]):
                answerIndex += totalQuestionsPerRound

            for roundIndex in range(quizMaster - 1):
                answerIndex += totalQuestionsPerRound

            

            # Updating the correct attribute to true in the database
            quiz['usersData'][usersName]['answers'][answerIndex]['correct'] = 'True'
            mongo.db.quizzes.update({'quizName': quizName},quiz)

        return redirect(url_for('review_answers'))

    return render_template('markanswers.html', quiz=quiz, username=username)


# Review answers
@app.route('/review_answers')
def review_answers():
    quiz = session['quizName']
    username = session['username']
    quiz = mongo.db.quizzes.find_one({'quizName': quiz})

    return render_template('reviewanswers.html', quiz=quiz, username=username)


# Log the user out.
@app.route('/log_out')
def log_out():
    session.clear()

    return redirect(url_for('menu'))


# Remove the quiz from the database.
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