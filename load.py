"""Task 01 + 03 - Extract and load (incremental, idempotent, logged).

API (/posts) -> SQLite warehouse.db, table `posts`

How it stays safe to re-run:
  * `load_state` stores a watermark (highest post id already loaded).
  * Only records with id > watermark are inserted (incremental).
  * INSERT OR IGNORE + PRIMARY KEY means a row can never be duplicated.
  * Load + watermark update happen in ONE transaction (all or nothing).
  * Every run (success or failure) is written to the `run_log` table.
"""
import logging
import sqlite3
from datetime import datetime, timezone

import requests

API_URL = "https://jsonplaceholder.typicode.com/posts"
DB_PATH = "warehouse.db"
TABLE = "posts"

log = logging.getLogger("load")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def extract():
    log.info("Fetching %s", API_URL)
    resp = requests.get(API_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()


def setup(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id      INTEGER PRIMARY KEY,
            user_id INTEGER,
            title   TEXT,
            body    TEXT
        );
        CREATE TABLE IF NOT EXISTS load_state (
            table_name     TEXT PRIMARY KEY,
            last_loaded_id INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS run_log (
            run_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at    TEXT,
            finished_at   TEXT,
            status        TEXT,
            rows_fetched  INTEGER,
            rows_inserted INTEGER,
            rows_skipped  INTEGER,
            message       TEXT
        );
        """
    )


def get_watermark(conn):
    row = conn.execute(
        "SELECT last_loaded_id FROM load_state WHERE table_name = ?", (TABLE,)
    ).fetchone()
    if row:
        return row[0]
    # First run with the new logic: start from whatever Task 01 already loaded
    return conn.execute("SELECT COALESCE(MAX(id), 0) FROM posts").fetchone()[0]


def load(conn, records):
    """Insert only new records. Returns stats dict."""
    watermark = get_watermark(conn)
    new_records = [r for r in records if r["id"] > watermark]
    rows = [(r["id"], r["userId"], r["title"], r["body"]) for r in new_records]

    before = conn.total_changes
    conn.executemany(
        "INSERT OR IGNORE INTO posts (id, user_id, title, body) VALUES (?, ?, ?, ?)",
        rows,
    )
    inserted = conn.total_changes - before

    new_watermark = max([watermark] + [r["id"] for r in new_records])
    conn.execute(
        "INSERT INTO load_state (table_name, last_loaded_id) VALUES (?, ?) "
        "ON CONFLICT(table_name) DO UPDATE SET last_loaded_id = excluded.last_loaded_id",
        (TABLE, new_watermark),
    )

    total = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    if total < len(records):
        raise RuntimeError(f"Row count check failed: warehouse {total} < source {len(records)}")

    conn.commit()  # data + watermark saved together
    return {
        "fetched": len(records),
        "inserted": inserted,
        "skipped": len(records) - inserted,
        "watermark": new_watermark,
        "total": total,
    }


def write_run_log(conn, started, status, stats, message=""):
    conn.execute(
        "INSERT INTO run_log (started_at, finished_at, status, rows_fetched, "
        "rows_inserted, rows_skipped, message) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (started, now(), status, stats.get("fetched", 0), stats.get("inserted", 0),
         stats.get("skipped", 0), message),
    )
    conn.commit()


def run(db_path=DB_PATH):
    started = now()
    conn = sqlite3.connect(db_path)
    try:
        setup(conn)
        records = extract()
        stats = load(conn, records)
        write_run_log(conn, started, "success", stats)
        log.info(
            "Load OK | fetched=%d inserted=%d skipped=%d total_in_warehouse=%d watermark=%d",
            stats["fetched"], stats["inserted"], stats["skipped"],
            stats["total"], stats["watermark"],
        )
        return stats
    except Exception as exc:
        conn.rollback()
        write_run_log(conn, started, "failed", {}, str(exc))
        log.error("Load FAILED: %s", exc)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    run()
