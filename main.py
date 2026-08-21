import time
from python_assets.set_manager import SetManager


def main(): 
    manager = SetManager()
    current_set = manager.load_initial_set()

    
    print("Current set loaded:")
    for word in current_set.words:
        print(f"- {word.word}: {word.definition}")

    while manager.buffer_set is None:
        print("  buffer_set is still None...")
        time.sleep(1)

    # Once the buffer set is ready, print its length
    buffer_set = manager.buffer_set
    
    print(f"Buffer set length: {len(buffer_set.words)}")
    
    

if __name__ == "__main__":
    main()