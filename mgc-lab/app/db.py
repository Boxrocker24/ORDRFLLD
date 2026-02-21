import sqlite3
from contextlib import closing

from flask import current_app, g


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS uploads(
    id TEXT PRIMARY KEY,
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    uploaded_at TEXT NOT NULL,
    row_count INTEGER,
    col_count INTEGER,
    file_size_bytes INTEGER
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with closing(db.cursor()) as cur:
        cur.executescript(SCHEMA_SQL)
        db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
