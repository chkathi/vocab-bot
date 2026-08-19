from word_set import Word_Set


def main(): 
    word_set = Word_Set()
    count = 0
    for w in word_set.words:
        count += 1
        print(f"\n{count}: {w.word} - {w.definition}\n")
        

if __name__ == "__main__":
    main()