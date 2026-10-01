# Data Load + Transformation Pipeline

Small ELT pipeline using the JSONPlaceholder `/posts` API and SQLite.

```
API -> load.py -> posts (raw) -> transform.py -> stg_posts (staging) -> posts_clean (final)
```

## How to run
```bash
pip install -r requirements.txt
python load.py        # Task 01: extract + load raw `posts` into warehouse.db
python transform.py   # Task 02: build stg_posts and posts_clean
```
`transform.py` does not need internet - it only reads `warehouse.db`.

## Task 01 - Extract and load
`load.py` pulls `/posts` and writes to `posts` (id, user_id, title, body)
using `INSERT OR REPLACE`, then checks the row count.

## Task 02 - Transformation
| Layer | Table | What happens |
|-------|-------|--------------|
| Raw | `posts` | Untouched copy of API data |
| Staging | `stg_posts` | Type casting, trimming, newline cleanup, deduplication on `post_id` |
| Final | `posts_clean` | Analyst table + `title_length`, `body_word_count` |

SQL lives in `sql/` (one file per layer). `transform.py` runs them in order and validates the result.

### Decisions
- **Separate SQL files per layer** so there is no giant query; each file does one job.
- **Dedup with `ROW_NUMBER()`** per `post_id`. Raw already has a primary key, but dedup is kept so staging stays safe if the source changes.
- **Drop and recreate** staging/final tables each run, so re-running gives the same result.
- **Validation** fails the script on empty output, duplicate ids, or final > raw.
- **SQLite** used for simplicity (no setup needed).
