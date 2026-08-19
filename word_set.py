
import datetime

class Word:
    def __init__(self, word, definition):
        self.word = word
        self.definition = definition
        self.streak = 0
        self.times_seen = 0
        self.mastered = False
        self.user_sentence = ""

    def mark_mastered(self):
        self.mastered = True

    def mark_correct(self):
        self.increment_streak()
        self.increment_times_seen()

        if self.streak >= 3:
            self.mark_mastered()

    def mark_incorrect(self):
        self.streak = 0
        self.increment_times_seen()

    def increment_streak(self):
        self.streak += 1    

    def increment_times_seen(self):
        self.times_seen += 1

    def set_user_sentence(self, sentence):
        self.user_sentence = sentence

    # To dict
    def to_dict(self):
        return {
            "word": self.word,
            "definition": self.definition,
            "streak": self.streak,
            "times_seen": self.times_seen,
            "mastered": self.mastered,
            "user_sentence": self.user_sentence
        }

    # Classmethod is something you can call on the class itself
    # You do NOT need to make an instance of the class to call this method.
    @classmethod
    def from_dict(cls, data):
        word = cls(data["word"], data["definition"])
        word.streak = data["streak"]
        word.times_seen = data["times_seen"]
        word.mastered = data["mastered"]
        word.user_sentence = data["user_sentence"]
        return word

class Word_Set:
    def __init__(self, words):
        self.set_id = datetime.datetime.now().isoformat()
        self.words = words          # a list of Word objects
        self.set_complete = False
        self.completed_date = None

    def add_word(self, word):
        self.words.append(word)

    def check_mastered(self):
        if all(word.mastered for word in self.words): 
            self.set_complete = True
            self.completed_date = datetime.datetime.now().isoformat()  

    def get_pending_words(self): 
        return [word for word in self.words if word.mastered == False]

