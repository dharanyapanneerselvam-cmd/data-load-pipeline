import sqlite3
import requests

API_URL = "https://jsonplaceholder.typicode.com/posts"
DB = "warehouse.db"

def extract():
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    return r.json()

def load(rows):
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        body TEXT)""")
    con.executemany(
        "INSERT OR REPLACE INTO posts VALUES (?,?,?,?)",
        [(r["id"], r["userId"], r["title"], r["body"]) for r in rows],
    )
    con.commit()
    count = con.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    con.close()
    return count

if __name__ == "__main__":
    data = extract()
    loaded = load(data)
    print(f"Source rows: {len(data)} | Table rows: {loaded}")
    assert loaded == len(data), "Row count mismatch!"
    print("Row count check passed ✅")
