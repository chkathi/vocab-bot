from python_assets.word_set import Word_Set
from python_assets.storage import (
    load_current_set,
    save_current_set,
    clear_current_set,
    load_all_sets,
    get_set_by_id,
    upsert_set,
)


class SetManager:
    def __init__(self):
        # In-memory mirror of current_set.json -- avoids a disk read on
        # every single request; reloaded from disk lazily if empty.
        self.current_set = load_current_set()

    def _flush_current_to_history(self):
        """
        Pushes whatever's in self.current_set into all_sets.json (loop +
        rewrite), then clears current_set.json. Called on switch or
        completion -- never on every answer.
        """
        if self.current_set is not None:
            upsert_set(self.current_set)
            clear_current_set()
            self.current_set = None

    def _ensure_current(self, set_id):
        """
        Makes sure self.current_set holds the set matching set_id.
        If a different set is already cached, flushes it first.
        """
        if self.current_set is not None and self.current_set.set_id == set_id:
            return self.current_set

        self._flush_current_to_history()

        word_set = get_set_by_id(set_id)
        if word_set is None:
            raise ValueError(f"No set found with id {set_id}")

        self.current_set = word_set
        save_current_set(self.current_set)
        return self.current_set

    def list_sets(self):
        """
        Returns every set for the History page. If a set is currently
        being practiced, its in-memory version (possibly ahead of what's
        saved in all_sets.json) is substituted in so History always
        reflects live progress, not stale data.
        """
        sets = load_all_sets()

        if self.current_set is not None:
            for i, existing in enumerate(sets):
                if existing.set_id == self.current_set.set_id:
                    sets[i] = self.current_set
                    break
            else:
                sets.append(self.current_set)

        return sets

    def get_set(self, set_id):
        """
        Loads the given set for practice, switching away from whatever
        was previously current (flushing it first, if needed).
        """
        return self._ensure_current(set_id)

    def generate_new_set(self):
        """
        Synchronous -- called directly by the "Generate new set" button.
        Flushes whatever was current, generates a fresh set, and makes
        it current immediately so it's ready to practice.
        """
        self._flush_current_to_history()

        new_set = Word_Set.generate_new()
        self.current_set = new_set
        save_current_set(self.current_set)
        return new_set

    def save_progress(self, word_set):
        """
        Called after every answer. Cheap write to current_set.json.
        If this answer just completed the set, flush it to all_sets.json
        immediately rather than waiting for the user to switch away.
        """
        self.current_set = word_set

        if word_set.set_complete:
            self._flush_current_to_history()
        else:
            save_current_set(word_set)