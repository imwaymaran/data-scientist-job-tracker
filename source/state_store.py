import sqlite3
from pathlib import Path
from datetime import date

DEFAULT_STATE_DB = "data/state/run_state.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS run_state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

DEFAULTS_SQL = """
INSERT OR IGNORE INTO run_state (key, value) VALUES
('last_reset', ?),
('carryover_requests', '0');
"""

def open_state_db(today: str, db_path: str | Path = DEFAULT_STATE_DB) -> sqlite3.Connection:
    """Open the SQLite state DB, ensure schema and default keys."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

    conn.execute(SCHEMA)
    conn.execute(DEFAULTS_SQL, (today,))
    conn.commit()
    return conn

def get_state(conn: sqlite3.Connection) -> dict:
    """Return a dict of all state keys with proper types (date, int)."""
    rows = conn.execute("SELECT key, value FROM run_state").fetchall()
    state = {}

    for key, value in rows:
        if key == "last_reset":
            try:
                state[key] = date.fromisoformat(value)
            except ValueError:
                state[key] = date.today()
        elif key == "carryover_requests":
            try:
                state[key] = int(value)
            except (TypeError, ValueError):
                state[key] = 0
    return state

def update_last_reset(conn: sqlite3.Connection, today: str):
    """Update the last_reset date."""
    with conn:
        conn.execute(
            "UPDATE run_state SET value=? WHERE key='last_reset'",
            (today,),
        )


def update_carryover(conn: sqlite3.Connection, carryover: int):
    """Update the carryover_requests count."""
    with conn:
        conn.execute(
            "UPDATE run_state SET value=? WHERE key='carryover_requests'",
            (str(carryover),),
        )