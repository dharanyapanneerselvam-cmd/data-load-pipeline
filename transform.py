"""Task 02 - Transformation pipeline.

raw `posts` -> staging `stg_posts` -> final `posts_clean`

Run:  python transform.py
(Run load.py first so warehouse.db has the raw `posts` table.)
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = "warehouse.db"
SQL_DIR = Path(__file__).parent / "sql"
# Order matters: staging first, then final
SQL_STEPS = ["01_staging_posts.sql", "02_final_posts_clean.sql"]


def run_sql_file(conn, filename):
    sql = (SQL_DIR / filename).read_text()
    conn.executescript(sql)
    print(f"[ok] ran {filename}")


def count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def validate(conn):
    """Basic checks - fail loudly if the output looks wrong."""
    raw, stg, final = count(conn, "posts"), count(conn, "stg_posts"), count(conn, "posts_clean")
    print(f"rows -> raw: {raw} | staging: {stg} | final: {final}")

    dupes = conn.execute(
        "SELECT COUNT(*) FROM (SELECT post_id FROM posts_clean GROUP BY post_id HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    if dupes:
        sys.exit(f"[FAIL] {dupes} duplicate post_id in posts_clean")
    if final == 0:
        sys.exit("[FAIL] posts_clean is empty")
    if final > raw:
        sys.exit("[FAIL] final has more rows than raw")
    print("[ok] validation passed")


def main():
    if not Path(DB_PATH).exists():
        sys.exit("warehouse.db illa - first python load.py run pannu")
    conn = sqlite3.connect(DB_PATH)
    try:
        for step in SQL_STEPS:
            run_sql_file(conn, step)
        conn.commit()
        validate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
