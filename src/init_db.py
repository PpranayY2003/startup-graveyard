import sqlite3
from pathlib import Path

DB = Path("data/startup_graveyard.db")
DB.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(DB) as con:
    con.executescript(Path("sql/schema.sql").read_text(encoding="utf-8"))
    tables = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    years = con.execute("SELECT COUNT(*), MIN(year_key), MAX(year_key) FROM dim_date").fetchone()

print("database:", DB)
print("tables:", [t[0] for t in tables])
print("dim_date rows / min / max:", years)
