from flask import Flask, request
from flask_cors import CORS
import time

from python_assets.quiz import Quiz

app = Flask(__name__)
CORS(app)

quiz = Quiz() 
print("Flask app initialized with Quiz instance.")

# GET to get next question
@app.route("/question", methods=["GET"])
def get_question():
    return quiz.get_next_question()

# GET current set
@app.route("/current_set", methods=["GET"])
def get_current_set(): 
    return quiz.current_set.to_dict()

@app.route("/history", methods=["GET"])
def get_history():
    history = quiz.get_history()
    if not history:
        return {"message": "No sets mastered yet", "history": []}
    return {"history": history}

@app.route("/submit", methods=["POST"])
def submit_answer():
    data = request.get_json()

    return quiz.submit_answer(data["word"], data["chosen_definition"])

if __name__ == "__main__":
    app.run(debug=True, port=5000)

