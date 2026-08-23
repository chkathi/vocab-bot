import threading

# Being run from main.py, so need to import from python_assets
from python_assets.word_set import Word_Set
from python_assets.storage import save_set, append_to_history, load_or_create_set, load_history


class SetManager:
    def __init__(self):
        self.current_set = None
        self.buffer_set = None
        self._buffer_thread = None
        self._lock = threading.Lock()

    def load_initial_set(self):
        """
        Called once at app startup. Synchronous -- the current set has to
        exist before there's anything to show the user, so this blocks.
        Once it's ready, kicks off the buffer generation in the background.
        """
        self.start_buffer_generation()
        self.current_set = load_or_create_set()
        return self.current_set

    def start_buffer_generation(self):
        """
        Reusable async buffer builder. Spawns a background thread that
        generates a brand new set and stores it in self.buffer_set when
        done. Íoes NOT block whatever set is currently in progress --
        called both at startup and after every rotation.
        """
        def _build():
            new_buffer = Word_Set.generate_new()
            with self._lock:
                self.buffer_set = new_buffer

        self._buffer_thread = threading.Thread(target=_build, daemon=True)
        self._buffer_thread.start()

    def complete_current_set(self):
        """
        Called when the current set is fully mastered.
        1. Commits the finished set to history.
        2. Promotes the buffer set to current (waiting for it to finish
           generating first, if it isn't ready yet -- this is the one
           spot where the user *could* wait, only if they finish their
           current set faster than the buffer could generate).
        3. Saves the new current set to disk.
        4. Kicks off a fresh buffer for next time.
        """
        append_to_history(self.current_set)

        if self._buffer_thread is not None:
            self._buffer_thread.join()  # no-op if already finished

        with self._lock:
            self.current_set = self.buffer_set
            self.buffer_set = None

        save_set(self.current_set)
        self.start_buffer_generation()

        return self.current_set

    def get_history(self): 
        return load_history()