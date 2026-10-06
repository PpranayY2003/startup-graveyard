import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(os.getenv("DB_PATH", "data/startup_graveyard.db"))


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


if __name__ == "__main__":
    with get_conn() as conn:
        print("SQLite", conn.execute("SELECT sqlite_version()").fetchone()[0])
        print("DB file:", DB_PATH.resolve())