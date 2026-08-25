# Project Context: Vocabulary Learning App

## ⚡ IMMEDIATE NEXT STEP
Phases 1–3 are functionally complete (core engine, Flask API, Next.js frontend). Before deployment (Phase 5), a mid-course architecture redesign (Phase 3.5) has been planned but not yet built:

- **Redesign goal:** eliminate the single "current set" concept. Every set (new, in-progress, or fully mastered) lives permanently in one unified list. History becomes the app's main/landing page, with two actions: "Practice this set" (loads any set, new or old, into the quiz UI) and "Generate new set" (explicit, synchronous — no more background buffering).
- **Next concrete step:** send backend files (`storage.py`, `set_manager.py`, `quiz.py`, `app.py`) for a file-by-file rewrite, backend first, then lock the new route contracts (`/sets`, `/sets/<id>`, `/sets/generate`, `/sets/<id>/question`, `/sets/<id>/submit`) before touching the frontend. Full file-impact map is in the "Phase 3.5" section below.
- Also still open from Phase 3 (may end up folded into the 3.5 rework rather than fixed standalone): ProgressBar styling not yet updated to the final locked palette; loading/error state handling never explicitly confirmed as "skip" vs "revisit later"; a full live end-to-end playthrough test never completed.

## Goal
A personal vocabulary-building web app, inspired by Anki-style spaced repetition. Words are learned in rotating sets of 15: the app fetches random words + definitions, quizzes the user via multiple choice, tracks mastery per word, and once all 15 words in a set are mastered, logs the completed set (with date). Under the Phase 3.5 redesign, "loading a fresh set" becomes an explicit user action rather than an automatic background swap.

## Tech Stack
- **Backend:** Python + Flask (`flask`, `flask-cors`) — word fetching, mastery/progress logic, quiz question generation, JSON API
- **Frontend:** Next.js + TypeScript (React) — built in Phase 3, functionally complete, styled to a locked palette
- **Local storage (current phase):** JSON files in `storage_data/` — under the Phase 3.5 redesign, `current_set.json` + `history.json` collapse into a single unified store (e.g. `all_sets.json`)
- **Future storage:** Supabase (Postgres) — deferred, not started
- **Hosting plan (Phase 4/5):** Frontend → **Vercel** (confirmed). Backend → likely **Render** free tier — accepting cold starts (~30–50s after 15min idle) and ephemeral filesystem (local JSON storage gets wiped on redeploy/restart) until the Supabase phase.

## Pip Requirements
- `requests` — API calls (random-word, Merriam-Webster)
- `python-dotenv` — loads `COLLIGIATE_VOCAB_KEY` from `.env`
- `flask` — API server
- `flask-cors` — CORS support
- Transitive deps: `urllib3` (pinned `<2` — see Lessons Learned), `certifi`, `charset-normalizer`, `idna`

Run `pip freeze > requirements.txt` to snapshot before deployment.

## Data Sources
- **Random word source:** `https://random-word-api.herokuapp.com/word`
- **Definitions:** Merriam-Webster Collegiate Dictionary API, `shortdef` field
- API key in `.env` as `COLLIGIATE_VOCAB_KEY`, loaded via `python-dotenv`
- **Known data quirk (not a bug, not fixed by design):** some MW `shortdef` entries end mid-clause (e.g. "...such as") — confirmed as real API data, not truncation. Also, at least one word ("limitless") returned the definition for a related headword ("limit") instead — known MW API behavior (`get_word()` takes the first result without validating headword match). Decided not to fix; an inline "edit definition" UI feature was considered and explicitly rejected (would mask real data bugs, complicate mastery/streak logic, remove validation against source of truth).

## Current File Structure
```
vocab_bot/
├── .venv/
├── .env
├── .gitignore
├── README.md
├── dev.sh                      # runs Flask + Next.js dev servers together
├── main.py                     # scratch/test scripts (direct calls into python_assets, no server)
├── backend/
│   ├── app.py                  # Flask server
│   ├── python_assets/
│   │   ├── word_set.py         # Word, Word_Set classes
│   │   ├── storage.py          # JSON read/write helpers (stateless)
│   │   ├── set_manager.py      # SetManager — holds current/buffer set in memory
│   │   └── quiz.py             # Quiz — question generation + answer handling
│   └── storage_data/
│       ├── current_set.json
│       └── history.json
└── vocab_learner_frontend/     # Next.js/TS, no src/ dir
    ├── app/                    # page.tsx, page.module.css, globals.css
    ├── components/             # Quiz, ProgressBar, History (+ .module.css each)
    ├── lib/                    # types.ts, api.ts
    ├── scripts/
    │   └── auto-answer.mjs     # dev-only: auto-answers a set correctly for fast testing
    └── .env.local              # NEXT_PUBLIC_API_URL
```
`python_assets/` is imported as a package — relative imports (`from .word_set import Word_Set`). Note: single git repo rooted at `vocab_bot/`, with `backend/` and `vocab_learner_frontend/` as sibling folders (each with own `.gitignore`) — this differs from the flat layout above and was a structural change made during/after Phase 2.

## Core Classes — status through Phase 3
`Word`, `Word_Set`, `SetManager`, `Quiz`, `storage.py` — all built and working as of Phase 3. Full current source for `word_set.py` and `quiz.py` (including `get_next_question()`/`submit_answer()`) has been reviewed and is confirmed correct and unchanged from Phase 2 design. **All of these are slated for a rewrite under Phase 3.5** (see below) — `word_set.py` is expected to survive mostly as-is; `storage.py`, `set_manager.py`, `quiz.py`, and `app.py` are not.

### `Word_Set.check_mastered()` — bug fixed in Phase 2, confirmed still correct
```python
def check_mastered(self):
    if all(word.mastered for word in self.words):
        self.set_complete = True
        self.completed_date = datetime.datetime.now().isoformat()
    return self.set_complete
```

### Investigated in Phase 3: word-selection "randomness" concern
Reported: word selection felt non-random ("removes words" pattern) both mid/late in a set AND allegedly early in a set. Root cause for the late-set feeling: confirmed **not a bug** — `Quiz.get_next_question()` uses `random.choice()` over `get_pending_words()`, which is genuinely uniform-random per call. As words get mastered, the pending pool shrinks, so repeats naturally increase — expected behavior, not list-order walking. The claim that it also happened early in a set (full 15-word pool) would point to something real — e.g. duplicate words biasing the pool, or `Quiz`/`SetManager` not persisting state correctly across requests — but this was **not investigated further; explicitly tabled by Chandu as a likely false alarm.** Flagged here in case it resurfaces.

## Phase 2 — Flask API — endpoints (current, pre-3.5)
- `GET /question` → `quiz.get_next_question()`
- `GET /current_set` → `quiz.current_set.to_dict()`
- `POST /submit` → body `{word, chosen_definition}` → `quiz.submit_answer(...)`, returns `{correct, correct_definition, word_mastered, set_completed}` (renamed from `/answer` during Phase 3 integration)
- `GET /history` → `quiz.get_history()`

CORS: changed from wide-open `CORS(app)` to `CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)` during Phase 3 (fixed an `OPTIONS` preflight 404).

## Phase 3 — Next.js Frontend — ✅ functionally complete
Built: `Quiz.tsx` (full quiz loop: fetch question → select → submit → feedback → Continue), `ProgressBar.tsx` (mastery count + word chips, refetches via `refreshTrigger` prop), `History.tsx` (collapsible per-set sections, word/definition grid layout), tab nav (Quiz/History) in `page.tsx`.

**Locked color palette:**
- Page background `#02111B`, Card `#30292F`, Input/option bg `#5D737E`, Input/option text `#FCFCFC`
- Progress chips/bar `#FCFCFC`
- Accent (selected border, submit button, active tab) `#5b8def` — **no hover variant, by explicit design choice**
- Success `#4ade80` / Error `#f87171` / Warning `#fbbf24` — no hover variants
- History word column `#93B0BC` bold (`font-weight:700`), definition column `#FCFCFC`

All visual decisions were iterated via the Visualizer/mockup tool before being turned into real CSS Modules — worked well, reusable approach for future visual features.

## Phase 3.5 — Architecture redesign (planned, not yet built)

**Core idea:** No more privileged "current set." Every set — untouched, in-progress, or fully mastered — is just an entry in one unified list. History becomes the main/landing page.

**New UX:**
- **History tab (main/landing page):** lists ALL sets regardless of completion state. Each set has a "Practice this set" button. A separate "Generate new set" button (top-level, not per-set) triggers a synchronous build — spinner while it runs, since there's no more background buffer to make it instant.
- **Practice tab:** the actual quiz UI (question/options/feedback), parameterized by whichever `set_id` was selected in History. Same screen whether the set is brand-new or being redone.

**Key decisions locked in during design discussion:**
- Re-practicing an already-mastered set is a **real requiz** — genuinely updates that set's actual `streak`/`mastered` data (mastery can revert to `False`). Not a no-consequence review copy.
- Generating a new set is now **explicit and synchronous** (button → live API calls → spinner), replacing the old async background-buffer approach. A short wait is acceptable.

**File-impact map:**

Backend:
| File | Change |
|---|---|
| `storage.py` | Rewrite: collapse `current_set.json` + `history.json` into one store (e.g. `all_sets.json`) holding a list of all sets. New functions: `load_all_sets()`, `save_set()`, `get_set_by_id()`. |
| `set_manager.py` | Rewrite: remove `load_initial_set()`, async buffer, `complete_current_set()`, `current_set` property. New shape: `list_sets()`, `get_set(set_id)`, `generate_new_set()` (synchronous). |
| `word_set.py` | Expected largely untouched — `Word`, `Word_Set`, `build_word_set()`, `get_word()`, `check_mastered()` all still valid. |
| `quiz.py` | `get_next_question()` and `submit_answer()` both take a `set_id` param instead of trusting a single `self.manager.current_set`. `get_history()` becomes `list_sets()` or is removed. |
| `app.py` | Drop `/current_set`. Add `/sets` (GET, list all), `/sets/<set_id>` (GET, one set), `/sets/generate` (POST, synchronous), `/sets/<set_id>/question` (GET), `/sets/<set_id>/submit` (POST). `/history` removed or aliased. |

Frontend (to be scoped once backend contracts are settled):
| File | Change |
|---|---|
| `lib/types.ts` | Replace `CurrentSet`/`HistoryEntry`/`HistoryResponse` with unified `SetSummary`/`SetDetail` types. |
| `lib/api.ts` | Drop `getCurrentSet()`/`getHistory()`. Add `listSets()`, `getSet(id)`, `generateSet()`, `getQuestion(setId)`, `submitAnswer(setId, payload)`. |
| `app/page.tsx` | Nav becomes History / Practice (2 tabs, replacing Quiz/History). Holds `selectedSetId` state. |
| `components/History.tsx` | Becomes the main page: lists all sets + "Practice this set" per set + top-level "Generate new set" button with loading state. |
| `components/Quiz.tsx` | Needs `setId` prop threaded to API calls (renders inside Practice tab). |
| `components/ProgressBar.tsx` | Needs `setId` prop — shows progress for whichever set is being practiced, not a global current set. |

## Phase 4 — Polish — not started
(ProgressBar palette / loading-error / end-to-end test items from Phase 3 likely get resolved here, folded into the 3.5 rebuild rather than patched separately.)

## Phase 5 — Deployment — not started, checklist drafted
- [ ] Push repo to GitHub (if not already)
- [ ] Deploy backend to Render (free web service, connect repo, set build/start commands)
- [ ] Set `NEXT_PUBLIC_API_URL` in Vercel env vars to the Render URL
- [ ] Update Flask CORS `origins` from `"*"` to the real Vercel domain
- [ ] Deploy frontend to Vercel (connect repo, auto-detects Next.js)
- [ ] Full live end-to-end test
- [ ] README note: backend data resets on redeploy (ephemeral storage) until Supabase phase

## Lessons Learned
- **Threading `.join()` does not stop a thread** — it blocks the *calling* thread until the target finishes on its own. Under the Phase 3.5 redesign this becomes moot, since the async buffer is being removed entirely.
- **A script "looking like" it confirms something isn't the same as it actually confirming it** — `check_mastered()`'s missing `return` went undetected because the original test script only checked individual word flags, never set-level completion.
- **Testing via direct Python calls vs. the real API are different tests** — the `check_mastered()` bug only surfaced once the completion path was exercised through real HTTP requests.
- **`NotOpenSSLWarning`** on macOS — fixed by pinning `urllib3<2` rather than upgrading.
- **Dev-only tooling should stay dev-only** — `/auto-answer` debug route and `scripts/auto-answer.mjs` are both explicitly flagged to stay out of production/deployment.
- **Environment variables are only read at server startup** — a `NEXT_PUBLIC_API_URL` fix required a dev server restart, not just a file save, before it took effect (Phase 3).
- **React `key` props belong on the outer element of a `.map()`, not a nested child** — caused a console warning in `Quiz.tsx`, fixed by moving the key up.

## Testing Notes
- Postman collection (`Vocab_API`) for manual endpoint testing.
- `main.py` remains a fast, no-server sandbox for testing core logic directly, bypassing Flask/HTTP.
- `dev.sh` (repo root) runs both servers together for local full-stack testing; needs a short `sleep` after starting Flask to avoid a startup race condition with the frontend's first fetch.
- `scripts/auto-answer.mjs` (frontend) speeds up manual end-to-end testing by auto-submitting correct answers in a loop until a set completes.

## Notes for Picking This Up in a New Chat
- Python 3.9, macOS, VS Code, `.venv` (located at `vocab_bot/.venv`, not inside `backend/`)
- Communication style: concise, plain-language first; will say "I still don't get it" if unclear — re-explain simpler, don't just add more words
- Prefers understanding *why* before code, but wants real code once concept is clear
- Comfortable driving design decisions — offer trade-offs, let user pick
- Wants styling in separate CSS files (CSS Modules pattern), not inline
- Still building git fluency (branching, PRs, Conventional Commits, rebase, squash, merge conflicts, cherry-pick, `git revert`) — walk through commands step by step
- Visual/design decisions work well mocked up first (Visualizer tool), then translated to real CSSS