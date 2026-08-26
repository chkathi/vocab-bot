from flask import Flask, request, jsonify

from flask_cors import CORS

from python_assets.quiz import Quiz

app = Flask(__name__)
CORS(app)

quiz = Quiz()
print("Flask app initialized with Quiz instance.")


@app.route("/sets", methods=["GET"])
def list_sets():
    sets = quiz.list_sets()
    return jsonify([s.to_dict() for s in sets])


@app.route("/sets/<set_id>", methods=["GET"])
def get_set(set_id):
    try:
        word_set = quiz.manager.get_set(set_id)
    except ValueError as e:
        return {"error": str(e)}, 404

    return word_set.to_dict()


@app.route("/sets/generate", methods=["POST"])
def generate_set():
    new_set = quiz.generate_new_set()
    return new_set.to_dict()


@app.route("/sets/<set_id>/question", methods=["GET"])
def get_question(set_id):
    try:
        question = quiz.get_next_question(set_id)
    except ValueError as e:
        return {"error": str(e)}, 404

    if question is None:
        return {"message": "Set already complete", "question": None}

    return question


@app.route("/sets/<set_id>/submit", methods=["POST"])
def submit_answer(set_id):
    data = request.get_json()

    try:
        result = quiz.submit_answer(set_id, data["word"], data["chosen_definition"])
    except ValueError as e:
        return {"error": str(e)}, 404

    return result


if __name__ == "__main__":
    app.run(debug=True, port=5000)
