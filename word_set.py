
import datetime
import os
from dotenv import load_dotenv
import requests

load_dotenv()


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
    def __init__(self, ):
        self.set_id = datetime.datetime.now().isoformat()
        self.words = self.build_word_set()          # a list of Word objects
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

    def build_word_set(self, target_count=15, max_attempts=50):
        words = []
        attempts = 0

        while len(words) < target_count and attempts < max_attempts:
            attempts += 1
            w = self.get_word()
            if w is None:
                continue
            words.append(w)

        if len(words) < target_count:
            raise RuntimeError(f"Only found {len(words)}/{target_count} words after {attempts} attempts")

        return words

    def get_word(self):
        api_key = os.environ.get("COLLIGIATE_VOCAB_KEY")
        word_url = "https://random-word-api.herokuapp.com/word"

        count = 0
        while count < 10:
            count += 1

            response = requests.get(word_url)
            word = response.json()[0]
            
           
            definition_url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}"
            response = requests.get(definition_url)

            if response.status_code != 200: 
                continue 

            data = response.json()

            if not data or isinstance(data[0], str): 
                # checks if the response is empty or if the first element is a string (which indicates no definition found)
                continue

            definition = response.json()[0]

            if "shortdef" not in definition or not definition["shortdef"]:
                continue

            return Word(word, definition['shortdef'][0])

        return None # Return None if no valid word is found after 10 attempts
    