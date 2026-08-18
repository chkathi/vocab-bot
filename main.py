import requests
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_word():
    url = "https://random-word-api.herokuapp.com/word"
    response = requests.get(url)

    return response.json()[0]


def fetch_definition(word): 
    api_key = os.environ.get("COLLIGIATE_VOCAB_KEY")
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}"

    response = requests.get(url)
    data = response.json()[0]

    return data['shortdef'][0]

def main(): 
    word = fetch_word()
    definition = fetch_definition(word)
    print(f"\nWord of the day: {word}")
    print(f"Definition: {definition}\n")

if __name__ == "__main__":
    main()