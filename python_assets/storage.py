import json
import os

from python_assets.word_set import Word_Set

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


def generate_and_save_set(path=SAVE_PATH):
    """
    Always generates a brand new set (slow -- hits the APIs),
    overwriting whatever is currently saved at `path`.
    Use this for rotation (old set finished, need a replacement)
    or for manually forcing a fresh set regardless of what's saved.
    """
    new_set = Word_Set.generate_new()
    save_set(new_set, path)
    return new_set


def load_history(path=HISTORY_PATH):
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        return json.load(f)


def append_to_history(word_set, path=HISTORY_PATH):
    """
    Called once, when a set is completed and about to rotate out.
    Reads the existing history list, appends this set's dict, writes it back.
    Not called on every answer -- only on set completion.
    """
    history = load_history(path)
    history.append(word_set.to_dict())

    with open(path, "w") as f:
        json.dump(history, f, indent=2)