import time
from python_assets.quiz import Quiz
from python_assets.set_manager import SetManager

def test_current_set_and_buffer():
    """
    Test function to demonstrate the SetManager's functionality.
    """
    manager = SetManager()

    # Load the initial set
    current_set = manager.load_initial_set()
    print(f"Initial set loaded with {len(current_set.words)} words.")

    # Check if the buffer set is generating or completed in the background
    while manager._buffer_thread.is_alive():
        print("Buffer set is still generating...")
        time.sleep(1)

    
    print(f"Buffer set has {len(manager.buffer_set.words)} words.")

    print("\n\nCurrent Set Words:")
    for word in current_set.words:
        print(f"Word: {word.word}, Definition: {word.definition}, Mastered: {word.mastered}")

    print("\n\nBuffer Set Words:")
    for word in manager.buffer_set.words:
        print(f"Word: {word.word}, Definition: {word.definition}, Mastered: {word.mastered}")

def test_finish_set():
    q = Quiz()

    for word in q.current_set.words:
        # Simulate answering each word correctly
        for _ in range(3):
            q.submit_answer(word.word, word.definition)
            time.sleep(0.1)  # Simulate a small delay between answers

            if word.mastered:
                print(f"Answered '{word.word}' correctly. Mastered?: {word.mastered}")

    print("All words in the current set are mastered after 3 correct answers each.")

def test_quiz_question():
# Generate a new quiz instance, which will load the initial set and start buffering the next one.
    q = Quiz()

    # Get the next question from the quiz.
    question = q.get_next_question()

    # Print the question and options to the console.
    print(f"\nQuestion: What is the definition of '{question['word']}'?")
    for i, option in enumerate(question['options'], start=1):
        print(f"{i}. {option}")

    # Get user input for the answer
    user_choice = input("\nPress Enter to submit your answer...")
    chosen_definition = question['options'][int(user_choice) - 1]

    # Submit the answer and check if it's correct
    is_correct = q.submit_answer(question['word'], chosen_definition)
    if is_correct:
        print("Correct!\n")
    else:
        print("Incorrect.\n")   