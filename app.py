from flask import Flask, request
from flask_cors import CORS
from python_assets.quiz import Quiz

app = Flask(__name__)

quiz = Quiz() 

@app.route('/hello')
def hello():
    return "Hello, World!"

# GET to get next question
@app.route("/question", methods=["GET"])
def get_question():
    return quiz.get_next_question()

@app.route("/submit", methods=["POST"])
def submit_answer():
    data = request.get_json()

    return quiz.submit_answer(data["word"], data["chosen_definition"])

