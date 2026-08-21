import random

from python_assets.set_manager import SetManager


class Quiz:
    def __init__(self, manager=None):
        # Allows injecting a SetManager (useful for testing) or building
        # a fresh one by default.
        self.manager = manager if manager is not None else SetManager()
        self.manager.load_initial_set()  # blocks until current_set is ready; buffer starts async

    @property
    def current_set(self):
        # Always reads live from the manager -- never our own stale copy.
        return self.manager.current_set

    def get_next_question(self):
        """
        Picks a random unmastered word and builds a 4-option multiple
        choice question: 1 correct definition + 3 distractors pulled
        from OTHER words in the same set (mastered or not -- this keeps
        the distractor pool at a full 14 words regardless of how many
        are still pending, which sidesteps the "fewer than 4 unmastered
        words remain" issue flagged in the project doc).
        Returns None if there are no pending words left (set is complete).
        """
        pending = self.current_set.get_pending_words()
        if not pending:
            return None

        word = random.choice(pending)
        correct_definition = word.definition

        distractor_pool = [
            w.definition for w in self.current_set.words if w.word != word.word
        ]

        if len(distractor_pool) < 3:
            raise RuntimeError(
                "Not enough words in the set to build 3 distractors"
            )

        distractors = random.sample(distractor_pool, 3)

        options = distractors + [correct_definition]
        random.shuffle(options)

        return {
            "word": word.word,
            "options": options,
            "correct_answer": correct_definition,
        }

    def submit_answer(self, word_text, chosen_definition):
        """
        Looks up the word being answered, marks it correct/incorrect,
        checks if the whole set just became mastered, and -- if so --
        triggers SetManager.complete_current_set() (history + rotation).
        Returns True/False for whether the answer was correct.
        """
        word = next(
            (w for w in self.current_set.words if w.word == word_text), None
        )
        if word is None:
            raise ValueError(f"Word '{word_text}' not found in current set")

        is_correct = chosen_definition == word.definition

        if is_correct:
            word.mark_correct()
        else:
            word.mark_incorrect()

        self.current_set.check_mastered()

        if self.current_set.set_complete:
            self.manager.complete_current_set()

        return is_correct