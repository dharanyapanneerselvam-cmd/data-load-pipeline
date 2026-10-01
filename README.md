# Data Load Pipeline (Level 1)

Loads data from a public API into a SQLite table and verifies the row count.

## What it does
1. Reads posts from https://jsonplaceholder.typicode.com/posts
2. Writes them to the `posts` table in `warehouse.db` (SQLite)
3. Checks that source row count equals table row count

## How to run
pip install -r requirements.txt
python load.py

## Decisions
- SQLite: no setup needed, easy for anyone to run.
- INSERT OR REPLACE on primary key: re-running never creates duplicates.
- Row count check with assert: fails loudly if any rows are missing.
