# Project Context: Vocabulary Learning App

## ⚡ IMMEDIATE NEXT STEP
**Phase 1 (core engine) is complete.** The one thing not yet verified: a full quiz playthrough has never actually been run to completion, so `history.json` has never been created and `SetManager.complete_current_set()` has never fired for real. Before starting Phase 2 (Flask), run a full playthrough — answer questions via `Quiz` until a set is fully mastered — and confirm `storage_data/history.json` gets created correctly with the completed set inside it. Once that's confirmed, move on to scaffolding `app.py` for Phase 2.

## Goal
A personal vocabulary-building web app, inspired by Anki-style spaced repetition. Words are learned in rotating sets of 15: the app fetches random words + definitions, quizzes the user via multiple choice, tracks mastery per word, and once all 15 words in a set are mastered, logs the completed set (with date) and loads a fresh set of 15.

## Tech Stack
- **Backend:** Python + Flask — handles word fetching, mastery/progress logic, quiz question generation, and serves a JSON API
- **Frontend:** Next.js + TypeScript (React) — user has recent hands-on experience with this stack
- **Local storage (current phase):** JSON files in a dedicated `storage_data/` folder
- **Future storage (planned upgrade):** Supabase (Postgres)
- **Hosting plan (future):**
  - Frontend → Vercel
  - Backend → Render/Railway/Fly.io (Flask needs a host that supports long-running Python servers; Vercel isn't suited for this)
  - CORS will need explicit setup (`flask-cors`) since frontend and backend live on different domains

## Data Sources
- **Random word source:** `https://random-word-api.herokuapp.com/word`
- **Definitions:** Merriam-Webster Collegiate Dictionary API (`dictionaryapi.com`), using the `shortdef` field specifically
- API key stored in `.env` as `COLLIGIATE_VOCAB_KEY`, loaded via `python-dotenv`

## Current File Structure
```
vocab_bot/
├── .venv/
├── .env
├── .gitignore
├── README.md
├── main.py                    # entry point / manual test scripts
├── python_assets/
│   ├── word_set.py            # Word, Word_Set classes
│   ├── storage.py             # JSON read/write helpers (no game state held here)
│   ├── set_manager.py         # SetManager class — holds current/buffer set in memory
│   └── quiz.py                # Quiz class — question generation + answer handling
└── storage_data/
    └── current_set.json        # history.json does not exist yet — no set has been fully completed
```
**Important:** `python_assets/` is imported as a package from the project root (`from python_assets.set_manager import SetManager`). Because of this, files *inside* `python_assets/` must import each other using relative imports (`from .word_set import Word_Set`), not bare imports (`from word_set import Word_Set`) — bare imports only work if you run that file standalone from inside the folder, and break once it's imported as part of a package. This bit us once already (`ModuleNotFoundError: No module named 'word_set'`) — fixed by switching to relative imports in `set_manager.py` and `storage.py`.

## Core Classes (built so far)

### `Word` (in `word_set.py`)
- Attributes: `word`, `definition`, `streak`, `times_seen`, `mastered`, `user_sentence`
- Methods: `mark_correct()`, `mark_incorrect()`, `mark_mastered()`, `set_user_sentence()`, `to_dict()`, `from_dict()` (classmethod)
- Mastery rule: 3 correct answers in a row (streak-based) marks a word mastered; a wrong answer resets streak to 0

### `Word_Set` (in `word_set.py`)
(naming note: should be renamed `WordSet` for PEP8 convention — still not done)
- Attributes: `set_id`, `words` (list of `Word` objects), `set_complete`, `completed_date`
- **Constructor fix (done):** `__init__(self, words=None)` is now fast and takes an optional pre-built list — no network calls, can't fail. A separate `generate_new()` classmethod does the actual fetching: makes an empty instance via `cls()`, calls `build_word_set()` on it, returns the populated instance. This was needed because the original design had `__init__` calling `build_word_set()` directly, which blocked `from_dict()` from safely reconstructing a saved set without triggering new API calls.
- `to_dict()` / `from_dict()` — built. `from_dict()` rebuilds `Word` objects first, then passes them into the fast constructor — no network calls on load.
- `build_word_set()` / `get_word()` — unchanged in logic, but **`get_word()` now has error handling**: both `requests.get()` calls have `timeout=5`, and the whole block is wrapped in `try/except requests.exceptions.RequestException`. A dropped connection or timeout is now treated like a bad word (skip, retry) instead of crashing the whole generation thread. This was added after a real `ConnectionError: Remote end closed connection without response` crashed a buffer-generation thread mid-run.

### `SetManager` (in `set_manager.py`, new)
Holds live game state in memory — `storage.py`'s functions are stateless (one I/O operation, no memory between calls), so something needed to track "what's the current set right now" and "what's generating in the background" across time. A class was chosen over module-level globals to bundle `buffer_set` together with the `threading.Lock` that protects it and the thread that populates it, reducing the chance of something mutating `buffer_set` without going through the lock.
- `self.current_set`, `self.buffer_set`, `self._buffer_thread`, `self._lock`
- `load_initial_set()` — called once at startup. **Order matters here:** it starts buffer generation *first* (non-blocking, `.start()` returns immediately), then loads/generates the current set synchronously on the main thread. This way, if both need to hit the APIs from scratch (first run, nothing saved), they run concurrently instead of one waiting on the other — worst case is closer to one generation cycle, not two.
- `start_buffer_generation()` — reusable async builder, spawns a daemon `threading.Thread` running `Word_Set.generate_new()`, stores the result in `self.buffer_set` under the lock when done. Used both at startup and after every rotation.
- `complete_current_set()` — commits the finished set to history (`append_to_history()`), waits for the buffer thread if it isn't done yet (`.join()` — the one spot where the user could theoretically wait, though unlikely given how slow generation is relative to quiz time), promotes buffer → current, saves it, then kicks off a new buffer for next time.
- **Design decision:** the buffer set is *never* persisted to disk while it's just a buffer — only `current_set.json` is written. If the server restarts mid-buffer, the buffer is simply regenerated; no user progress is lost since no mastery data was ever recorded against it.

### `Quiz` (in `quiz.py`, new)
Owns a `SetManager` and handles gameplay — deliberately kept separate so `SetManager` stays focused purely on set lifecycle (load/buffer/rotate) while `Quiz` is only responsible for asking questions and scoring answers.
- `__init__(self, manager=None)` — accepts an injected `SetManager` (useful for testing) or builds its own; calls `load_initial_set()` immediately.
- `current_set` — a `@property`, not a stored copy. This matters: after rotation, `manager.current_set` becomes a *different object* (the promoted buffer). A property means `Quiz` always reads live instead of holding a stale reference — this exact stale-snapshot bug was hit once already in a test script (`buffer_set = manager.buffer_set` captured `None` before a wait loop, then never re-read after the loop finished).
- `get_next_question()` — picks a random unmastered word, builds a 4-option multiple choice question (1 correct + 3 distractors). **Distractors are pulled from the full word list (`current_set.words`), not just pending/unmastered words** — this was a deliberate fix so the distractor pool never shrinks below 3, even late in a set when only 1-2 words remain unmastered. Resolves the "distractor pool" open question from the original design doc.
- `submit_answer(word_text, chosen_definition)` — looks up the word, calls `mark_correct()`/`mark_incorrect()`, checks `current_set.check_mastered()`, and if the set just completed, triggers `manager.complete_current_set()`. This is the wiring point that connects quiz gameplay to set rotation.

### `storage.py`
Pure, stateless I/O — no memory of its own, `SetManager` is the one deciding *when* to call these.
- `SAVE_PATH` / `HISTORY_PATH` now point into `storage_data/` (a dedicated folder, not the project root). `_ensure_storage_dir()` creates that folder automatically (`os.makedirs(..., exist_ok=True)`) the first time anything writes.
- `save_set()` / `load_set()` — current set only
- `load_or_create_set()` — the startup helper; loads from disk if present, else generates fresh and saves
- `generate_and_save_set()` — standalone utility to force a brand-new set regardless of what's saved (not currently called by `SetManager`, but available for manual/CLI use)
- `load_history()` / `append_to_history()` — history is a **separate, append-only file** (`history.json`). Deliberately kept separate from `current_set.json` because the current set gets rewritten on every single quiz answer, while history is only written once per completed set — combining them would mean rewriting the entire history on every answer.
- **`history.json` does not exist on disk yet** — no set has been fully mastered in testing so far, so `append_to_history()` has never actually run. This is expected, not a bug.

## Known Open Design Questions (deferred, not yet decided)
- Duplicate word handling (within a set, and across sets over time)
- Whether `user_sentence` factors into mastery at all, or is purely reference
- Auto-save vs. explicit save for `user_sentence` edits
- Session/resume behavior (quit mid-quiz, come back later — reshuffle or resume exactly?)
- Daily quiz limits vs. unlimited
- ~~Distractor definition pool when fewer than 4 unmastered words remain~~ — **resolved**: pulling distractors from the full set instead of just pending words means the pool never drops below 14 candidates

## Roadmap (phased) — current status

### Phase 1 — Core Word Engine (Python) — nearly done
Branch: `featurep1/core-engine`
Done: constructor refactor, `Word_Set` serialization, JSON save/load helpers, `check_mastered()` wired via `Quiz.submit_answer()`, quiz question generator, answer handling, completed-set history logging, set rotation via `SetManager`, async buffer generation via threading
Not yet done: full end-to-end test of a completed set (to confirm `history.json` actually gets created correctly), duplicate handling, user_sentence wiring, rename `Word_Set` → `WordSet`

### Phase 2 — Flask API — about to start
Branch convention in use: `feature/quiz-flask` and `feature/quiz-ui` as flat sibling branches off `feature/quiz` (see Git Learnings below for why they're flat, not nested)
Endpoints needed: get current set/progress, get next quiz question (`Quiz.get_next_question()`), submit answer (`Quiz.submit_answer()`), get progress summary, get completed-set history (`storage.load_history()`). Must set up `flask-cors` early.
**Design decision confirmed:** Flask holds one shared `Quiz` instance in memory at startup (same pattern as `SetManager`), and each endpoint just calls a method on it. Flask is purely a messenger — no new game logic lives in Flask itself, no separate `Game` class needed. The frontend (not Python) will own the actual play loop: call `/question`, show it, wait for a click, call `/answer`, repeat.

### Phase 3 — Next.js Frontend
Branch: `featurep3/nextjs-frontend`
Quiz screen, answer feedback UI, progress view, history view, styling. Explicitly waiting on Phase 2 to exist first — user considered building a throwaway CLI or simple HTML interface to test sooner, but decided to go straight Flask → Next.js instead.

### Phase 4 — Polish
Branch: `featurep4/polish`
Error handling in UI, loading states, session persistence, config options (set size, mastery threshold).

### Phase 5 — Deployment
Branch: `featurep5/deployment`
Migrate JSON → Supabase, host Flask backend separately, host Next.js frontend on Vercel, production env var config.

## Git Learnings (this session)
- **Branch name collisions are a file/folder problem:** git branch names are literal paths under `.git/refs/heads/`. `feature/quiz/flask` can't be created if `feature/quiz` already exists as a branch name, because that would require `feature/quiz` to be both a file and a folder at once. Resolved by using flat names (`feature/quiz-flask`, `feature/quiz-ui`) instead of nesting under an existing branch name.
- **Recovering a branch that exists remotely but not locally:** `git fetch origin` then `git checkout -b <branch-name> origin/<branch-name>` — recreates the local branch tracking the remote one, no data lost.
- **`git merge --abort`** — backs out of an in-progress, uncommitted merge entirely, back to the state before `git merge` was run. Only works before the merge commit is finalized.
- **Vim basics** (comes up during merge commits and rebases): `i` enters Insert mode to type, `Esc` exits back to Normal mode, `:wq` saves and quits, `:q!` quits without saving. User is still building comfort here — walk through Vim steps explicitly rather than assuming familiarity.
- **`git commit --amend`** — rewrites the most recent commit's message (or content). Safe if not yet pushed; requires `git push --force` afterward if it was already pushed.
- Current merge plan in progress: recover `feature/storage` from remote → work on storage changes → merge into `main` (pulling `main` up to date first) → switch to `feature/quiz` (which is behind `main`) → `git merge main` → resolve any conflicts.

## Learning Goals Alongside Building
User is deliberately learning as they go — Python fundamentals and git workflows. Consistently pushes back until an explanation is actually clear rather than accepting a surface-level answer; prefers being walked through *why* something works before or alongside the code itself. Specific concepts covered in depth this session:
- `@classmethod` as an alternate constructor pattern (`generate_new()`, `from_dict()`) — used only where an instance must be created as part of the method's job; everything else stays a regular instance method
- `@property` — makes a method callable without `()`, and here specifically ensures live reads (`self.current_set`) instead of a stale cached copy
- `threading` vs `asyncio` trade-offs — threading chosen because `requests` is a blocking library; true async would require swapping to `aiohttp`
- Variable snapshot bugs — assigning `buffer_set = manager.buffer_set` captures the value at that instant, not a live link; must re-read after any wait/loop
- Relative vs. absolute imports inside a package (see File Structure note above)
- Git: rebase practice (Phase 1), branch naming/path collisions, recovering remote-only branches, `--abort`, `--amend`, Vim basics for commit messages

Each phase still has a specific git skill deliberately woven in for practice (unchanged from original plan):
- **Phase 1:** rebase practice (sub-branch off core-engine, rebase before merging back)
- **Phase 2:** interactive rebase/squashing messy WIP commits + opening a real PR for review before merging
- **Phase 3:** deliberately triggering and resolving a merge conflict (two branches editing the same file)
- **Phase 4:** cherry-picking a commit made on the wrong branch to the correct one
- **Phase 5:** `git revert` on a merge commit (simulating a broken deploy) + tagging a release (`git tag -a v1.0`)

## Notes for Picking This Up in a New Chat
- User is on Python 3.9, macOS, VS Code, using a `.venv` virtual environment
- Communication style: wants concise, plain-language explanations first — avoid jargon-heavy answers up front. Will explicitly say "I still don't get it" if an explanation doesn't land; respond by re-explaining more simply/concretely, not by repeating the same explanation with more words
- Prefers to understand *why* before seeing code, but does want the actual code written out (not just described) once the concept is clear
- Comfortable driving high-level design decisions (e.g. two-file storage split, flat git branch naming, Quiz-owns-SetManager structure) — good to offer trade-offs and let the user pick, rather than deciding unilaterally
- Still building git fluency — don't assume familiarity with merge conflict resolution, Vim, or rebase mechanics; walk through commands step by step
- Immediate next steps when resuming: (1) finish the in-progress git merge (`feature/storage` → `main` → `feature/quiz`), (2) run a full quiz playthrough to confirm `history.json` gets created correctly on first real set completion, (3) start scaffolding the Flask app (`app.py`) with the five endpoints listed under Phase 2