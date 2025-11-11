import sqlite3
from pathlib import Path
from datetime import date, datetime

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

def open_state_db(db_path: str, today: str) -> sqlite3.Connection:
    """Open the SQLite state DB, ensure schema and default keys."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)

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
                state[key] = datetime.strptime(value, "%Y-%m-%d").date()
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
            (str(int(carryover)),),
        )