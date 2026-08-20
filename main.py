from python_assets.word_set import Word_Set
from


def main(): 
    word_set = Word_Set.generate_new(target_count=15, max_attempts=50)
    count = 0
    for w in word_set.words:
        count += 1
        print(f"\n{count}: {w.word} - {w.definition}\n")
        

if __name__ == "__main__":
    main()