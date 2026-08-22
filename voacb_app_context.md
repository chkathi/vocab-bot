# Project Context: Vocabulary Learning App

## ⚡ IMMEDIATE NEXT STEP
Phase 2 (Flask API) core endpoints are built and working. Before starting Phase 3 (Next.js frontend):
- Re-verify `history.json` writes correctly end-to-end now that `check_mastered()` bug is fixed (run `/auto-answer` or manual Postman flow, then check `storage_data/history.json`)
- Confirm `/current_set` (`to_dict()`) returns enough per-word data (e.g. `mastered` flags) for the frontend to compute a progress bar client-side
- Clean up commits on `feature/quiz-flask` (interactive rebase/squash) and open a PR before merging, per Phase 2's git skill assignment

## Goal
A personal vocabulary-building web app, inspired by Anki-style spaced repetition. Words are learned in rotating sets of 15: the app fetches random words + definitions, quizzes the user via multiple choice, tracks mastery per word, and once all 15 words in a set are mastered, logs the completed set (with date) and loads a fresh set of 15.

## Tech Stack
- **Backend:** Python + Flask (`flask`, `flask-cors`) — word fetching, mastery/progress logic, quiz question generation, JSON API
- **Frontend:** Next.js + TypeScript (React) — not yet started
- **Local storage (current phase):** JSON files in `storage_data/`
- **Future storage:** Supabase (Postgres)
- **Hosting plan (future):** Frontend → Vercel; Backend → Render/Railway/Fly.io

## Pip Requirements (installed so far)
- `requests` — API calls (random-word, Merriam-Webster)
- `python-dotenv` — loads `COLLIGIATE_VOCAB_KEY` from `.env`
- `flask` — API server
- `flask-cors` — CORS support (needed since frontend/backend will live on different domains)
- Transitive deps pulled in automatically: `urllib3`, `certifi`, `charset-normalizer`, `idna`

Run `pip freeze > requirements.txt` to snapshot the full list once Phase 2 is finalized.

## Data Sources
- **Random word source:** `https://random-word-api.herokuapp.com/word`
- **Definitions:** Merriam-Webster Collegiate Dictionary API, `shortdef` field
- API key in `.env` as `COLLIGIATE_VOCAB_KEY`, loaded via `python-dotenv`

## Current File Structure
```
vocab_bot/
├── .venv/
├── .env
├── .gitignore
├── README.md
├── main.py                    # scratch/test scripts (direct calls into python_assets, no server)
├── app.py                     # Flask server — new for Phase 2
├── python_assets/
│   ├── word_set.py            # Word, Word_Set classes
│   ├── storage.py             # JSON read/write helpers (stateless)
│   ├── set_manager.py         # SetManager — holds current/buffer set in memory
│   └── quiz.py                # Quiz — question generation + answer handling
└── storage_data/
    ├── current_set.json
    └── history.json
```
`python_assets/` is imported as a package — files inside it must use relative imports (`from .word_set import Word_Set`).

## Core Classes
See prior phase notes for full detail on `Word`, `Word_Set`, `SetManager`, `Quiz`, `storage.py` — unchanged in this phase except where noted below.

### `Word_Set.check_mastered()` — bug fixed this phase
Original version set `self.set_complete = True` and `self.completed_date` correctly when all words were mastered, but had **no `return` statement** — so it always returned `None` (falsy), meaning callers checking `if self.current_set.check_mastered():` never triggered, even though the underlying state was set correctly. `main.py`'s original test script never caught this because it only checked individual `word.mastered` flags, never the set-level completion signal.

**Fix:**
```python
def check_mastered(self):
    if all(word.mastered for word in self.words):
        self.set_complete = True
        self.completed_date = datetime.datetime.now().isoformat()
    return self.set_complete
```

### `Quiz` — new method this phase
```python
def get_history(self):
    return self.manager.get_history()
```
Delegates to `SetManager` rather than importing `storage` directly — keeps `storage` imports confined to `SetManager`, which is the class responsible for I/O timing/orchestration.

### `SetManager` — new method this phase
```python
def get_history(self):
    return storage.load_history()
```

## Phase 2 — Flask API — endpoints built
Branch: `feature/quiz-flask` (flat sibling off `feature/quiz`)
Flask holds one shared `Quiz` instance in memory at startup — Flask is purely a messenger, no game logic lives in Flask itself.

- `GET /question` → `quiz.get_next_question()`
- `GET /current_set` → `quiz.current_set.to_dict()`
- `POST /answer` → body `{word, chosen_definition}` → `quiz.submit_answer(...)`, returns `{correct, correct_definition, word_mastered, set_completed}`
- `GET /history` → `quiz.get_history()`, returns `{"message": "No sets mastered yet", "history": []}` if empty

`/answer` returning `correct_definition`, `word_mastered`, and `set_completed` in one response (rather than requiring separate calls) was a deliberate design choice — Flask stays a thin passthrough, and the frontend gets everything it needs from a single POST.

**Frontend flow decided:** on submit, user sees correct/incorrect + correct answer + a "Continue" button. The *next* question is only fetched (`GET /question`) when "Continue" is clicked — not bundled into the `/answer` response — so questions are generated fresh at the moment the user actually asks for them, not pre-fetched.

CORS: `CORS(app)` added, wide open for local dev.

## Lessons Learned This Phase
- **Threading `.join()` does not stop a thread** — it blocks the *calling* thread until the target thread finishes on its own. `SetManager.complete_current_set()`'s `.join()` on the buffer thread can cause a visible wait if quiz-answering finishes faster than background API-based buffer generation (network-bound) — this is expected behavior, not a bug.
- **A script "looking like" it confirms something isn't the same as it actually confirming it.** `test_finish_set()` printed a success message and individual word mastery, but never checked `set_complete` or `history.json` — masking the `check_mastered()` bug for the entire time it existed.
- **Testing via direct Python calls (`main.py`) and testing via the real API (Flask/Postman) are different tests.** The `check_mastered()` bug only surfaced once the completion path was exercised through actual `submit_answer()` → `check_mastered()` → `complete_current_set()` wiring, driven by real HTTP requests.
- **`NotOpenSSLWarning`** — macOS Python often links against LibreSSL, not OpenSSL; `urllib3` v2 warns about this. Fixed by downgrading (`pip install "urllib3<2"`) rather than upgrading — the newer library was the stricter one, not the outdated one.
- Avoid building test-only logic (e.g. an auto-answer-everything-correctly route) as a permanent, callable API endpoint — kept `/auto-answer`-style testing as a `main.py`/script-based tool instead, not shipped as production API surface. (Note: an `/auto-answer` route was added during this phase for quick debugging — flag for removal before Phase 3/deployment.)

## Testing Notes
- Postman collection set up (`Vocab_API`) for manual endpoint testing — GET requests also testable directly in browser or via `curl`.
- `main.py` remains useful going forward as a fast, no-server sandbox for testing core logic directly (bypassing Flask/HTTP) — not obsolete, just shifted from "main entry point" to "dev/debug tool."

## Roadmap — current status

### Phase 1 — Core Word Engine — ✅ complete, verified
### Phase 2 — Flask API — ✅ core endpoints built and tested; final `history.json` re-verification + git cleanup pending
### Phase 3 — Next.js Frontend — not started
Quiz screen, answer feedback UI (show correct/incorrect + correct answer + Continue button), progress view, styling. History view deferred (backend ready, frontend not required yet).
### Phase 4 — Polish — not started
### Phase 5 — Deployment — not started

## Notes for Picking This Up in a New Chat
- Python 3.9, macOS, VS Code, `.venv`
- Communication style: concise, plain-language first; will say "I still don't get it" if unclear — re-explain simpler, don't just add more words
- Prefers understanding *why* before code, but wants real code once concept is clear
- Comfortable driving design decisions — offer trade-offs, let user pick
- Still building git fluency (Vim, merge conflicts, rebase) — walk through commands step by step