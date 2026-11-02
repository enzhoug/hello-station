import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


def initialize():
    with connect() as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)")


@contextmanager
def connect():
    path = Path(os.environ.get("DATABASE_PATH", "data/tasks.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()
