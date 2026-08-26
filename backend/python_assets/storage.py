import json
import os

from python_assets.word_set import Word_Set

STORAGE_DIR = "storage_data"
CURRENT_SET_PATH = os.path.join(STORAGE_DIR, "current_set.json")
ALL_SETS_PATH = os.path.join(STORAGE_DIR, "all_sets.json")


def _ensure_storage_dir():
    os.makedirs(STORAGE_DIR, exist_ok=True)


# ---------- current_set.json: the one set being actively practiced ----------

def load_current_set(path=CURRENT_SET_PATH):
    """
    Returns the Word_Set currently cached for practice, or None if
    nothing is loaded yet (fresh start, or nothing selected).
    """
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        data = json.load(f)

    return Word_Set.from_dict(data)


def save_current_set(word_set, path=CURRENT_SET_PATH):
    """
    Overwrites current_set.json with this set's latest state.
    Called after every answer -- cheap, single-file write, no looping.
    """
    _ensure_storage_dir()
    with open(path, "w") as f:
        json.dump(word_set.to_dict(), f, indent=2)


def clear_current_set(path=CURRENT_SET_PATH):
    """
    Called after flushing current_set into all_sets.json (on switch or
    completion), so a stale current_set.json doesn't linger.
    """
    if os.path.exists(path):
        os.remove(path)


# ---------- all_sets.json: full history/list of every set ----------

def load_all_sets(path=ALL_SETS_PATH):
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        raw = json.load(f)

    return [Word_Set.from_dict(entry) for entry in raw]


def _save_all_sets(sets, path=ALL_SETS_PATH):
    _ensure_storage_dir()
    with open(path, "w") as f:
        json.dump([s.to_dict() for s in sets], f, indent=2)


def get_set_by_id(set_id, path=ALL_SETS_PATH):
    for word_set in load_all_sets(path):
        if word_set.set_id == set_id:
            return word_set
    return None


def upsert_set(word_set, path=ALL_SETS_PATH):
    """
    Loops through all_sets, replaces the matching entry (or appends if new),
    and rewrites the whole file. Only called on completion or switch --
    NOT on every answer.
    """
    sets = load_all_sets(path)

    for i, existing in enumerate(sets):
        if existing.set_id == word_set.set_id:
            sets[i] = word_set
            break
    else:
        sets.append(word_set)

    _save_all_sets(sets, path)
    return word_set