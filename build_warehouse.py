"""Task 04 - Build the dimensional model, run quality gates, publish only if clean.

posts_clean  ->  build_dim_users, build_dim_length_bucket, build_fact_posts
              ->  quality tests
              ->  PASS: rename to dim_users, dim_length_bucket, fact_posts (published)
              ->  FAIL: stop, exit code 1, published tables stay untouched

Run:  python build_warehouse.py   (needs warehouse.db with posts_clean from transform.py)
"""
import logging
import sqlite3
import sys
from pathlib import Path

from quality_tests import TESTS

DB_PATH = "warehouse.db"
MODEL_DIR = Path(__file__).parent / "sql" / "model"
MODEL_STEPS = ["01_dim_users.sql", "02_dim_length_bucket.sql", "03_fact_posts.sql"]
TABLES = ["dim_users", "dim_length_bucket", "fact_posts"]

log = logging.getLogger("build_warehouse")


def build(conn):
    for name in MODEL_STEPS:
        conn.executescript((MODEL_DIR / name).read_text())
        log.info("Built model step %s", name)
    conn.commit()


def run_tests(conn):
    """Returns list of failed test names."""
    failed = []
    for name, sql in TESTS.items():
        bad_rows = conn.execute(sql).fetchall()
        if bad_rows:
            failed.append(name)
            log.error("TEST FAILED: %s | %d bad row(s), e.g. %s", name, len(bad_rows), bad_rows[:3])
        else:
            log.info("TEST PASSED: %s", name)
    return failed


def publish(conn):
    """Swap build_* tables in as the published tables, all in one transaction."""
    statements = ["BEGIN;"]
    for t in TABLES:
        statements.append(f"DROP TABLE IF EXISTS {t};")
        statements.append(f"ALTER TABLE build_{t} RENAME TO {t};")
    statements.append("COMMIT;")
    conn.executescript("\n".join(statements))
    log.info("Published: %s", ", ".join(TABLES))


def main(db_path=DB_PATH):
    if not Path(db_path).exists():
        sys.exit("warehouse.db illa - first python load.py and transform.py run pannu")
    conn = sqlite3.connect(db_path)
    try:
        build(conn)
        failed = run_tests(conn)
        if failed:
            sys.exit(f"Quality gate FAILED ({len(failed)} test(s): {', '.join(failed)}). Nothing published.")
        publish(conn)
        log.info("Quality gate passed: %d tests OK", len(TESTS))
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    main()
