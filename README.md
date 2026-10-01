# Data Load + Transformation Pipeline

Small ELT pipeline using the JSONPlaceholder `/posts` API and SQLite.

```
API -> load.py -> posts (raw) -> transform.py -> stg_posts (staging) -> posts_clean (final)
```

## How to run
```bash
pip install -r requirements.txt
python run_pipeline.py     # load (incremental) + transform, with logging
```
Or step by step:
```bash
python load.py            # Task 01/03: incremental load into warehouse.db
python transform.py       # Task 02: build stg_posts and posts_clean (no internet needed)
```

## Task 01 - Extract and load
`load.py` pulls `/posts` and writes to `posts` (id, user_id, title, body), then checks the row count.

## Task 02 - Transformation
| Layer | Table | What happens |
|-------|-------|--------------|
| Raw | `posts` | Untouched copy of API data |
| Staging | `stg_posts` | Type casting, trimming, newline cleanup, deduplication on `post_id` |
| Final | `posts_clean` | Analyst table + `title_length`, `body_word_count` |

SQL lives in `sql/` (one file per layer). `transform.py` runs them in order and validates the result.

## Task 03 - Scheduled and idempotent

### Re-running gives the same result
- `posts.id` is a PRIMARY KEY and rows are inserted with `INSERT OR IGNORE`, so a row can never be duplicated.
- Staging and final tables are dropped and rebuilt on every run, so they always match the raw table.

### Incremental load
- Table `load_state` keeps a **watermark** = highest post id already loaded.
- Each run inserts only records with `id > watermark`, then moves the watermark forward.
- Data and watermark are saved in **one transaction**: if a run fails halfway, nothing is saved and the next run retries cleanly.

### Logging
- `pipeline.log` (console + file): what each run did (fetched / inserted / skipped / total).
- Table `run_log` in `warehouse.db`: one row per run with status, counts and error message.
```sql
SELECT * FROM run_log ORDER BY run_id DESC;
```

### Example
| Run | fetched | inserted | skipped |
|-----|---------|----------|---------|
| 1 (empty DB) | 100 | 100 | 0 |
| 2 (re-run) | 100 | 0 | 100 |
| 3 (source has 5 new posts) | 105 | 5 | 100 |

### Running on a schedule
**Windows (Task Scheduler)** - runs daily at 09:00:
```bat
schtasks /create /tn "PostsPipeline" /tr "C:\full\path\to\run_pipeline.bat" /sc daily /st 09:00
```
**Linux/Mac (cron)** - every day at 09:00:
```
0 9 * * * cd /path/to/data-load-pipeline && python run_pipeline.py
```

### Decisions
- **Watermark on `id`**: the API has no `updated_at` field, and posts are append-only, so max id is the simplest reliable marker.
- **API is still fetched in full** (the endpoint has no reliable "since" filter and it is only 100 rows), but only new rows are written to the warehouse. That is the incremental part.
- **Existing rows are not updated** (`INSERT OR IGNORE`): posts in this API do not change. If they did, an upsert would be the next step.
- **SQLite** used for simplicity (no setup needed).
- Every run is logged, including failed runs.
