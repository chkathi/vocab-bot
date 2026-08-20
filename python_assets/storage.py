import json
import os

from word_set import Word_Set

SAVE_PATH = "current_set.json"
HISTORY_PATH = "history.json"


def save_set(word_set, path=SAVE_PATH):
    with open(path, "w") as f:
        json.dump(word_set.to_dict(), f, indent=2)


def load_set(path=SAVE_PATH):
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        data = json.load(f)

    return Word_Set.from_dict(data)


def load_or_create_set(path=SAVE_PATH):
    """
    Called once when the app starts.
    If a saved set exists on disk, load it instantly (no network calls).
    Otherwise, generate a brand new set (slow -- hits the APIs).
    """
    existing = load_set(path)
    if existing is not None:
        return existing

    new_set = Word_Set.generate_new()
    save_set(new_set, path)
    return new_set