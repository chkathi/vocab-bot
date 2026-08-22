from flask import Flask, request
from flask_cors import CORS
import time

from python_assets.quiz import Quiz

app = Flask(__name__)
CORS(app)

quiz = Quiz() 
print("Flask app initialized with Quiz instance.")

@app.route('/hello')
def hello():
    return "Hello, World!"

# GET to get next question
@app.route("/question", methods=["GET"])
def get_question():
    return quiz.get_next_question()

# GET current set
@app.route("/current_set", methods=["GET"])
def get_current_set(): 
    return quiz.current_set.to_dict()

@app.route("/submit", methods=["POST"])
def submit_answer():
    data = request.get_json()

    return quiz.submit_answer(data["word"], data["chosen_definition"])

@app.route("/auto-answer", methods=["GET"])
def auto_answer(): 
    for word in quiz.current_set.words:
        # Simulate answering each word correctly
        for _ in range(3):
            quiz.submit_answer(word.word, word.definition)
            time.sleep(0.1)  # Simulate a small delay between answers
    
            if word.mastered:
                print(f"Answered '{word.word}' correctly. Mastered?: {word.mastered}")

    return quiz.current_set.to_dict()


if __name__ == "__main__":
    app.run(debug=True, port=5000)

