import time
from python_assets.quiz import Quiz


def main(): 
    # Generate a new quiz instance, which will load the initial set and start buffering the next one.
    q = Quiz()

    # Get the next question from the quiz.
    question = q.get_next_question()

    # Print the question and options to the console.
    print(f"Question: What is the definition of '{question['word']}'?")
    for i, option in enumerate(question['options'], start=1):
        print(f"{i}. {option}")

    # Get user input for the answer
    user_choice = input("Press Enter to submit your answer...")
    chosen_definition = question['options'][int(user_choice) - 1]

    # Submit the answer and check if it's correct
    is_correct = q.submit_answer(question['word'], chosen_definition)
    if is_correct:
        print("Correct!")
    else:
        print("Incorrect.")

if __name__ == "__main__":
    main()