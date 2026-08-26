import random

from python_assets.set_manager import SetManager


class Quiz:
    def __init__(self, manager=None):
        # No load_initial_set() call anymore -- there's no set to load
        # until the user picks one or generates one. SetManager's own
        # __init__ already handles restoring current_set.json if one
        # happens to exist from a previous session.
        self.manager = manager if manager is not None else SetManager()

    def get_next_question(self, set_id):
        """
        Loads/switches to set_id via the manager, then picks a random
        unmastered word and builds a 4-option multiple choice question.
        Distractors are drawn from the other 14 words in the set
        (mastered or not), same approach as before.
        Returns None if there are no pending words left (set is complete).
        """
        word_set = self.manager.get_set(set_id)

        pending = word_set.get_pending_words()
        if not pending:
            return None

        word = random.choice(pending)
        correct_definition = word.definition

        distractor_pool = [
            w.definition for w in word_set.words if w.word != word.word
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

    def submit_answer(self, set_id, word_text, chosen_definition):
        word_set = self.manager.get_set(set_id)

        word = next(
            (w for w in word_set.words if w.word == word_text), None
        )
        if word is None:
            raise ValueError(f"Word '{word_text}' not found in set '{set_id}'")

        is_correct = (chosen_definition == word.definition)
        if is_correct:
            word.mark_correct()
        else:
            word.mark_incorrect()

        set_completed = word_set.check_mastered()

        self.manager.save_progress(word_set)

        return {
            "correct": is_correct,
            "correct_definition": word.definition,
            "word_mastered": word.mastered,
            "set_completed": set_completed,
        }

    def list_sets(self):
        return self.manager.list_sets()

    def generate_new_set(self):
        return self.manager.generate_new_set()

    def get_set(self, set_id):
        return self.manager.get_set(set_id)