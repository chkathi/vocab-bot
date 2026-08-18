import requests
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_word():
    url = "https://random-word-api.herokuapp.com/word"
    response = requests.get(url)

    return response.json()[0]

def get_url(word, COLLIGIATE_VOCAB_KEY):
    api_key = os.environ.get("COLLIGIATE_VOCAB_KEY")
    return f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}"



def word_of_the_day(): 
    status = -1

    # Try the word and if we fail get another word and try again until we get a valid response
    count = 0
    while status != 200 or count > 10:
        word = fetch_word()
        url = get_url(word, os.environ.get("COLLIGIATE_VOCAB_KEY"))
        response = requests.get(url)

        status = response.status_code
        count += 1

    data = response.json()[0]

    if count < 10: 
        print(f"\nWord of the day: {word}")
        print(f"Definition: {data['shortdef'][0]}\n")

        '''
        if count - 1 > 0:
            print(f"\nTried {count - 1} times to get a valid word.\n")
        '''

        return

    print(f"\n Word of the day Timed Out.... Try again later. \n")


def main(): 
    word_of_the_day()

if __name__ == "__main__":
    main()